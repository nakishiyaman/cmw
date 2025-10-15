"""
Command Line Interface for Claude Multi-Worker Framework
"""
import click
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

from .coordinator import Coordinator
from .templates import TemplateManager
from . import __version__


console = Console()


@click.group()
@click.version_option(version=__version__)
def main():
    """Claude Multi-Worker Framework - Document-Driven Multi-Agent Development"""
    pass


@main.command()
@click.argument('project_name')
@click.option('--template', '-t', default='web-app', 
              help='プロジェクトテンプレート')
@click.option('--path', '-p', default='.', 
              help='プロジェクト作成場所')
def init(project_name: str, template: str, path: str):
    """新規プロジェクトを初期化"""
    console.print(f"[bold blue]プロジェクト作成中: {project_name}[/bold blue]")
    
    project_path = Path(path) / project_name
    
    if project_path.exists():
        console.print(f"[bold red]エラー: {project_path} は既に存在します[/bold red]")
        sys.exit(1)
    
    # テンプレートマネージャーを使用
    template_mgr = TemplateManager()
    
    try:
        template_mgr.create_project(project_name, template, Path(path))
        console.print(f"[bold green]✓ プロジェクト作成完了: {project_path}[/bold green]")
        console.print("\n次のステップ:")
        console.print(f"  cd {project_name}")
        console.print("  cmw start")
    except Exception as e:
        console.print(f"[bold red]エラー: {e}[/bold red]")
        sys.exit(1)


@main.command()
@click.option('--path', '-p', default='.', 
              help='プロジェクトディレクトリ')
@click.option('--interval', '-i', default=300, 
              help='進捗チェック間隔（秒）')
def start(path: str, interval: int):
    """Coordinatorを起動"""
    project_path = Path(path)
    
    if not (project_path / "workers-config.yaml").exists():
        console.print("[bold red]エラー: workers-config.yaml が見つかりません[/bold red]")
        console.print("プロジェクトディレクトリで実行してください")
        sys.exit(1)
    
    console.print("[bold blue]Coordinator を起動しています...[/bold blue]")
    
    try:
        coordinator = Coordinator(project_path)
        coordinator.run(check_interval=interval)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Coordinator を停止しました[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]エラー: {e}[/bold red]")
        sys.exit(1)


@main.command()
@click.option('--path', '-p', default='.', 
              help='プロジェクトディレクトリ')
