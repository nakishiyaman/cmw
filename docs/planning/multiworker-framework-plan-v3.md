# マルチワーカーフレームワーク開発計画 v3.0

**作成日**: 2025-10-15  
**更新日**: 2025-10-16  
**重要な変更**: Claude API不要、アーキテクチャの根本的見直し

---

## 🔄 アーキテクチャの根本的変更

### ❌ 旧アーキテクチャ（誤り）

```
ユーザー
  ↓
cmwコマンド
  ↓
Anthropic API呼び出し ← ❌ 二重コスト
  ↓
コード生成
  ↓
ファイル保存
```

**問題点**:
- ❌ Claude CodeとcmwがそれぞれAPIを呼び出し（二重課金）
- ❌ cmwコマンドは実質的に不要なラッパー
- ❌ 無駄な中間層
- ❌ セットアップが複雑（APIキー必要）

---

### ✅ 新アーキテクチャ（正しい設計）

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

**利点**:
- ✅ **APIコストゼロ**: Claude Codeが直接実行（追加コストなし）
- ✅ **シンプル**: APIキー不要
- ✅ **明確な役割分担**: cmw=管理、Claude Code=実行
- ✅ **高速**: API往復なし

---

## 🎯 役割分担の明確化

### cmwが担当：構造的メタデータ（WHAT/WHEN/WHERE）

#### 1. タスク定義
```json
{
  "id": "TASK-001",
  "title": "ユーザー認証API実装",
  "description": "JWT認証を使用したログイン機能",
  "section": "3.1 ユーザー認証",
  "priority": "high"
}
```

#### 2. 依存関係管理
```json
{
  "dependencies": ["TASK-004"],
  "blocks": ["TASK-002", "TASK-003"],
  "parallel_group": "backend-api"
}
```

#### 3. ファイル配置ルール
```json
{
  "target_files": ["backend/auth.py"],
  "related_files": ["backend/models.py"],
  "test_files": ["tests/test_auth.py"]
}
```

#### 4. コンテキスト参照（ポインタ）
```json
{
  "requirements_section": "3.1 ユーザー認証",
  "api_spec": "api-spec.md#auth-endpoints",
  "data_model": "backend/models.py#User"
}
```

#### 5. 受け入れ基準
```json
{
  "acceptance_criteria": [
    "POST /login エンドポイント実装",
    "JWT トークン発行機能",
    "パスワードハッシュ化",
    "エラーハンドリング"
  ]
}
```

#### 6. 状態管理
```json
{
  "status": "completed",
  "started_at": "2025-10-16T10:00:00Z",
  "completed_at": "2025-10-16T10:30:00Z",
  "artifacts": ["backend/auth.py", "tests/test_auth.py"]
}
```

---

### Claude Codeが担当：実装の詳細（HOW/WHY）

#### 1. 技術スタック選択
```python
# cmw: "認証機能を実装してください"
# Claude Code: FastAPI + python-jose を選択
```

#### 2. 実装パターン
```python
# 既存コードのパターンを分析して統一
# - 命名規則
# - エラーハンドリング
# - コメントスタイル
```

#### 3. 最適化判断
```python
# bcrypt vs argon2
# 同期 vs 非同期
# キャッシュ戦略
```

#### 4. エラー対応
```python
# 実装中のエラーを検出
# 自動的に修正
# 代替アプローチを試す
```

#### 5. コード生成
```python
# Claude Code自身の能力でコーディング
# API呼び出し不要（追加コストなし）
```

---

## 📊 現状の完成度：60% → 40%（見直し後）

### ✅ 完成している機能

#### 1. プロジェクト構造管理
- ✅ `cmw init` - プロジェクト初期化
- ✅ ディレクトリ構造自動生成
- ✅ `workers-config.yaml` - ワーカー定義

#### 2. タスク生成機能
- ✅ requirements.md 解析
- ✅ タスク自動生成（19個生成成功）
- ✅ 依存関係の自動設定
- ✅ `tasks.json` 出力

#### 3. Coordinator機能（部分的）
- ✅ 依存関係グラフ構築
- ✅ ブロッカー検出
- ✅ 進捗管理（`progress.json`）
- 🔄 **TaskProvider実装が必要**

