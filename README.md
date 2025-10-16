# Claude Multi-Worker Framework (cmw)

Claude Codeと統合してソフトウェア開発を効率化するタスク管理フレームワークです。

requirements.mdから自動的にタスクを生成し、依存関係を管理しながら、Claude Codeによる実装を支援します。

## 🎯 概要

cmwは**タスク管理・メタデータ層**として機能し、Claude Codeと協調して大規模プロジェクトの開発を支援します。

### アーキテクチャ

```
ユーザー「ToDoアプリを作って」
  ↓
┌─────────────────────────────────────────┐
│ Claude Code（司令塔 + 実行層）          │
│  - 自然言語理解                          │
│  - コード生成（自身の機能）              │
│  - ファイル操作                          │
│  - テスト実行                            │
└─────────────────────────────────────────┘
  ↓ ↑ タスク情報の取得・完了報告
┌─────────────────────────────────────────┐
│ cmw（タスク管理・メタデータ層）         │
│  - requirements.md → タスク分解         │
│  - 依存関係グラフ管理                   │
│  - 進捗状態の永続化                     │
│  - ファイル配置ルール                   │
│  - 受け入れ基準                         │
└─────────────────────────────────────────┘
```

### 役割分担

**cmwが担当（WHAT/WHEN/WHERE）:**
- タスク定義と自動生成
- 依存関係管理
- 進捗状態の永続化
- ファイル配置ルール
- 受け入れ基準の提供

**Claude Codeが担当（HOW/WHY）:**
- 技術スタック選択
- 実装パターン決定
- コード生成（自身の機能で実行、API追加コストなし）
- エラー検出と修正

## ✨ 主な機能

### ✅ 実装済み（Phase 0 + Phase 1 + Phase 3.1）

#### タスク管理層（Phase 1）
- **TaskProvider**: タスク情報の提供、コンテキスト構築、状態管理
- **StateManager**: ロック機構、セッション管理、進捗永続化
- **ParallelExecutor**: 並列実行判定、ファイル競合検出

#### エラーハンドリング（Phase 3.1）
- **ErrorHandler**: エラー対応決定、ロールバック、復旧提案
  - リトライ可能なエラーの自動判定
  - 部分的な成果物の自動削除
  - エラー別の復旧方法提案
  - 影響を受けるタスクの分析

#### 基盤機能（Phase 0）
- ✅ プロジェクト初期化（`cmw init`）
- ✅ requirements.md解析
- ✅ タスク自動生成
- ✅ 依存関係の自動設定
- ✅ 進捗管理
- ✅ CLI実装

### ✅ Phase 2.1完了
- Claude Code統合ガイド作成完了

### ✅ Phase 3.1完了
- ErrorHandler実装完了（エラーハンドリングと回復機能）

### 🔄 開発中（Phase 4+）
- Phase 4: UX/フィードバック機能
- Phase 5: Git統合（オプション）
- Phase 2.2: MCP統合（オプション）

## 📦 インストール

```bash
# リポジトリをクローン
git clone https://github.com/nakishiyaman/claude-multi-worker-framework.git
cd claude-multi-worker-framework

# 仮想環境を作成（推奨）
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows

# 依存パッケージをインストール
pip install -r requirements.txt

# cmwコマンドをインストール
pip install -e .
```

## 🚀 クイックスタート

### 1. プロジェクト初期化

```bash
# 新しいプロジェクトを作成
cmw init my-project
cd my-project
```

### 2. requirements.mdを編集

`shared/docs/requirements.md`に要件を記述：

```markdown
# プロジェクト要件

## 1. ユーザー認証
- ユーザー登録機能
- ログイン/ログアウト
- パスワードリセット

## 2. ToDoリスト管理
- ToDoの作成、更新、削除
- 完了/未完了の切り替え
```

### 3. タスク生成

```bash
# requirements.mdからタスクを自動生成
cmw tasks generate
```

### 4. Claude Codeから使用

Claude Codeのセッションで：

