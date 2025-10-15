"""
コマンドラインインターフェース (CLI)

cmw コマンドの実装
"""
import os
import json
import click
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from .models import TaskStatus
from .api_client import ClaudeAPIClient
from .coordinator import Coordinator, PromptGenerator
from .executor import TaskExecutor


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Claude Multi-Worker Framework - マルチワーカー開発フレームワーク"""
    pass


@cli.command()
@click.option('--name', default='new-project', help='プロジェクト名')
def init(name: str):
    """新しいプロジェクトを初期化"""
    project_path = Path.cwd() / name
    
    if project_path.exists():
        click.echo(f"❌ エラー: ディレクトリ {name} は既に存在します", err=True)
        return
    
    # ディレクトリ構造を作成
    dirs = [
        "shared/docs",
        "shared/coordination",
        "shared/artifacts/backend/core",
        "shared/artifacts/frontend",
        "shared/artifacts/tests"
    ]
    
    for dir_path in dirs:
        (project_path / dir_path).mkdir(parents=True, exist_ok=True)
    
    # サンプルファイルを作成
    requirements_file = project_path / "shared" / "docs" / "requirements.md"
    requirements_file.write_text("""# プロジェクト要件書

## 概要
このプロジェクトの概要を記載してください。

## 機能要件
### 機能1: 
### 機能2: 

