# Claude Multi-Worker Framework

**Document-Driven Multi-Agent Development Orchestration Framework**

複数のClaude Codeワーカーを並列実行し、Coordinatorが統括する開発フレームワーク。ドキュメント駆動で整合性を保ちながら、大規模プロジェクトを効率的に開発します。

## 📦 重要：フレームワークとプロジェクトの関係

**このリポジトリ = ツール本体**
- `claude-multi-worker-framework/` は **再利用可能なツール** です
- 一度インストールすれば、システム全体で `cmw` コマンドが使えます
- 複数のプロジェクトで使い回せます

**プロジェクト = 実際の開発**
- `cmw init` で作成するのは **別の場所に配置する開発プロジェクト** です
- フレームワークのディレクトリ内には作りません
- 各プロジェクトは独立したGitリポジトリで管理できます

```
あなたのPC/
├── claude-multi-worker-framework/  ← このリポジトリ（ツール）
│   └── pip install -e . で1回インストール
│
└── my-projects/                     ← プロジェクト置き場（別の場所）
    ├── ecommerce-site/              ← cmw init で作成
    ├── ml-pipeline/                 ← cmw init で作成
    └── another-project/             ← cmw init で作成
```

詳細は [DIRECTORY_LAYOUT.md](DIRECTORY_LAYOUT.md) を参照してください。

## 🌟 特徴

- 📚 **ドキュメント駆動**: `/shared/docs/` を起点とした開発
- 🤖 **マルチワーカー**: 並列開発で生産性向上
- 🎯 **自動オーケストレーション**: Coordinatorが自律的に管理
- 🔄 **動的構成**: プロジェクトに応じたワーカー定義
- ✅ **整合性保証**: API仕様、データモデルの自動チェック
- 📊 **進捗可視化**: リアルタイムで状況把握

## 🚀 クイックスタート

### ステップ1: フレームワークをインストール（1回だけ）

```bash
# 1. このリポジトリをクローンまたはダウンロード
cd /path/to/claude-multi-worker-framework

# 2. 開発モードでインストール
pip install -e .

# 3. 確認
cmw --version
# → "cmw, version 0.1.0" と表示されればOK
```

これで、システム全体で `cmw` コマンドが使えるようになります。

### ステップ2: プロジェクトを作成（プロジェクトごと）

**重要: フレームワークのディレクトリの外で実行してください**

```bash
# 1. プロジェクトを作りたい場所に移動（任意の場所）
cd ~/my-projects  # または好きなディレクトリ

# 2. 新しいプロジェクトを作成
cmw init my-ecommerce-project --template web-app

# 3. プロジェクトディレクトリに移動
cd my-ecommerce-project

# 4. 構造を確認
ls -la
# → shared/ workers-config.yaml README.md が作成されている
```

これで以下の構造が作成されます：

```
my-ecommerce-project/
├── shared/
│   ├── docs/              # 設計ドキュメント
│   ├── coordination/      # タスク・進捗管理
│   └── artifacts/         # 成果物
├── workers-config.yaml    # ワーカー定義
└── coordinator.py         # Coordinator実行スクリプト
```

### ワーカー構成の定義

`workers-config.yaml` を編集：

```yaml
project_name: "My E-Commerce Project"

workers:
  - id: frontend
    role: "フロントエンド開発"
    skills: ["React", "TypeScript"]
    
  - id: backend
    role: "バックエンド開発"
    skills: ["Python", "FastAPI"]
    depends_on: [database]
    
  - id: database
    role: "データベース設計"
    skills: ["PostgreSQL"]
```

### Coordinator起動

```bash
# Coordinatorを起動
python coordinator.py

# または
cmw start
```

## 📖 基本的な使い方

### 1. 要件定義を書く

`shared/docs/requirements.md` に要件を記述：

```markdown
# 要件定義

## ユーザー認証
- メールアドレスとパスワードでログイン
- JWTトークン発行（有効期限24時間）
```

### 2. API仕様を定義

`shared/docs/api-specification.yaml` にAPI仕様を記述：

```yaml
openapi: 3.0.0
paths:
  /auth/login:
    post:
      summary: ユーザーログイン
      requestBody:
        content:
          application/json:
            schema:
              properties:
                email: { type: string }
                password: { type: string }
```

### 3. Coordinatorに任せる

Coordinatorが自動的に：
1. 要件を分析
2. タスクを分解
3. 適切なワーカーに割り当て
4. 進捗を監視
5. 整合性をチェック

### 4. 進捗確認

```bash
# 進捗を確認
cmw status

# 詳細なレポート
cmw report

# リアルタイムダッシュボード
cmw dashboard
```