#### 4. CLI機能（一部削除予定）
- ✅ `cmw init`
- ✅ `cmw status`
- ✅ `cmw tasks list`
- ✅ `cmw tasks show`
- ❌ `cmw tasks execute` ← **削除予定**

---

### ❌ Phase 1.2の見直し（大幅変更）

#### 削除するもの
```bash
src/cmw/api_client.py      # ❌ 完全削除（API不要）
src/cmw/executor.py         # ❌ 大幅簡略化
```

#### 新規実装が必要なもの
```bash
src/cmw/task_provider.py    # ✅ Claude Codeへタスク情報提供
src/cmw/context_builder.py  # ✅ コンテキスト情報構築
src/cmw/state_manager.py    # ✅ 状態の永続化管理
```

---

## 🆕 Phase構成の見直し

### Phase 0: 基盤構築 ✅ 100%
- プロジェクト構造
- CLI基本機能
- タスク生成

### Phase 1: タスク管理層の実装
**推定時間**: 3-4時間  
**現在の進捗**: 40%

#### Phase 1.1: TaskProvider実装（2時間）⭐ 最優先
```python
# src/cmw/task_provider.py
class TaskProvider:
    """Claude Codeにタスク情報を提供"""
    
    def get_next_task(self) -> Optional[Task]:
        """依存関係を考慮して次のタスクを取得"""
    
    def get_task_context(self, task_id: str) -> dict:
        """タスク実行に必要な全情報を構築"""
        return {
            "task": task,
            "requirements": "...",
            "api_spec": "...",
            "related_files": [...],
            "acceptance_criteria": [...]
        }
    
    def mark_started(self, task_id: str):
        """タスク開始を記録"""
    
    def mark_completed(self, task_id: str, artifacts: list[str]):
        """タスク完了を記録"""
    
    def mark_failed(self, task_id: str, error: str):
        """タスク失敗を記録"""
```

#### Phase 1.2: StateManager実装（1時間）
```python
# src/cmw/state_manager.py
class StateManager:
    """状態の永続化とセッション管理"""
    
    def acquire_lock(self) -> bool:
        """ロック取得（複数セッション対応）"""
    
    def release_lock(self):
        """ロック解放"""
    
    def save_progress(self, progress: Progress):
        """進捗をprogress.jsonに保存"""
    
    def load_progress(self) -> Progress:
        """進捗を読み込み"""
```

#### Phase 1.3: ParallelExecutor実装（1-2時間）
```python
# src/cmw/parallel_executor.py
class ParallelExecutor:
    """並列実行の制御"""
    
    def get_executable_tasks(self) -> list[Task]:
        """並列実行可能なタスクを判定"""
    
    def can_run_parallel(self, task1: Task, task2: Task) -> bool:
        """ファイル競合をチェック"""
```

---

### Phase 2: Claude Code統合
**推定時間**: 3-4時間（スキル）〜 3日（MCP含む）

#### Phase 2.1: スキル統合（1-2時間）⭐ 次の優先
```markdown
# /mnt/skills/user/cmw/SKILL.md

## cmwの役割
- タスク情報の提供（メタデータ）
- 進捗管理
- 依存関係解決

## Claude Codeの役割
- コード生成（自身の機能で実行）
- ファイル操作
- テスト実行

## ワークフロー
1. タスク情報取得: `cmw.get_next_task()`
2. Claude Codeがコーディング（API不要）
3. 完了報告: `cmw.mark_completed()`
```

#### Phase 2.2: MCP統合（オプション、2-3日）
- MCPサーバー実装
- より緊密な統合

---

### Phase 3: エラーハンドリングと回復
**推定時間**: 2-3時間

#### Phase 3.1: ErrorHandler実装
```python
# src/cmw/error_handler.py
class ErrorHandler:
    """タスク失敗時の処理"""
    
    def handle_task_failure(
        self, 
        task: Task, 
        error: Exception
    ) -> TaskFailureAction:
        """失敗時の対応を決定"""
    
    def rollback_partial_work(self, task: Task):
        """部分的な成果物を削除"""
    
    def suggest_recovery(self, task: Task, error: Exception) -> str:
        """復旧方法を提案"""
```

---

### Phase 4: UX/フィードバック機能
**推定時間**: 2時間