def status(path: str):
    """プロジェクトの進捗状況を表示"""
    project_path = Path(path)
    coordinator = Coordinator(project_path)
    
    progress = coordinator.check_progress()
    
    # 全体進捗
    console.print(f"\n[bold]プロジェクト: {progress.project_name}[/bold]")
    console.print(f"全体進捗: [bold green]{progress.overall_progress}[/bold green]")
    console.print(f"更新日時: {progress.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # ワーカーごとの進捗テーブル
    table = Table(title="ワーカー進捗")
    table.add_column("ワーカーID", style="cyan")
    table.add_column("状態", style="magenta")
    table.add_column("進捗", style="green")
    table.add_column("現在のタスク")
    table.add_column("完了数")
    
    for worker_id, worker_progress in progress.workers.items():
        status_emoji = {
            "idle": "⚪",
            "working": "🟢",
            "blocked": "🔴",
            "completed": "✅",
            "error": "❌"
        }.get(worker_progress.status, "❓")
        
        table.add_row(
            worker_id,
            f"{status_emoji} {worker_progress.status}",
            worker_progress.completion,
            worker_progress.current_task or "-",
            str(len(worker_progress.completed_tasks))
        )
    
    console.print(table)


@main.command()
@click.option('--path', '-p', default='.', 
              help='プロジェクトディレクトリ')
def report(path: str):
    """詳細レポートを表示"""
    project_path = Path(path)
    
    # 各ファイルを直接読み込む
    tasks_file = project_path / "shared" / "coordination" / "tasks.json"
    progress_file = project_path / "shared" / "coordination" / "progress.json"
    config_file = project_path / "workers-config.yaml"
    
    import json
    import yaml
    
    # 設定ファイル読み込み
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            project_name = config.get('project_name', 'Unknown')
    else:
        project_name = "Unknown"
    
    # 進捗ファイル読み込み
    if progress_file.exists():
        with open(progress_file, 'r', encoding='utf-8') as f:
            progress_data = json.load(f)
            overall_progress = progress_data.get('overall_progress', '0%')
    else:
        overall_progress = '0%'
    
    console.print(f"\n[bold]プロジェクト詳細レポート[/bold]\n")
    console.print(f"プロジェクト名: {project_name}")
    console.print(f"全体進捗: {overall_progress}\n")
    
    # タスク一覧
    if tasks_file.exists():
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
            tasks = tasks_data.get('tasks', [])
        
        tasks_table = Table(title="タスク一覧")
        tasks_table.add_column("タスクID")
        tasks_table.add_column("タイトル")
        tasks_table.add_column("ワーカー")
        tasks_table.add_column("状態")
        tasks_table.add_column("優先度")
        
        for task in tasks:
            tasks_table.add_row(
                task.get('task_id', ''),
                task.get('title', '')[:40],
                task.get('worker_id', ''),
                task.get('status', ''),
                task.get('priority', '')
            )
        
        console.print(tasks_table)
        console.print(f"\n合計タスク数: {len(tasks)} 件")
        
        # ステータス別集計
        status_count = {}
        for task in tasks:
            status = task.get('status', 'unknown')
            status_count[status] = status_count.get(status, 0) + 1
        
        console.print("\n[bold]ステータス別:[/bold]")
        for status, count in status_count.items():
            console.print(f"  • {status}: {count} 件")
        
        # ワーカー別集計
        worker_count = {}
        for task in tasks:
            worker = task.get('worker_id', 'unknown')
            worker_count[worker] = worker_count.get(worker, 0) + 1
        
        console.print("\n[bold]ワーカー別:[/bold]")
        for worker, count in worker_count.items():
            console.print(f"  • {worker}: {count} 件")
    else:
        console.print("[yellow]タスクファイルが見つかりません[/yellow]")


@main.group()
def workers():
    """ワーカー管理コマンド"""
    pass


@workers.command('list')
@click.option('--path', '-p', default='.', 
              help='プロジェクトディレクトリ')
def workers_list(path: str):
    """ワーカー一覧を表示"""
    project_path = Path(path)
    coordinator = Coordinator(project_path)
    
    table = Table(title="登録ワーカー")
    table.add_column("ID", style="cyan")
    table.add_column("役割")
    table.add_column("タイプ")
    table.add_column("スキル")
    table.add_column("依存")
    
    for worker_id, worker in coordinator.workers.items():
        table.add_row(
            worker_id,
            worker.role,
            worker.type,
            ", ".join(worker.skills[:3]),
            ", ".join(worker.depends_on) if worker.depends_on else "-"
        )
    
    console.print(table)


@main.group()
def tasks():
    """タスク管理コマンド"""
    pass


@tasks.command('list')
@click.option('--path', '-p', default='.', 
              help='プロジェクトディレクトリ')
@click.option('--status', '-s', 
              help='状態でフィルタ')
def tasks_list(path: str, status: str):
    """タスク一覧を表示"""
    project_path = Path(path)
    
    # tasks.jsonを直接読み込む（Coordinatorを初期化しない）
    tasks_file = project_path / "shared" / "coordination" / "tasks.json"
    
    if not tasks_file.exists():
        console.print("[yellow]タスクファイルが見つかりません。[/yellow]")
        console.print("まず 'cmw start' を実行してタスクを生成してください。")
        return
    
    # JSONファイルを読み込み
    import json
    with open(tasks_file, 'r', encoding='utf-8') as f:
        tasks_data = json.load(f)
    
    tasks_to_show = tasks_data.get('tasks', [])
    
    # ステータスでフィルタ
    if status:
        tasks_to_show = [t for t in tasks_to_show if t.get('status') == status]
    
    table = Table(title=f"タスク一覧 {f'(status={status})' if status else ''}")
    table.add_column("ID")
    table.add_column("タイトル")
    table.add_column("ワーカー")
    table.add_column("状態")
    table.add_column("優先度")
    
    for task in tasks_to_show:
        table.add_row(
            task.get('task_id', ''),
            task.get('title', '')[:50],
            task.get('worker_id', ''),
            task.get('status', ''),
            task.get('priority', '')
        )
    
    console.print(table)
    console.print(f"\n合計: {len(tasks_to_show)} 件")


@main.group()
def check():
    """整合性チェックコマンド"""
    pass


@check.command('api')
@click.option('--path', '-p', default='.', 
              help='プロジェクトディレクトリ')
def check_api(path: str):
    """API仕様の整合性をチェック"""
    project_path = Path(path)
    coordinator = Coordinator(project_path)
    
    console.print("[bold]API仕様の整合性をチェック中...[/bold]")
    results = coordinator.consistency_checker.check_api_consistency()
    
    if not results:
        console.print("[bold green]✓ 問題ありません[/bold green]")
    else:
        console.print(f"[bold red]✗ {len(results)} 件の不一致を検出[/bold red]\n")
        for issue in results:
            console.print(f"  • {issue['type']}: {issue['message']}")


@check.command('all')
@click.option('--path', '-p', default='.', 
              help='プロジェクトディレクトリ')
def check_all(path: str):
    """すべての整合性チェックを実行"""
    project_path = Path(path)
    coordinator = Coordinator(project_path)
    
    console.print("[bold]全整合性チェックを実行中...[/bold]\n")
    
    results = coordinator.check_consistency()
    
    for check_type, issues in results.items():
        if not issues:
            console.print(f"[bold green]✓ {check_type}: OK[/bold green]")
        else:
            console.print(f"[bold red]✗ {check_type}: {len(issues)} 件の問題[/bold red]")


@main.group()
def templates():
    """テンプレート管理コマンド"""
    pass


@templates.command('list')
def templates_list():
    """利用可能なテンプレート一覧"""
    template_mgr = TemplateManager()
    available = template_mgr.list_templates()
    
    table = Table(title="利用可能なテンプレート")
    table.add_column("ID", style="cyan")
    table.add_column("名前")
    table.add_column("説明")
    
    for tmpl in available:
        table.add_row(
            tmpl['id'],
            tmpl['name'],
            tmpl['description']
        )
    
    console.print(table)


if __name__ == '__main__':
    main()