## 🏗️ アーキテクチャ

```
┌─────────────────────────────────┐
│     Coordinator Worker          │
│  (プロジェクト統括)              │
└────────┬────────────────────────┘
         │
    ┌────┴────┬────────┬──────┐
    ↓         ↓        ↓      ↓
┌────────┐ ┌────────┐ ┌────┐ ┌────┐
│Frontend│ │Backend │ │DB  │ │Test│
│Worker  │ │Worker  │ │Wrkr│ │Wrkr│
└────┬───┘ └───┬────┘ └──┬─┘ └──┬─┘
     │         │          │      │
     └─────────┴──────────┴──────┘
              ↓
      /shared/ (共有領域)
```

## 📋 プロジェクトテンプレート

利用可能なテンプレート：

- `web-app`: フルスタックWebアプリケーション
- `ml-pipeline`: 機械学習パイプライン
- `data-analytics`: データ分析プロジェクト
- `microservices`: マイクロサービス構成
- `api-only`: APIバックエンドのみ

```bash
# テンプレート一覧
cmw templates list

# テンプレートから作成
cmw init my-project --template ml-pipeline
```

## 🛠️ コマンドラインツール

### プロジェクト管理

```bash
cmw init <project-name>              # 新規プロジェクト作成
cmw start                            # Coordinator起動
cmw stop                             # Coordinator停止
cmw restart                          # Coordinator再起動
```

### ワーカー管理

```bash
cmw workers list                     # ワーカー一覧
cmw workers add <worker-id>          # ワーカー追加
cmw workers remove <worker-id>       # ワーカー削除
cmw workers status <worker-id>       # ワーカー状態確認
```

### タスク管理

```bash
cmw tasks list                       # タスク一覧
cmw tasks assign <task-id> <worker>  # タスク割り当て
cmw tasks status <task-id>           # タスク状態確認
```

### 進捗とレポート

```bash
cmw status                           # 全体進捗
cmw report                           # 詳細レポート
cmw dashboard                        # リアルタイムダッシュボード
cmw logs                             # ログ表示
```

### 整合性チェック

```bash
cmw check api                        # API仕様の整合性
cmw check data-models                # データモデルの整合性
cmw check security                   # セキュリティポリシー準拠
cmw check all                        # 全チェック
```

## 📚 ドキュメント構造

```
shared/docs/
├── requirements.md           # 要件定義
├── architecture.md          # アーキテクチャ
├── api-specification.yaml   # API仕様
├── data-models.json         # データモデル
├── coding-standards.md      # コーディング規約
├── security-policy.md       # セキュリティポリシー
├── test-strategy.md         # テスト戦略
└── workers-config.yaml      # ワーカー構成
```

各ドキュメントのテンプレートは `/templates/docs/` にあります。

## 🔧 カスタマイズ

### カスタムワーカーの追加

```python
# custom_worker.py

from cmw.workers import BaseWorker

class CustomAnalyticsWorker(BaseWorker):
    def __init__(self):
        super().__init__(
            id="analytics",
            role="データ分析",
            skills=["Python", "pandas", "Plotly"]
        )
    
    def execute_task(self, task):
        # タスク実行ロジック
        pass
```

### カスタムCoordinatorロジック

```python
# coordinator_extensions.py

from cmw.coordinator import Coordinator

class CustomCoordinator(Coordinator):
    def custom_consistency_check(self):
        # カスタム整合性チェック
        pass
```

## 📊 進捗ダッシュボード

リアルタイムダッシュボードの起動：

```bash
cmw dashboard --port 8080
```

ブラウザで `http://localhost:8080` を開くと：

- 各ワーカーの進捗状況
- タスク完了率
- ブロッカー情報
- 整合性チェック結果
- タイムライン

## 🧪 テスト

```bash
# ユニットテスト
pytest tests/

# 統合テスト
pytest tests/integration/

# E2Eテスト（サンプルプロジェクトで）
cmw test
```

## 🤝 コントリビューション

コントリビューション歓迎です！

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照

## 🙏 謝辞

- [Anthropic](https://www.anthropic.com/) - Claude API
- マルチエージェントシステム研究コミュニティ

## 📮 サポート

- Issue: [GitHub Issues](https://github.com/yourusername/claude-multi-worker-framework/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/claude-multi-worker-framework/discussions)
- Email: your.email@example.com

## 🗺️ ロードマップ

- [ ] v0.1.0: 基本機能実装
- [ ] v0.2.0: ダッシュボードUI
- [ ] v0.3.0: MCP統合
- [ ] v0.4.0: プラグインシステム
- [ ] v1.0.0: 安定版リリース

---

**Happy Multi-Worker Development! 🚀**