#### Phase 4.1: FeedbackManager実装
```python
# src/cmw/feedback.py
class FeedbackManager:
    """リアルタイムフィードバック"""
    
    def report_progress(self):
        """進捗を表示"""
    
    def explain_error(self, task: Task, error: Exception):
        """エラーを分かりやすく説明"""
    
    def show_next_steps(self):
        """次のアクションを提案"""
```

---

### Phase 5: 拡張機能（オプション）
**推定時間**: 2-3時間

- Git統合（自動コミット）
- 複数プロジェクト管理
- パフォーマンス最適化

---

## 🔑 重要な考慮点（10項目）

### 1. 状態管理とセッション継続性 ⭐⭐⭐⭐⭐

**課題:**
```
Claude Codeセッション1: TASK-001完了
（再起動）
Claude Codeセッション2: 前回の進捗を引き継げるか？
```

**対策:**
- ✅ `progress.json`への永続化
- ✅ ロック機構（複数セッション対応）
- ✅ 冪等性の保証

**実装:**
```python
# 各タスク完了時に自動保存
state_manager.save_progress(current_progress)

# セッション開始時に読み込み
progress = state_manager.load_progress()
```

---

### 2. 並列実行の制御 ⭐⭐⭐⭐⭐

**課題:**
```
TASK-001 (backend/auth.py)
TASK-002 (backend/auth.py)  ← ファイル競合
```

**対策:**
- ✅ ファイルレベルの競合検出
- ✅ 並列実行可能性の判定
- ✅ 実行グループの管理

**実装:**
```python
# 並列実行可能なタスクを取得
executable = parallel_executor.get_executable_tasks()
# → ファイル競合しないタスクのみ返す
```

---

### 3. エラーハンドリングと回復 ⭐⭐⭐⭐⭐

**課題:**
```
TASK-001実行中にエラー
→ リトライ？スキップ？ユーザーに確認？
```

**対策:**
- ✅ エラーの種類に応じた対応
- ✅ 部分的な成果物のロールバック
- ✅ 依存タスクへの影響管理

**実装:**
```python
action = error_handler.handle_task_failure(task, error)
if action == TaskFailureAction.RETRY:
    # リトライ
elif action == TaskFailureAction.BLOCK:
    # 依存タスクをブロック
```

---

### 4. テスタビリティとデバッグ ⭐⭐⭐⭐

**課題:**
```
Claude Codeなしでcmwをテストできるか？
```

**対策:**
- ✅ Claude Code依存の分離
- ✅ モックとスタブの提供
- ✅ ユニットテストの充実

**実装:**
```python
# tests/mocks/claude_code_mock.py
class ClaudeCodeMock:
    """テスト用のモック"""
    def execute_task(self, task: Task) -> ExecutionResult:
        return ExecutionResult(success=True, artifacts=["mock.py"])

# tests/test_task_provider.py
def test_dependency_resolution():
    provider = TaskProvider(test_project)
    assert provider.get_next_task().id == "TASK-001"
```

---

### 5. 既存実装の移行パス ⭐⭐⭐⭐

**課題:**
```
Phase 1.2で作った api_client.py, executor.py をどうする？
```

**対策:**
- ✅ 段階的な削除
- ✅ 非推奨警告の表示
- ✅ ドキュメントの更新

**実装:**
```python
# src/cmw/cli.py
@cli.command()
def execute(task_id: str):
    """
    [非推奨] このコマンドは削除予定です。
    Claude Code統合を使用してください。
    """
    warnings.warn(
        "cmw tasks execute は非推奨です。"
        "Claude Codeから直接実行してください。",
        DeprecationWarning
    )
```

---

### 6. ユーザー体験とフィードバック ⭐⭐⭐⭐

**課題:**
```
ユーザーは今何が起きているか分かるか？
```

**対策:**
- ✅ リアルタイム進捗表示
- ✅ 分かりやすいエラーメッセージ
- ✅ 次のアクション提案

**実装:**
```python
# リアルタイムフィードバック
feedback_manager.report_progress()
# → "3/19 タスク完了 (15.8%)"
# → "次: TASK-004 データベース設計"
```

---

### 7. Git統合とバージョン管理 ⭐⭐⭐

**課題:**
```
生成されたコードをどうコミットする？
```

**対策:**
- ✅ タスク単位の自動コミット（オプション）
- ✅ 分かりやすいコミットメッセージ
- ✅ ブランチ戦略