## 非機能要件
- パフォーマンス: 
- セキュリティ: 
""", encoding='utf-8')
    
    # .env.example を作成
    env_example = project_path / ".env.example"
    env_example.write_text("ANTHROPIC_API_KEY=your-api-key-here\n", encoding='utf-8')
    
    click.echo(f"✅ プロジェクト '{name}' を初期化しました")
    click.echo(f"\n次のステップ:")
    click.echo(f"  1. cd {name}")
    click.echo(f"  2. shared/docs/requirements.md を編集")
    click.echo(f"  3. .env ファイルを作成してAPIキーを設定")
    click.echo(f"  4. cmw tasks generate")


@cli.group()
def tasks():
    """タスク管理コマンド"""
    pass


@tasks.command('list')
@click.option('--status', type=click.Choice(['pending', 'in_progress', 'completed', 'failed', 'blocked']), 
              help='ステータスでフィルタ')
def list_tasks(status: Optional[str]):
    """タスク一覧を表示"""
    project_path = Path.cwd()
    coordinator = Coordinator(project_path)
    
    if not coordinator.tasks:
        click.echo("タスクが見つかりません。'cmw tasks generate' を実行してください。")
        return
    
    # フィルタリング
    tasks_to_show = coordinator.tasks.values()
    if status:
        tasks_to_show = [t for t in tasks_to_show if t.status.value == status]
    
    click.echo(f"\n{'='*80}")
    click.echo(f"タスク一覧 ({len(list(tasks_to_show))} 件)")
    click.echo(f"{'='*80}\n")
    
    for task in tasks_to_show:
        status_emoji = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.FAILED: "❌",
            TaskStatus.BLOCKED: "🚫"
        }
        
        emoji = status_emoji.get(task.status, "❓")
        click.echo(f"{emoji} {task.id}: {task.title}")
        click.echo(f"   ステータス: {task.status.value}")
        click.echo(f"   担当: {task.assigned_to}")
        if task.dependencies:
            click.echo(f"   依存: {', '.join(task.dependencies)}")
        click.echo()


@tasks.command('show')
@click.argument('task_id')
def show_task(task_id: str):
    """タスクの詳細を表示"""
    project_path = Path.cwd()
    coordinator = Coordinator(project_path)
    
    task = coordinator.get_task(task_id)
    if not task:
        click.echo(f"❌ タスク {task_id} が見つかりません", err=True)
        return
    
    click.echo(f"\n{'='*80}")
    click.echo(f"タスク詳細: {task.id}")
    click.echo(f"{'='*80}\n")
    
    click.echo(f"タイトル: {task.title}")
    click.echo(f"説明: {task.description}")
    click.echo(f"ステータス: {task.status.value}")
    click.echo(f"優先度: {task.priority.value}")
    click.echo(f"担当ワーカー: {task.assigned_to}")
    
    if task.dependencies:
        click.echo(f"依存タスク: {', '.join(task.dependencies)}")
    
    if task.artifacts:
        click.echo(f"\n生成されたファイル:")
        for artifact in task.artifacts:
            click.echo(f"  - {artifact}")
    
    if task.error_message:
        click.echo(f"\nエラー: {task.error_message}")


@tasks.command('execute')
@click.argument('task_id')
@click.option('--api-key', envvar='ANTHROPIC_API_KEY', help='Anthropic API key')
@click.option('--dry-run', is_flag=True, help='プロンプトを表示するだけ（実行しない）')
def execute_task(task_id: str, api_key: Optional[str], dry_run: bool):
    """タスクを実行してコードを生成
    
    例:
        cmw tasks execute TASK-001
        cmw tasks execute TASK-001 --dry-run
        cmw tasks execute TASK-001 --api-key sk-xxx
    """
    project_path = Path.cwd()
    
    # .envファイルを読み込む
    env_file = project_path / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    
    # Coordinatorを初期化
    coordinator = Coordinator(project_path)
    
    # タスクを取得
    task = coordinator.get_task(task_id)
    if not task:
        click.echo(f"❌ タスク {task_id} が見つかりません", err=True)
        return
    
    # Dry-runモード: プロンプトのみ表示
    if dry_run:
        click.echo(f"\n{'='*80}")
        click.echo(f"生成されたプロンプト (Dry-run)")
        click.echo(f"{'='*80}\n")
        
        generator = PromptGenerator(project_path)
        prompt = generator.generate_prompt(task)
        click.echo(prompt)
        return
    
    # APIキーの確認
    api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        click.echo("❌ エラー: ANTHROPIC_API_KEY が設定されていません", err=True)
        click.echo("\n以下のいずれかの方法でAPIキーを設定してください:")
        click.echo("  1. .env ファイルに記載: ANTHROPIC_API_KEY=sk-xxx")
        click.echo("  2. 環境変数を設定: export ANTHROPIC_API_KEY=sk-xxx")
        click.echo("  3. コマンドオプション: --api-key sk-xxx")
        return
    
    try:
        # API クライアントを初期化
        api_client = ClaudeAPIClient(api_key)
        
        # 実行エンジンを初期化
        executor = TaskExecutor(api_client, coordinator)
        
        # タスクを実行
        click.echo(f"\n{'='*80}")
        click.echo(f"タスク {task_id} を実行中...")
        click.echo(f"{'='*80}\n")
        
        result = executor.execute_task(task_id)
        
        # 結果を表示
        if result.success:
            click.echo(f"\n✅ タスク {task_id} の実行が完了しました!")
            click.echo(f"実行時間: {result.execution_time:.2f}秒")
            
            if result.generated_files:
                click.echo(f"\n生成されたファイル:")
                for file in result.generated_files:
                    click.echo(f"  ✓ {file}")
        else:
            click.echo(f"\n❌ タスク {task_id} の実行が失敗しました", err=True)
            click.echo(f"エラー: {result.error}")
            
    except Exception as e:
        click.echo(f"\n❌ 実行エラー: {str(e)}", err=True)


@tasks.command('execute-all')
@click.option('--api-key', envvar='ANTHROPIC_API_KEY', help='Anthropic API key')
@click.option('--continue-on-error', is_flag=True, help='エラーが発生しても続行')
def execute_all_tasks(api_key: Optional[str], continue_on_error: bool):
    """実行可能な全タスクを順次実行"""
    project_path = Path.cwd()
    
    # .envファイルを読み込む
    env_file = project_path / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    
    # APIキーの確認
    api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        click.echo("❌ エラー: ANTHROPIC_API_KEY が設定されていません", err=True)
        return
    
    try:
        # 初期化
        api_client = ClaudeAPIClient(api_key)
        coordinator = Coordinator(project_path)
        executor = TaskExecutor(api_client, coordinator)
        
        # 実行可能なタスクを取得
        executable_tasks = coordinator.get_executable_tasks()
        
        if not executable_tasks:
            click.echo("実行可能なタスクがありません")
            return
        
        click.echo(f"\n実行可能なタスク: {len(executable_tasks)} 件")
        for task in executable_tasks:
            click.echo(f"  - {task.id}: {task.title}")
        
        # 確認
        if not click.confirm("\nこれらのタスクを実行しますか?"):
            return
        
        # 実行
        results = executor.execute_multiple_tasks([t.id for t in executable_tasks])
        
        # サマリー表示
        click.echo(f"\n{'='*80}")
        click.echo("実行サマリー")
        click.echo(f"{'='*80}")
        
        success_count = sum(1 for r in results if r.success)
        failed_count = len(results) - success_count
        
        click.echo(f"成功: {success_count} / {len(results)}")
        click.echo(f"失敗: {failed_count} / {len(results)}")
        
    except Exception as e:
        click.echo(f"\n❌ 実行エラー: {str(e)}", err=True)


@cli.command()
def status():
    """プロジェクトの進捗状況を表示"""
    project_path = Path.cwd()
    coordinator = Coordinator(project_path)
    
    if not coordinator.tasks:
        click.echo("タスクが見つかりません")
        return
    
    # ステータスごとにカウント
    status_counts = {
        TaskStatus.PENDING: 0,
        TaskStatus.IN_PROGRESS: 0,
        TaskStatus.COMPLETED: 0,
        TaskStatus.FAILED: 0,
        TaskStatus.BLOCKED: 0
    }
    
    for task in coordinator.tasks.values():
        status_counts[task.status] += 1
    
    total = len(coordinator.tasks)
    completed = status_counts[TaskStatus.COMPLETED]
    progress = (completed / total * 100) if total > 0 else 0
    
    click.echo(f"\n{'='*80}")
    click.echo("プロジェクト進捗状況")
    click.echo(f"{'='*80}\n")
    
    click.echo(f"全体進捗: {completed}/{total} タスク完了 ({progress:.1f}%)")
    click.echo(f"\nステータス別:")
    click.echo(f"  ⏳ 待機中: {status_counts[TaskStatus.PENDING]}")
    click.echo(f"  🔄 実行中: {status_counts[TaskStatus.IN_PROGRESS]}")
    click.echo(f"  ✅ 完了: {status_counts[TaskStatus.COMPLETED]}")
    click.echo(f"  ❌ 失敗: {status_counts[TaskStatus.FAILED]}")
    click.echo(f"  🚫 ブロック: {status_counts[TaskStatus.BLOCKED]}")


if __name__ == '__main__':
    cli()