```python
from pathlib import Path
from cmw import TaskProvider

# プロジェクトパスを指定
project_path = Path.cwd()
provider = TaskProvider(project_path)

# 次のタスクを取得
task = provider.get_next_task()
print(f"次のタスク: {task.id} - {task.title}")

# タスク開始を記録
provider.mark_started(task.id)

# タスクコンテキストを取得
context = provider.get_task_context(task.id)
print(f"対象ファイル: {context['task']['target_files']}")
print(f"受け入れ基準: {context['task']['acceptance_criteria']}")

# Claude Codeがコーディング（自身の機能で実行）
# ... コード生成 ...

# 完了報告
provider.mark_completed(task.id, ["shared/artifacts/backend/auth.py"])
```

詳細は[Claude Code統合ガイド](docs/CLAUDE_CODE_INTEGRATION.md)を参照してください。

## 📂 プロジェクト構造

```
my-project/
├── shared/
│   ├── docs/                 # 設計ドキュメント
│   │   ├── requirements.md   # 要件定義
│   │   └── api-spec.md       # API仕様
│   ├── coordination/         # タスク定義と進捗
│   │   ├── tasks.json        # タスク定義
│   │   ├── progress.json     # 進捗管理
│   │   └── .lock             # セッションロック
│   └── artifacts/            # 生成されたコード
│       ├── backend/
│       ├── frontend/
│       └── tests/
```

## 🎮 CLIコマンド

### プロジェクト管理

```bash
# プロジェクト初期化
cmw init <project-name>

# プロジェクト状態表示
cmw status
```

### タスク管理

```bash
# タスク生成
cmw tasks generate

# タスク一覧
cmw tasks list
cmw tasks list --status pending
cmw tasks list --status completed

# タスク詳細
cmw tasks show TASK-001
```

## 📖 ドキュメント

- **[Claude Code統合ガイド](docs/CLAUDE_CODE_INTEGRATION.md)** - Claude Codeからの使用方法
- **[Phase 1実装ガイド](docs/planning/phase-1-implementation-guide.md)** - タスク管理層の実装詳細
- **[アーキテクチャ設計v3.0](docs/planning/multiworker-framework-plan-v3.md)** - 全体設計と計画

## 🧪 テスト

```bash
# 全テストを実行
python -m pytest tests/ -v --ignore=tests/test_coordinator.py

# 特定のテストを実行
python -m pytest tests/test_task_provider.py -v
python -m pytest tests/test_state_manager.py -v
python -m pytest tests/test_parallel_executor.py -v
python -m pytest tests/test_error_handler.py -v
```

現在42個のテストが全てパスしています。

## 📊 開発ロードマップ

### ✅ Phase 0: 基盤構築（100%）
- プロジェクト構造管理
- タスク生成機能
- Coordinator機能
- CLI基本機能

### ✅ Phase 1: タスク管理層（100%）
- **Phase 1.1**: TaskProvider実装
- **Phase 1.2**: StateManager実装
- **Phase 1.3**: ParallelExecutor実装

### ✅ Phase 2: Claude Code統合（65%）
- **Phase 2.1**: ドキュメント作成（完了）
- Phase 2.2: MCP統合（オプション）

### ✅ Phase 3: エラーハンドリング（100%）
- **Phase 3.1**: ErrorHandler実装（完了）

### 🔄 Phase 4: UX/フィードバック（0%）
### 🔄 Phase 5: 拡張機能（0%）

**全体進捗**: 約75%

## 💡 主な特徴

### 1. APIコストゼロ
Claude Codeが直接コードを生成するため、追加のAPI呼び出しコストはかかりません。

### 2. セッション継続性
`progress.json`に状態を永続化するため、セッションを跨いで開発を継続できます。

### 3. 並列実行サポート
ファイル競合を検出し、安全に並列実行可能なタスクを判定します。

### 4. 依存関係管理
タスク間の依存関係を自動的に管理し、正しい順序で実行します。

## 🔧 技術スタック

- **Python 3.12+**
- **Typer**: CLIフレームワーク
- **pytest**: テストフレームワーク
- **Pydantic**: データバリデーション（モデル定義）

## 📝 ライセンス

MIT License

## 👥 開発者

- GitHub: https://github.com/nakishiyaman/claude-multi-worker-framework

## 🤝 貢献

バグ報告や機能リクエストは、GitHubのIssuesでお願いします。

## 🔗 関連リンク

- [Claude Code公式ドキュメント](https://docs.claude.com/en/docs/claude-code)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
