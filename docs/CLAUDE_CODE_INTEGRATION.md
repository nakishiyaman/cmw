# Claude Code統合ガイド

このドキュメントは、Claude Codeからcmwフレームワークを使用する方法を説明します。

## 🎯 概要

cmwフレームワークは、Claude Codeと統合することで、大規模なソフトウェアプロジェクトを効率的に開発できます。

### 役割分担

**cmw（タスク管理・メタデータ層）**
- requirements.mdからタスクを自動生成
- 依存関係の管理
- 進捗状態の永続化
- ファイル配置ルール
- 受け入れ基準の提供

**Claude Code（司令塔 + 実行層）**
- 自然言語理解
- コード生成（自身の機能で実行）
- ファイル操作
- テスト実行
- エラー検出と修正

## 🚀 基本的な使用方法

### 1. プロジェクトの初期化

```bash
# プロジェクトディレクトリを作成
mkdir my-project
cd my-project

# cmwプロジェクトを初期化
cmw init --name my-project

# ディレクトリ構造が作成される:
# my-project/
#   shared/
#     docs/
#       requirements.md   # 要件定義
#       api-spec.md      # API仕様
#     coordination/
#       tasks.json       # タスク定義
#       progress.json    # 進捗管理
#     artifacts/         # 生成コード
#       backend/
#       frontend/
#       tests/
```

### 2. requirements.mdを作成

`shared/docs/requirements.md`に要件を記述します：

```markdown
# プロジェクト要件

## 1. ユーザー認証
- ユーザー登録機能
- ログイン/ログアウト
- パスワードリセット

## 2. ToDoリスト管理
- ToDoの作成、更新、削除
- 完了/未完了の切り替え
- 優先度設定

## 3. API実装
- RESTful API
- JWT認証
- エラーハンドリング
```

### 3. タスクを生成

```bash
# requirements.mdからタスクを自動生成
cmw tasks generate
```

これにより、`shared/coordination/tasks.json`にタスクが生成されます。

### 4. Claude Codeから使用

Claude Codeのセッションで、以下のように使用します：

```python
from pathlib import Path
from cmw import TaskProvider

# プロジェクトパスを指定
project_path = Path("/home/user/my-project")
provider = TaskProvider(project_path)

# === 基本的なワークフロー ===

# 1. 次のタスクを取得
task = provider.get_next_task()
if not task:
    print("全タスク完了！")
else:
    print(f"次のタスク: {task.id} - {task.title}")

    # 2. タスク開始を記録
    provider.mark_started(task.id)

    # 3. タスクコンテキストを取得
    context = provider.get_task_context(task.id)

    print(f"説明: {context['task']['description']}")
    print(f"対象ファイル: {context['task']['target_files']}")
    print(f"受け入れ基準: {context['task']['acceptance_criteria']}")

    # 4. Claude Codeがコーディング（自身の能力で実行）
    # ... ここでコードを生成してファイルに書き込む ...

    # 5. 完了報告
    generated_files = ["shared/artifacts/backend/auth.py", "shared/artifacts/tests/test_auth.py"]
    provider.mark_completed(task.id, generated_files)

    print(f"タスク {task.id} 完了！")
```

## 📋 API リファレンス

### TaskProvider

#### `get_next_task() -> Optional[Task]`
次に実行すべきタスクを取得します。依存関係を考慮し、実行可能なタスクの中から優先度の高いものを返します。

```python
task = provider.get_next_task()
if task:
    print(f"ID: {task.id}")
    print(f"タイトル: {task.title}")
    print(f"説明: {task.description}")
    print(f"優先度: {task.priority}")
    print(f"依存: {task.dependencies}")
```

#### `get_task_context(task_id: str) -> Dict`
タスク実行に必要な全コンテキストを取得します。

```python
context = provider.get_task_context("TASK-001")

# context の構造:
# {
#     "task": {
#         "id": "TASK-001",
#         "title": "タスクタイトル",
#         "description": "詳細説明",
#         "target_files": ["backend/auth.py"],
#         "acceptance_criteria": ["基準1", "基準2"]
#     },
#     "requirements": "requirements.mdの内容",
#     "api_spec": "API仕様の内容",
#     "related_files": [{"path": "...", "content": "..."}],
#     "dependencies_artifacts": [{"task_id": "...", "path": "...", "content": "..."}],
#     "project_structure": {"backend_dir": "...", "frontend_dir": "..."}
# }
```

#### `mark_started(task_id: str)`
タスク開始を記録します。

```python
provider.mark_started("TASK-001")
```

#### `mark_completed(task_id: str, artifacts: List[str])`
タスク完了を記録します。

