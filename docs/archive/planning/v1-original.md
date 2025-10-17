# マルチワーカーフレームワーク開発計画

**作成日**: 2025-10-15  
**目的**: Claude Code workerを並列実行し、Coordinatorが統括するマルチワーカーアーキテクチャの実現

---

## 📊 現状の完成度：60%

### ✅ 完成している機能

#### 1. プロジェクト構造管理
- ✅ `cmw init` - プロジェクト初期化
- ✅ ディレクトリ構造自動生成
  - `shared/docs/` - 設計ドキュメント
  - `shared/coordination/` - 調整ファイル
  - `shared/artifacts/` - 成果物
- ✅ `workers-config.yaml` - ワーカー定義

#### 2. タスク生成機能
- ✅ requirements.md 解析
- ✅ セクション・機能要件の自動抽出
- ✅ タスク自動生成（19個生成成功）
- ✅ ワーカーへの自動割り当て
- ✅ 依存関係の自動設定
- ✅ `tasks.json` 出力

#### 3. Coordinator機能
- ✅ ワーカー初期化
- ✅ 依存関係グラフ構築
- ✅ ブロッカー検出
- ✅ 整合性チェック（API仕様との照合）
- ✅ 進捗管理（`progress.json`）

#### 4. CLI機能
- ✅ `cmw start` - Coordinator起動
- ✅ `cmw status` - 進捗確認
- ✅ `cmw tasks list` - タスク一覧
- ✅ `cmw tasks execute --show-prompt` - プロンプト表示

---

## ❌ 未実装の機能

### Phase 1: タスク実行エンジン（最重要）
**推定時間**: 4-6時間

#### 1.1 プロンプト生成機能 ✅ 一部完成
- ✅ PromptGenerator クラス実装済み
- ✅ タスク情報からプロンプト生成
- ✅ 関連ドキュメント自動読み込み
- ❌ プロンプト品質の検証・改善

#### 1.2 Claude API統合
**優先度**: 高  
**推定時間**: 2-3時間

**実装内容**:
```python
class ClaudeAPIClient:
    """Claude APIとの通信を管理"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"
    
    def execute_task(self, prompt: str, max_tokens: int = 4000) -> str:
        """タスクを実行してコードを生成"""
        # API呼び出し
        # レスポンス処理
        # エラーハンドリング
```

**必要なファイル**:
- `src/cmw/api_client.py` - API通信
- `src/cmw/executor.py` - タスク実行管理
- `.env` - APIキー管理

**検証方法**:
```bash
# 単純なタスクで動作確認
cmw tasks execute TASK-004 --api-key $ANTHROPIC_API_KEY
```

#### 1.3 コード生成とファイル保存
**優先度**: 高  
**推定時間**: 2時間

**実装内容**:
- 生成されたコードの解析
- 適切なディレクトリに保存
- 既存ファイルとの統合
- Git コミット自動化（オプション）

**保存先ルール**:
```
Backend worker → shared/artifacts/backend/
Frontend worker → shared/artifacts/frontend/
Database worker → shared/artifacts/backend/core/
Test worker → shared/artifacts/tests/
```

---

### Phase 2: Worker間連携（重要度：中）
**推定時間**: 3-4時間

#### 2.1 成果物の共有
- Workerが生成したファイルを他のWorkerが参照
- API定義の自動同期
- データモデルの共有

#### 2.2 依存関係の実行時解決
- 前提タスクの完了待機
- ブロック状態の自動解除
- リトライ機能

---

### Phase 3: エラーハンドリングと検証（重要度：中）
**推定時間**: 2-3時間

#### 3.1 生成コードの検証
- 構文チェック（Pythonの場合: `ast.parse()`)
- Linting（pylint, eslint）
- 型チェック（mypy, TypeScript）

#### 3.2 自動テスト実行
- Test workerの成果物を実行
- テスト結果の記録
- 失敗時のフィードバック

---

### Phase 4: ダッシュボード（重要度：低）
**推定時間**: 4-6時間

- リアルタイム進捗表示
- ワーカーステータス可視化
- ログ表示
- Web UI（FastAPI + React）

---

## 🎯 開発の優先順位

### 最優先：Phase 1.2 - Claude API統合
**理由**:
- これがないとWorkerが動かない
- 他の機能はこれが前提

**成功基準**:
```bash
# 単純なタスクで動作確認
cmw tasks execute TASK-004

# 期待される結果:
# - Claude APIにリクエスト送信
# - コードが生成される
# - ファイルに保存される
# - タスクステータスが "completed" になる
```

### 次の優先：Phase 1.3 - コード保存
**理由**:
- API統合だけでは不完全
- ファイルに保存しないと検証できない

### その後：Phase 2 - Worker間連携
**理由**:
- 複数タスクの連携実行に必要
- simple-todo完成には必須

---

## 🧪 検証計画

### 検証1: 単一タスク実行
**タスク**: TASK-004（データベース設計: ユーザー認証）

**手順**:
1. `cmw tasks execute TASK-004 --api-key $KEY`
2. `shared/artifacts/backend/core/models.py` が生成される
3. Userモデルが正しく実装されている
4. テーブル作成が動作する

### 検証2: 依存タスク実行
**タスク**: TASK-001（バックエンドAPI: ユーザー認証）

**前提**: TASK-004完了

**手順**:
1. `cmw tasks execute TASK-001`
2. TASK-004の成果物（models.py）を参照する
3. auth.py が生成される
4. APIエンドポイントが動作する

### 検証3: simple-todo完全生成
**目標**: 19個全タスクを自動実行

**手順**:
1. `cmw start --auto-execute`
2. 依存関係順にタスク実行
3. すべてのファイルが生成される
4. アプリケーションが起動・動作する

---

## 📝 次回セッションの開始手順

### 準備
```bash
# フレームワークディレクトリに移動
cd ~/workspace/cmw

# 最新の状態を確認
git status
git log --oneline -5

# 現在の進捗を確認
cd ~/workspace/projects/simple-todo
cmw status
```

### Phase 1.2の実装開始
```bash
# API統合の実装
vi src/cmw/api_client.py

# 実装後、テスト
python -m pytest tests/test_api_client.py
```

---

## 📊 マイルストーン

| Phase | 内容 | 推定時間 | 完成度 | 優先度 |
|-------|------|----------|--------|--------|
| Phase 0 | 基盤構築 | - | 100% ✅ | - |
| Phase 1.1 | プロンプト生成 | 2h | 80% 🟡 | 高 |
| Phase 1.2 | API統合 | 3h | 0% ❌ | 最高 |
| Phase 1.3 | コード保存 | 2h | 0% ❌ | 高 |
| Phase 2 | Worker連携 | 4h | 0% ❌ | 中 |
| Phase 3 | 検証機能 | 3h | 0% ❌ | 中 |
| Phase 4 | ダッシュボード | 6h | 0% ❌ | 低 |

**合計推定残り時間**: 18-22時間

---

## 🎓 学習リソース

- Anthropic API Documentation: https://docs.anthropic.com
- Claude Code Documentation: https://docs.claude.com/en/docs/claude-code
- マルチエージェントシステム: CrewAI, LangGraph, MetaGPT

---

## 📌 重要な注意事項

1. **APIコスト管理**
   - 各タスク実行でAPIコールが発生
   - 19タスク × 約4000トークン = 約$0.50-1.00
   - テスト時は少数タスクで検証

2. **エラーハンドリング**
   - API rate limit
   - ネットワークエラー
   - 生成コードの構文エラー

3. **セキュリティ**
   - APIキーを `.env` で管理
   - `.gitignore` に追加
   - 環境変数から読み込み
