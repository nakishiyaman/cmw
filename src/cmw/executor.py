"""
タスク実行エンジン

タスクを実行し、Claudeにコード生成を依頼し、結果をファイルに保存します。
"""
import re
import time
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime

from .models import Task, TaskStatus, ExecutionResult
from .api_client import ClaudeAPIClient
from .coordinator import Coordinator, PromptGenerator


class TaskExecutor:
    """タスク実行を管理するエンジン"""
    
    def __init__(self, api_client: ClaudeAPIClient, coordinator: Coordinator):
        """
        タスク実行エンジンを初期化
        
        Args:
            api_client: Claude APIクライアント
            coordinator: コーディネーター
        """
        self.api_client = api_client
        self.coordinator = coordinator
        self.project_path = coordinator.project_path
    
    def execute_task(self, task_id: str) -> ExecutionResult:
        """
        タスクを実行
        
        Args:
            task_id: 実行するタスクのID
            
        Returns:
            実行結果
        """
        start_time = time.time()
        
        # 1. タスクを取得
        task = self.coordinator.get_task(task_id)
        if not task:
            return ExecutionResult(
                success=False,
                task_id=task_id,
                error=f"タスク {task_id} が見つかりません"
            )
        
        # 2. タスクステータスを「実行中」に更新
        self.coordinator.update_task_status(task_id, TaskStatus.IN_PROGRESS)
        
        try:
            # 3. プロンプトを生成
            prompt_generator = PromptGenerator(self.project_path)
            prompt = prompt_generator.generate_prompt(task)
            
            # 4. Claude APIでコード生成
            print(f"🤖 Claude APIを呼び出し中...")
            generated_code = self.api_client.generate_code(prompt)
            
            # 5. 生成されたコードを解析してファイルに保存
            print(f"💾 生成されたコードを保存中...")
            saved_files = self._save_generated_code(generated_code, task)
            
            # 6. タスクステータスを「完了」に更新
            execution_time = time.time() - start_time
            self.coordinator.update_task_status(
                task_id, 
                TaskStatus.COMPLETED,
                artifacts=saved_files
            )
            
            return ExecutionResult(
                success=True,
                task_id=task_id,
                generated_files=saved_files,
                output=generated_code,
                execution_time=execution_time
            )
            
        except Exception as e:
            # エラー発生時
            execution_time = time.time() - start_time
            error_message = str(e)
            
            self.coordinator.update_task_status(
                task_id,
                TaskStatus.FAILED,
                error_message=error_message
            )
            
            return ExecutionResult(
                success=False,
                task_id=task_id,
                error=error_message,
                execution_time=execution_time
            )
    
    def _save_generated_code(self, generated_code: str, task: Task) -> List[str]:
        """
        生成されたコードを解析してファイルに保存
        
        Args:
            generated_code: Claudeが生成したコード
            task: タスク情報
            
        Returns:
            保存されたファイルのパスリスト
        """
        saved_files = []
        
        # コードブロックを抽出（```language から ``` まで）
        code_blocks = self._extract_code_blocks(generated_code)
        
        if not code_blocks:
            # コードブロックが見つからない場合、全体を保存
            print("⚠️  コードブロックが見つかりません。全体をテキストファイルとして保存します。")
            output_file = self._determine_output_path(task, "output.txt")
            self._write_file(output_file, generated_code)
            saved_files.append(str(output_file))
        else:
            # 各コードブロックを保存
            for i, (language, code, file_path) in enumerate(code_blocks):
                if file_path:
                    # コード内にファイルパスが指定されている場合
                    output_file = self.project_path / "shared" / "artifacts" / file_path
                else:
                    # ファイルパスが指定されていない場合、自動生成
                    extension = self._get_extension_for_language(language)
                    filename = f"generated_{i + 1}.{extension}"
                    output_file = self._determine_output_path(task, filename)
                
                self._write_file(output_file, code)
                saved_files.append(str(output_file.relative_to(self.project_path)))
                print(f"  ✓ {output_file.relative_to(self.project_path)}")
        
        return saved_files
    
    def _extract_code_blocks(self, text: str) -> List[Tuple[str, str, Optional[str]]]:
        """
        テキストからコードブロックを抽出
        
        Args:
            text: 解析するテキスト
            
        Returns:
            (言語, コード, ファイルパス) のタプルのリスト
        """
        # ```language から ``` までのパターン
        pattern = r'```(\w+)\s*\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        code_blocks = []
        for language, code in matches:
            # コード内からファイルパスを抽出（# File: path/to/file.py など）
            file_path_match = re.search(r'#\s*File:\s*([^\n]+)', code)
            file_path = file_path_match.group(1).strip() if file_path_match else None
            
            # コメント行を削除したコードを保存
            if file_path:
                code = re.sub(r'#\s*File:\s*[^\n]+\n', '', code, count=1)
            
            code_blocks.append((language, code.strip(), file_path))
        
        return code_blocks
    
    def _determine_output_path(self, task: Task, filename: str) -> Path:
        """
        タスク情報から出力先パスを決定
        
        Args:
            task: タスク
            filename: ファイル名
            
        Returns:
            出力先のフルパス
        """
        # ワーカーIDから配置先を決定
        worker_id = task.assigned_to.lower()
        
        if "backend" in worker_id:
            base_path = self.project_path / "shared" / "artifacts" / "backend"
            if "database" in task.title.lower() or "model" in task.title.lower():
                base_path = base_path / "core"
        elif "frontend" in worker_id:
            base_path = self.project_path / "shared" / "artifacts" / "frontend"
        elif "test" in worker_id:
            base_path = self.project_path / "shared" / "artifacts" / "tests"
        else:
            base_path = self.project_path / "shared" / "artifacts"
        
        # ディレクトリを作成
        base_path.mkdir(parents=True, exist_ok=True)
        
        return base_path / filename
    
    def _get_extension_for_language(self, language: str) -> str:
        """
        プログラミング言語から適切な拡張子を取得
        
        Args:
            language: プログラミング言語
            
        Returns:
            拡張子（例: "py", "ts", "js"）
        """
        extensions = {
            "python": "py",
            "typescript": "ts",
            "javascript": "js",
            "tsx": "tsx",
            "jsx": "jsx",
            "html": "html",
            "css": "css",
            "json": "json",
            "yaml": "yaml",
            "yml": "yml",
            "bash": "sh",
            "shell": "sh",
            "sql": "sql"
        }
        return extensions.get(language.lower(), "txt")
    
    def _write_file(self, file_path: Path, content: str):
        """
        ファイルにコンテンツを書き込む
        
        Args:
            file_path: 書き込み先のパス
            content: ファイルの内容
        """
        # ディレクトリが存在しない場合は作成
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # ファイルに書き込む
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def execute_multiple_tasks(self, task_ids: List[str]) -> List[ExecutionResult]:
        """
        複数のタスクを順次実行
        
        Args:
            task_ids: 実行するタスクIDのリスト
            
        Returns:
            各タスクの実行結果のリスト
        """
        results = []
        
        for task_id in task_ids:
            print(f"\n{'='*60}")
            print(f"タスク {task_id} を実行中...")
            print(f"{'='*60}")
            
            result = self.execute_task(task_id)
            results.append(result)
            
            if not result.success:
                print(f"❌ タスク {task_id} が失敗しました: {result.error}")
                # エラーが発生した場合、続行するか確認（オプション）
            else:
                print(f"✅ タスク {task_id} が完了しました")
        
        return results