```python
provider.mark_completed("TASK-001", [
    "shared/artifacts/backend/auth.py",
    "shared/artifacts/tests/test_auth.py"
])
```

#### `mark_failed(task_id: str, error: str)`
タスク失敗を記録します。依存タスクは自動的にブロックされます。

```python
try:
    # タスク実行
    ...
except Exception as e:
    provider.mark_failed("TASK-001", str(e))
```

### StateManager

セッション管理とロック機構を提供します。

```python
from cmw import StateManager, SessionContext

# ロックを使用したセッション管理
with SessionContext(project_path) as session:
    # ロックが取得された状態で作業
    provider = TaskProvider(project_path)
    task = provider.get_next_task()
    # ...
# ロック自動解放
```

### ParallelExecutor

並列実行のサポート（将来的な拡張用）。

```python
from cmw import ParallelExecutor

executor = ParallelExecutor(project_path)

# 並列実行可能なタスクを取得
executable_tasks = executor.get_executable_tasks(max_parallel=3)

# 2つのタスクが並列実行可能か判定
can_parallel = executor.can_run_parallel(task1, task2)
```

## 🔄 典型的なワークフロー

### シナリオ1: 単一タスクの実行

```python
from pathlib import Path
from cmw import TaskProvider

project_path = Path.cwd()
provider = TaskProvider(project_path)

# 次のタスクを取得
task = provider.get_next_task()
provider.mark_started(task.id)

# コンテキスト取得
context = provider.get_task_context(task.id)

# Claude Codeがコーディング
# ... 実装 ...

# 完了報告
provider.mark_completed(task.id, ["backend/auth.py"])
```

### シナリオ2: 全タスクの実行

```python
from pathlib import Path
from cmw import TaskProvider

project_path = Path.cwd()
provider = TaskProvider(project_path)

while True:
    task = provider.get_next_task()
    if not task:
        print("全タスク完了！")
        break

    print(f"実行中: {task.id} - {task.title}")
    provider.mark_started(task.id)

    try:
        context = provider.get_task_context(task.id)

        # Claude Codeがコーディング
        # ... 実装 ...

        provider.mark_completed(task.id, ["generated_file.py"])
    except Exception as e:
        print(f"エラー: {e}")
        provider.mark_failed(task.id, str(e))
```

### シナリオ3: セッション継続性

```python
from pathlib import Path
from cmw import TaskProvider

# セッション1: 最初の実行
project_path = Path.cwd()
provider = TaskProvider(project_path)
task = provider.get_next_task()
provider.mark_completed(task.id, ["file1.py"])

# セッション2: 別のセッションで継続
# progress.jsonから進捗を自動読み込み
provider2 = TaskProvider(project_path)
task2 = provider2.get_next_task()  # 次のタスクが返される
```

## 💡 ベストプラクティス

### 1. タスク粒度
- 各タスクは1〜2時間で完了できるサイズに
- 大きすぎるタスクは分割する

### 2. 依存関係
- 明確な依存関係を設定
- 循環依存を避ける

### 3. 受け入れ基準
- 各タスクに明確な完了条件を設定
- テスト可能な基準にする

### 4. エラーハンドリング
- エラー時は必ず`mark_failed()`を呼ぶ
- エラーメッセージは詳細に記録

### 5. ファイル配置
- `shared/artifacts/`以下に成果物を配置
- バックエンド、フロントエンド、テストで分離

## 🐛 トラブルシューティング

### タスクが見つからない
```python
task = provider.get_next_task()
if not task:
    # 原因: 全タスク完了、または依存関係で全てブロック
    # 確認: shared/coordination/progress.json
```

### ロックエラー
```python
# エラー: "Could not acquire lock"
# 原因: 別のセッションがロックを保持
# 対策: 他のセッションを終了、または5分待機（自動タイムアウト）
```

### 進捗が失われる
```python
# 原因: progress.jsonが削除された
# 対策: バックアップから復元、または`cmw tasks generate`でリセット
```

## 📚 次のステップ

1. **実際のプロジェクトで試す**
   - サンプルプロジェクトを作成
   - requirements.mdを書いてタスク生成
   - Claude Codeから実行

2. **カスタマイズ**
   - tasks.jsonを手動編集して細かく調整
   - 優先度や依存関係を最適化

3. **自動化**
   - スクリプトでワークフローを自動化
   - CI/CDと統合

## 🔗 関連リンク

- [Phase 1実装ガイド](planning/phase-1-implementation-guide.md)
- [アーキテクチャ設計](planning/multiworker-framework-plan-v3.md)
- [Claude Code公式ドキュメント](https://docs.claude.com/en/docs/claude-code)
