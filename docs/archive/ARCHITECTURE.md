# Claude Multi-Worker Framework - プロジェクト構造

このドキュメントは、フレームワークの全体構造と各コンポーネントの役割を説明します。

## 📁 ディレクトリ構造

```
claude-multi-worker-framework/
│
├── src/cmw/                           # メインパッケージ
│   ├── __init__.py                    # パッケージ初期化、バージョン情報
│   ├── models.py                      # データモデル定義（Pydantic）
│   ├── coordinator.py                 # Coordinatorクラス（コア）
│   ├── workers.py                     # WorkerInstanceクラス
│   ├── utils.py                       # ユーティリティクラス
│   ├── cli.py                         # CLIツール（Click）
│   └── templates.py                   # プロジェクトテンプレート管理
│
├── tests/                             # テストコード
│   ├── test_coordinator.py            # Coordinatorのテスト
│   ├── test_workers.py                # Workerのテスト
│   └── test_utils.py                  # ユーティリティのテスト
│
├── docs/                              # ドキュメント（オプション）
│   ├── index.md                       # トップページ
│   ├── getting-started.md             # 入門ガイド
│   ├── architecture.md                # アーキテクチャ説明
│   └── api-reference.md               # API リファレンス
│
├── .github/                           # GitHub関連
│   ├── workflows/
│   │   ├── ci.yml                     # CI/CDパイプライン
│   │   └── publish.yml                # PyPI公開ワークフロー
│   ├── ISSUE_TEMPLATE/                # Issueテンプレート
│   └── PULL_REQUEST_TEMPLATE.md       # PRテンプレート
│
├── pyproject.toml                     # プロジェクト設定（PEP 621）
├── requirements.txt                   # 依存関係
├── setup.py                           # レガシーセットアップ（オプション）
│
├── README.md                          # プロジェクト概要
├── LICENSE                            # MITライセンス
├── CONTRIBUTING.md                    # 貢献ガイドライン
├── SETUP.md                           # セットアップガイド
├── CHANGELOG.md                       # 変更履歴
│
├── .gitignore                         # Git除外設定
├── .python-version                    # Python バージョン指定
└── .env.example                       # 環境変数のサンプル
```

## 🧩 コアコンポーネント

### 1. models.py - データモデル

Pydantic を使用したデータモデル定義。

```python
# 主要なモデル
- WorkerConfig      # ワーカー設定
- Task              # タスク定義
- WorkerProgress    # ワーカー進捗
- ProjectProgress   # プロジェクト全体の進捗
- Decision          # 意思決定ログ
- InconsistencyReport  # 整合性レポート

# Enum
- WorkerType        # ワーカータイプ
- WorkerStatus      # ワーカー状態
- TaskStatus        # タスク状態
- TaskPriority      # タスク優先度
```

### 2. coordinator.py - Coordinator

プロジェクト全体を統括するオーケストレーター。

**主要メソッド:**
```python
- __init__(project_path)              # 初期化
- load_configuration()                # 設定読み込み
- initialize_workers()                # ワーカー初期化
- decompose_requirements()            # 要件をタスクに分解
- assign_tasks(tasks)                 # タスク割り当て
- check_progress()                    # 進捗確認
- identify_blockers()                 # ブロッカー特定
- check_consistency()                 # 整合性チェック
- make_decision(...)                  # 意思決定記録
- run(check_interval)                 # メインループ
```

**責任:**
- タスク分解と割り当て
- 進捗監視
- 整合性保証
- ブロッカー解消
- 意思決定の記録

### 3. workers.py - WorkerInstance

個々のワーカーの実装。

**主要メソッド:**
```python
- assign_task(task)                   # タスク受け取り
- complete_task(task_id)              # タスク完了
- get_progress()                      # 進捗取得
- is_ready()                          # 準備完了チェック
- can_handle(task)                    # タスク処理可否
```

**状態管理:**
- idle → working → (completed | error)
- ブロッカー管理
- タスクキュー

### 4. utils.py - ユーティリティ

補助機能を提供。

**主要クラス:**
```python
- Logger                              # ロギング
- DocumentParser                      # ドキュメント解析
- ConsistencyChecker                  # 整合性チェック
- FileWatcher                         # ファイル監視
```

### 5. cli.py - CLIツール

コマンドラインインターフェース。

**主要コマンド:**
```bash
cmw init <project>                    # プロジェクト作成
cmw start                             # Coordinator起動
cmw status                            # 進捗確認
cmw report                            # 詳細レポート
cmw workers list                      # ワーカー一覧
cmw tasks list                        # タスク一覧
cmw check api                         # API整合性チェック
cmw templates list                    # テンプレート一覧
```

### 6. templates.py - テンプレート管理

プロジェクトテンプレートの作成と管理。

**テンプレート:**
- web-app: Webアプリケーション
- ml-pipeline: 機械学習パイプライン
- data-analytics: データ分析
- microservices: マイクロサービス
- api-only: APIバックエンド

## 📋 作成されるプロジェクト構造

`cmw init` で作成されるプロジェクト:

```
my-project/
├── shared/
│   ├── docs/                         # 📚 設計ドキュメント
│   │   ├── requirements.md           # 要件定義
│   │   ├── architecture.md           # アーキテクチャ
│   │   ├── api-specification.yaml    # API仕様
│   │   ├── data-models.json          # データモデル
│   │   ├── coding-standards.md       # コーディング規約
│   │   ├── security-policy.md        # セキュリティ
│   │   └── test-strategy.md          # テスト戦略
│   │
│   ├── coordination/                 # 🎯 調整ファイル
│   │   ├── tasks.json                # タスク定義
│   │   ├── progress.json             # 進捗状況
│   │   ├── decisions-log.json        # 意思決定ログ
│   │   └── blockers.json             # ブロッカー
│   │
│   ├── contracts/                    # 📋 契約（Worker間）
│   │   ├── api-spec.json             # API仕様（実行時）
│   │   └── data-models.json          # データモデル（実行時）
│   │
│   └── artifacts/                    # 🔨 成果物
│       ├── frontend/                 # フロントエンド
│       ├── backend/                  # バックエンド
│       ├── database/                 # データベース
│       ├── tests/                    # テスト
│       └── docs/                     # ドキュメント
│
├── workers-config.yaml               # ワーカー定義
└── README.md                         # プロジェクトREADME
```

## 🔄 データフロー

### 1. 初期化フロー

```
ユーザー: cmw init my-project
    ↓
TemplateManager.create_project()
    ↓
ディレクトリ構造作成
    ↓
workers-config.yaml 生成
    ↓
サンプルドキュメント作成
```

### 2. 実行フロー

```
ユーザー: cmw start
    ↓
Coordinator.__init__()
    ├─ load_configuration()
    ├─ initialize_workers()
    └─ build_dependency_graph()
    ↓
decompose_requirements()
    ├─ requirements.md 読み込み
    ├─ タスクに分解
    └─ assign_tasks()
    ↓
run() - メインループ
    ├─ check_progress()
    ├─ identify_blockers()
    ├─ check_consistency()
    └─ sleep(interval)
```

### 3. 整合性チェックフロー

```
check_consistency()
    ├─ check_api_consistency()
    │   ├─ api-specification.yaml 読み込み
    │   ├─ Frontend コード解析
    │   ├─ Backend コード解析
    │   └─ 不一致検出
    │
    ├─ check_data_model_consistency()
    │   └─ データモデルの整合性
    │
    └─ check_security_compliance()
        └─ セキュリティポリシー準拠
```

## 🔌 拡張ポイント

フレームワークは以下のポイントで拡張可能：

### 1. カスタムワーカー

```python
from cmw.workers import WorkerInstance
from cmw.models import WorkerConfig

class CustomWorker(WorkerInstance):
    def execute_task(self, task):
        # カスタムロジック
        pass
```

### 2. カスタムチェッカー

```python
from cmw.utils import ConsistencyChecker

class CustomChecker(ConsistencyChecker):
    def check_custom_compliance(self):
        # カスタムチェック
        pass
```

### 3. カスタムテンプレート

```yaml
# my-template.yaml
workers:
  - id: custom_worker
    role: "Custom Role"
    # ...
```

## 📦 依存関係

### 必須
- pyyaml: YAML設定ファイル
- click: CLIフレームワーク
- rich: ターミナルUI
- watchdog: ファイル監視
- pydantic: データバリデーション
- httpx: HTTP クライアント

### オプション
- fastapi + uvicorn: ダッシュボード
- pytest: テスト
- black, ruff, mypy: コード品質

## 🎯 設計思想

### 1. ドキュメント駆動
すべての意思決定は `/shared/docs/` のドキュメントに基づく

### 2. 疎結合
各Workerは独立して動作、Coordinatorが調整

### 3. 透明性
全ての判断をログに記録、追跡可能

### 4. 柔軟性
プロジェクトに応じてワーカー構成を変更可能

### 5. 拡張性
プラグインシステムで機能追加が容易

## 📝 設定ファイル

### workers-config.yaml

プロジェクトの中心的な設定ファイル。

```yaml
project_name: "プロジェクト名"
description: "説明"
version: "1.0"

settings:
  communication:
    shared_space: "/shared/"
    progress_update_interval: "5分"
  
  quality:
    code_review_required: true
    test_coverage_minimum: 80

workers:
  - id: worker_id
    role: "役割"
    type: implementation
    skills: [...]
    responsibilities: [...]
    depends_on: [...]
```

## 🔐 セキュリティ

- 機密情報は `.env` で管理
- APIキーはGitにコミットしない
- セキュリティポリシーを文書化
- 定期的な依存関係の更新

## 🚀 パフォーマンス

- 並列Worker実行
- 効率的なファイル監視
- キャッシング戦略
- 段階的なタスク実行

---

**次に読むべきドキュメント:**
- [README.md](README.md) - プロジェクト概要
- [SETUP.md](SETUP.md) - セットアップガイド
- [CONTRIBUTING.md](CONTRIBUTING.md) - 貢献ガイド