**実装:**
```python
# オプション機能
if config.auto_commit:
    git_integration.auto_commit_task(task, artifacts)
    # → "feat: ユーザー認証API実装 (#TASK-001)"
```

---

### 8. パフォーマンスとスケーラビリティ ⭐⭐⭐

**課題:**
```
100タスク以上の大規模プロジェクトでも動作するか？
```

**対策:**
- ✅ 依存関係グラフのキャッシュ
- ✅ 遅延読み込み
- ✅ 増分更新

**実装:**
```python
# キャッシュの活用
@lru_cache(maxsize=128)
def get_task_context(task_id: str) -> dict:
    # 頻繁にアクセスされる情報をキャッシュ
```

---

### 9. セキュリティと検証 ⭐⭐⭐

**課題:**
```
生成されたコードの安全性は？
```

**対策:**
- ✅ 危険なパターンの検出
- ✅ 機密情報の漏洩チェック
- ✅ サンドボックス実行（オプション）

**実装:**
```python
# 生成コードの検証
result = security_validator.validate_generated_code(code)
if not result.is_safe:
    # 警告を表示
```

---

### 10. 複数プロジェクト管理 ⭐⭐⭐

**課題:**
```
複数プロジェクトを同時に開発できるか？
```

**対策:**
- ✅ プロジェクトの自動検出
- ✅ 設定の分離
- ✅ ワークスペース管理

**実装:**
```python
# カレントディレクトリからプロジェクトを自動検出
workspace = WorkspaceManager()
project = workspace.get_active_project()
```

---

## 🎯 実装の優先順位

### 最優先（Phase 1）: タスク管理層 - 3-4時間

1. **TaskProvider実装**（2時間）
   - タスク情報の提供
   - コンテキスト構築
   - 完了報告の受け付け

2. **StateManager実装**（1時間）
   - 永続化
   - ロック機構
   - セッション管理

3. **ParallelExecutor実装**（1-2時間）
   - 並列実行の判定
   - ファイル競合検出

---

### 次の優先（Phase 2.1）: Claude Code統合 - 1-2時間

1. **スキルファイル作成**
   - cmwの使い方
   - ワークフロー
   - ベストプラクティス

2. **動作確認**
   - Claude Codeから使用
   - エラーケースのテスト

---

### その後（Phase 3-4）: 品質向上 - 2-3時間

1. **エラーハンドリング**
2. **フィードバック機能**
3. **ユニットテスト**

---

### オプション（Phase 5）: 拡張機能 - 2-3時間

1. Git統合
2. MCP統合
3. パフォーマンス最適化

---

## 📝 次回セッションの開始手順

### Phase 1.1: TaskProvider実装

```bash
# 1. フレームワークディレクトリに移動
cd ~/workspace/claude-multi-worker-framework

# 2. 最新状態を確認
git status

# 3. TaskProviderを実装
vi src/cmw/task_provider.py

# 実装内容:
"""
Claude Codeにタスク情報を提供するクラス
- get_next_task(): 次に実行すべきタスクを返す
- get_task_context(): タスクの全コンテキストを返す
- mark_completed(): タスク完了を記録
"""

# 4. テスト
python -m pytest tests/test_task_provider.py
```

---

## 🧪 検証計画

### 検証1: TaskProvider動作確認

```python
# テストコード
provider = TaskProvider("~/workspace/projects/test-api")

# 次のタスクを取得
task = provider.get_next_task()
print(f"次のタスク: {task.id} - {task.title}")

# コンテキストを取得
context = provider.get_task_context(task.id)
print(f"要件: {context['requirements'][:100]}...")

# 完了報告
provider.mark_completed(task.id, ["backend/main.py"])
print(f"タスク {task.id} を完了としてマーク")
```

**期待される結果:**
- ✅ 依存関係を考慮したタスクが返る
- ✅ コンテキストが正しく構築される
- ✅ progress.jsonが更新される

---

### 検証2: Claude Code統合テスト

```
# Claude Codeで実行

ユーザー: 「test-apiプロジェクトの次のタスクを実行して」

Claude Code:
1. cmwからタスク取得
   task = cmw.get_next_task()
   
2. タスクコンテキスト取得
   context = cmw.get_task_context(task.id)
   
3. 自分でコーディング（API不要）
   # FastAPIのエンドポイントを実装
   
4. 完了報告
   cmw.mark_completed(task.id, ["backend/main.py"])
```

