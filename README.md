# Claude Multi-Worker Framework

マルチワーカーアーキテクチャでソフトウェア開発を自動化するフレームワークです。

## 概要

Claude Code workerを並列実行し、Coordinatorが統括することで、大規模なソフトウェアプロジェクトを自動生成します。

## 機能

- ✅ プロジェクト初期化（`cmw init`）
- ✅ requirements.md解析
- ✅ タスク自動生成
- ✅ ワーカーへの自動割り当て
- ✅ 依存関係の自動設定
- ✅ **Claude API統合（Phase 1.2）**
- ✅ **タスク実行エンジン（Phase 1.2）**
- ✅ **コード生成とファイル保存（Phase 1.2）**
- ✅ 進捗管理
- ✅ CLI完全実装

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/nakishiyaman/claude-multi-worker-framework.git
cd claude-multi-worker-framework

# 依存パッケージをインストール
pip install -r requirements.txt --break-system-packages

# cmwコマンドをインストール
pip install -e . --break-system-packages
```

## セットアップ

### 1. APIキーの設定

Anthropic APIキーを取得して、環境変数に設定します。

```bash
# .envファイルを作成
cp .env.example .env

# .envファイルを編集してAPIキーを設定
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

### 2. プロジェクトの初期化

```bash
# 新しいプロジェクトを作成
cmw init my-project

# プロジェクトディレクトリに移動
cd my-project

# requirements.mdを編集
vi shared/docs/requirements.md
```

## 使い方

### タスクの実行

```bash
# 単一タスクを実行
cmw tasks execute TASK-001

# プロンプトのみ表示（dry-run）
cmw tasks execute TASK-001 --dry-run

# 実行可能な全タスクを実行
cmw tasks execute-all
```

### タスクの管理

```bash
# タスク一覧を表示
cmw tasks list

# 特定のステータスでフィルタ
cmw tasks list --status completed
cmw tasks list --status pending

# タスクの詳細を表示
cmw tasks show TASK-001

# プロジェクトの進捗を表示
cmw status
```

## プロジェクト構造

```
my-project/
├── shared/
│   ├── docs/              # 設計ドキュメント
│   │   ├── requirements.md
│   │   └── api-spec.md
│   ├── coordination/      # タスク定義と進捗
│   │   ├── tasks.json
│   │   └── progress.json
│   └── artifacts/         # 生成されたコード
│       ├── backend/
│       ├── frontend/
│       └── tests/
└── .env                   # APIキー（Gitにコミットしない）
```

## Phase 1.2 の実装内容

このバージョンでは、以下の機能を実装しました：

### 1. Claude API統合 (`api_client.py`)

- Anthropic APIとの通信を管理
- コード生成リクエストの送信
- エラーハンドリング

### 2. タスク実行エンジン (`executor.py`)

- プロンプト生成
- Claude APIでのコード生成
- 生成されたコードの解析
- ファイルへの保存
- タスクステータスの更新

### 3. CLI拡張 (`cli.py`)

- `cmw tasks execute` - 単一タスクの実行
- `cmw tasks execute-all` - 全タスクの実行
- `cmw tasks list` - タスク一覧
- `cmw tasks show` - タスク詳細
- `cmw status` - 進捗表示

## 例: simple-todoの生成

```bash
# 1. プロジェクト作成
cmw init simple-todo
cd simple-todo

# 2. requirements.mdを編集（省略）

# 3. タスク生成（別途実装が必要）
cmw tasks generate

# 4. APIキー設定
echo "ANTHROPIC_API_KEY=sk-xxx" > .env

# 5. タスク実行
cmw tasks execute TASK-001

# 6. 進捗確認
cmw status

# 7. 全タスク実行
cmw tasks execute-all
```

## 開発ロードマップ

### ✅ Phase 0: 基盤構築（100%）
- プロジェクト構造管理
- タスク生成機能
- Coordinator機能
- CLI基本機能

### ✅ Phase 1.2: Claude API統合（100%）
- API通信
- タスク実行エンジン
- コード生成とファイル保存

### 🔄 Phase 2: Worker間連携（0%）
- 成果物の共有
- 依存関係の実行時解決
- リトライ機能

### 🔄 Phase 3: エラーハンドリングと検証（0%）
- 生成コードの検証
- 自動テスト実行
- フィードバックループ

### 🔄 Phase 4: ダッシュボード（0%）
- リアルタイム進捗表示
- Web UI

## コスト管理

- 各タスク実行で約4000トークン使用
- 19タスク × 約4000トークン ≈ $0.50-1.00
- テスト時は少数のタスクで検証推奨

## ライセンス

MIT License

## 開発者

- GitHub: https://github.com/nakishiyaman/claude-multi-worker-framework

## 貢献

バグ報告や機能リクエストは、GitHubのIssuesでお願いします。