**期待される結果:**
- ✅ タスク情報を正しく取得
- ✅ コードが生成される
- ✅ ファイルが保存される
- ✅ 進捗が更新される

---

### 検証3: エンドツーエンド

**目標**: simple-todoを対話的に生成

```
ユーザー: 「ToDoアプリを作って」

Claude Code:
1. 要件をヒアリング
2. cmw init --name todo-app
3. requirements.mdを生成
4. tasks.jsonを作成（19タスク）
5. 依存関係順に実行
   - TASK-004: データベース設計
   - TASK-001: 認証API
   - ...
6. アプリケーション完成
```

**期待される結果:**
- ✅ 全タスク完了
- ✅ アプリケーションが起動
- ✅ 全機能が動作

---

## 📊 更新されたマイルストーン

| Phase | 内容 | 推定時間 | 完成度 | 優先度 |
|-------|------|----------|--------|--------|
| Phase 0 | 基盤構築 | - | 100% ✅ | - |
| **Phase 1.1** | **TaskProvider** | **2h** | **0% ⭐** | **最優先** |
| **Phase 1.2** | **StateManager** | **1h** | **0% ⭐** | **最優先** |
| **Phase 1.3** | **ParallelExecutor** | **1-2h** | **0% ⭐** | **高** |
| **Phase 2.1** | **スキル統合** | **1-2h** | **0% ⭐** | **高** |
| Phase 2.2 | MCP統合 | 3日 | 0% | 中 |
| Phase 3 | エラーハンドリング | 2-3h | 0% | 中 |
| Phase 4 | UX/フィードバック | 2h | 0% | 中 |
| Phase 5 | 拡張機能 | 2-3h | 0% | 低 |

**Phase 1完了後の推定進捗**: 40% → 60%  
**Phase 2.1完了後の推定進捗**: 60% → 75%  
**全体推定残り時間**: 12-18時間

---

## 🎓 重要な設計原則

### 原則1: 関心の分離
```
cmw        : WHAT（何を）、WHEN（いつ）、WHERE（どこに）
Claude Code: HOW（どう）、WHY（なぜ）
```

### 原則2: API不要
```
❌ cmw → Anthropic API → コード生成
✅ Claude Code → 直接コード生成（追加コストなし）
```

### 原則3: 永続化
```
全ての状態をprogress.jsonに保存
→ セッションを跨いで継続可能
```

### 原則4: 冪等性
```
同じタスクを何度実行しても安全
→ エラー回復が容易
```

### 原則5: 拡張性
```
cmwのデータ構造は他のツールでも利用可能
→ Claude Code以外のLLMでも使える
```

---

## 🎉 Phase 1完了後のビジョン

```
ユーザー: 「ToDoアプリを作って」

Claude Code:
  ↓ (cmw.get_next_task())
  次のタスク: TASK-004 データベース設計
  
  ↓ (自分でコーディング)
  models.py を作成
  
  ↓ (cmw.mark_completed())
  TASK-004完了
  
  ↓ (cmw.get_next_task())
  次のタスク: TASK-001 認証API
  
  ↓ (繰り返し)
  ...
  
  ✅ 全19タスク完了
  ✅ ToDoアプリ完成
  ✅ 所要時間: 10-15分
```

**実現すること:**
- ✅ 自然な対話でアプリ生成
- ✅ APIコストゼロ
- ✅ セットアップ不要（APIキー不要）
- ✅ 高速（API往復なし）
- ✅ 再現性（タスク定義で管理）

---

## 📚 参考資料

- Claude Code: https://docs.claude.com/en/docs/claude-code
- MCP: https://modelcontextprotocol.io/
- 旧計画書: multiworker-framework-plan-v2.md（参考用）

---

**v3.0の主な変更点:**
- ✅ Claude API呼び出しを完全削除
- ✅ cmwの役割を「タスク管理・メタデータ」に特化
- ✅ Claude Codeとの役割分担を明確化
- ✅ 10個の重要な考慮点を統合
- ✅ 実装優先順位を再定義
- ✅ より実用的で効率的なアーキテクチャ

**次のアクション: Phase 1.1 TaskProviderの実装から開始！** 🚀
