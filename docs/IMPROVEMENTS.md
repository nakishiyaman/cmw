# cmwフレームワーク改善計画

**作成日**: 2025-10-16
**検証プロジェクト**: todo-api (17タスク、2000行コード、106テスト)

## 📋 検証結果サマリー

### ✅ 検証の成功指標

| 項目 | 結果 | 詳細 |
|------|------|------|
| タスク完了率 | 17/17 (100%) | 全タスクが正常に完了 |
| テスト成功率 | 106/106 (100%) | 全テストがパス |
| コード行数 | 約2000行 | バックエンド + テストコード |
| 実装時間 | 約2時間 | 手動タスク定義20分含む |
| ファイル競合 | 2件検出 | auth.py, tasks.py |
| API動作確認 | 9/9エンドポイント | 全機能が正常動作 |

### 🎯 フレームワークの有効性

**うまく機能した機能:**
1. **TaskProvider** - 依存関係の正確な解決
2. **StateManager** - ロック機構によるファイル整合性保証
3. **ParallelExecutor** - 並列実行可能タスクの判定
4. **ErrorHandler** - エラー種別の自動判定と対応決定
5. **FeedbackManager** - 分かりやすいエラー説明と次ステップ提案

## 🔍 発見された課題

### 課題1: タスク定義の手動作成

**問題点:**
- `requirements.md`から`tasks.json`への変換が完全手動
- 17タスクの定義に約20分かかった
- 依存関係の推論も手作業
- エラーの可能性が高い

**影響度**: 🔴 高 - 導入障壁が非常に高い

**実例 (todo-api検証時):**
```markdown
# requirements.md
## 2. 認証機能
### 2.1 ユーザー登録
- エンドポイント: POST /auth/register
- リクエストボディ: email, password
- バリデーション: メールアドレス形式、パスワード強度、重複チェック
```

↓ 手動で変換 ↓

```json
{
  "id": "TASK-004",
  "title": "ユーザー登録エンドポイント実装",
  "description": "POST /auth/register エンドポイントを実装する",
  "dependencies": ["TASK-001", "TASK-002", "TASK-003"],
  "target_files": ["backend/routers/auth.py"],
  "acceptance_criteria": [
    "メールアドレスバリデーション",
    "パスワード強度チェック",
    "重複ユーザーチェック"
  ]
}
```

**現状の問題:**
- 手動でID採番（TASK-001, TASK-002...）
- 依存関係を人間が推測
- ファイルパスを手動で決定
- 受け入れ基準を手動抽出

### 課題2: ファイルベースの依存関係推論

**問題点:**
- 同じファイルを編集するタスクの順序が不明確
- ファイル競合を事前に検出できない
- 依存関係の記述漏れが発生しやすい

**影響度**: 🟡 中 - 並列実行時の安全性に影響

**実例 (todo-api検証時):**
```
TASK-004: routers/auth.py にユーザー登録を実装
TASK-005: routers/auth.py にログインを実装
→ 両方が同じファイルを編集するが、依存関係が不明瞭
```

**理想的な動作:**
```python
# 自動検出してほしい依存関係
TASK-004 → TASK-005  # 同一ファイル編集のため順序付け
TASK-007, TASK-008   # 異なるファイルなので並列実行可能
```

### 課題3: リアルタイム進捗の可視性不足

**問題点:**
- `progress.json`は更新されているが見にくい
- 「今何%完了か」がすぐに分からない
- 残り時間の見積もりがない
- エラー発生時の影響範囲が不明

**影響度**: 🟡 中 - UX/開発体験に影響

**現状の表示:**
```json
{
  "updated_at": "2025-10-16T11:54:27.905683",
  "tasks": {
    "TASK-001": {"status": "completed", ...},
    "TASK-002": {"status": "completed", ...},
    ...
  }
}
```

**理想的な表示:**
```
┌─────────────────────────────────────────┐
│ Todo API プロジェクト進捗               │
├─────────────────────────────────────────┤
│ 進捗: ████████████░░░░ 70% (12/17)     │
│ 完了: 12タスク                          │
│ 進行中: 1タスク (TASK-013)              │
│ 保留: 4タスク                           │
│ 失敗: 0タスク                           │
│ 推定残り時間: 約45分                    │
└─────────────────────────────────────────┘

次のタスク: TASK-014 (認証テストの作成)
依存: TASK-004, TASK-005 (完了済み)
```

### 課題4: エラーハンドリングの分類精度

**問題点:**
- エラータイプの分類がまだ粗い
- リトライすべきエラーの判定基準が不明確
- 自動修復できるエラーの検出が不十分

**影響度**: 🟢 低 - 基本機能は動作している

**実例 (todo-api検証時):**
```python
# bcrypt互換性エラー
ValueError: password cannot be longer than 72 bytes

現状: TaskFailureAction.ROLLBACK (正しい)
→ 問題ないが、より詳細な分類があればベター

# datetime deprecation警告
DeprecationWarning: datetime.datetime.utcnow() is deprecated

現状: TaskFailureAction.RETRY (不要)
→ 警告は無視すべきだが、リトライしようとした
```

**改善案:**
```python
class ErrorSeverity(Enum):
    WARNING = "warning"      # 無視可能
    RETRYABLE = "retryable"  # リトライで解決可能
    FIXABLE = "fixable"      # コード修正で解決可能
    BLOCKING = "blocking"    # 手動介入が必要

class ErrorCategory(Enum):
    DEPENDENCY = "dependency"      # 依存パッケージエラー
    SYNTAX = "syntax"              # 構文エラー
    TYPE = "type"                  # 型エラー
    RUNTIME = "runtime"            # 実行時エラー
    COMPATIBILITY = "compatibility" # 互換性エラー
    DEPRECATION = "deprecation"    # 非推奨警告
```

## 🚀 改善ロードマップ

### Phase 5: 自動タスク生成機能 (優先度: 🔴 最高)

**目標**: requirements.mdからタスクを完全自動生成

**実装内容:**

#### 5.1 RequirementsParser (2-3時間)

```python
# src/cmw/requirements_parser.py

from typing import List, Dict, Optional
from pathlib import Path
import re
from .models import Task

class RequirementsParser:
    """requirements.mdを解析してタスクを自動生成"""

    def parse(self, requirements_path: Path) -> List[Task]:
        """
        Markdownファイルを解析してタスクリストを生成

        Args:
            requirements_path: requirements.mdのパス

        Returns:
            生成されたタスクのリスト
        """
        content = requirements_path.read_text(encoding='utf-8')
        sections = self._extract_sections(content)
        tasks = []

        for section in sections:
            task = self._section_to_task(section)
            tasks.append(task)

        # 依存関係を推論
        tasks = self._infer_dependencies(tasks)

        return tasks

    def _extract_sections(self, content: str) -> List[Dict]:
        """
        Markdownからセクションを抽出

        戦略:
        - ## レベルの見出しをメインタスクとして認識
        - ### レベルの見出しをサブタスクとして認識
        - リストアイテムを受け入れ基準として抽出
        - コードブロックを技術仕様として抽出
        """
        sections = []
        current_section = None

        for line in content.split('\n'):
            # H2見出し = 新しいメインタスク
            if line.startswith('## '):
                if current_section:
                    sections.append(current_section)
                current_section = {
                    'level': 2,
                    'title': line[3:].strip(),
                    'subsections': [],
                    'criteria': [],
                    'technical_notes': []
                }

            # H3見出し = サブタスク
            elif line.startswith('### ') and current_section:
                subsection = {
                    'level': 3,
                    'title': line[4:].strip(),
                    'criteria': []
                }
                current_section['subsections'].append(subsection)

            # リスト項目 = 受け入れ基準
            elif line.strip().startswith('-') and current_section:
                criterion = line.strip()[1:].strip()
                if current_section['subsections']:
                    current_section['subsections'][-1]['criteria'].append(criterion)
                else:
                    current_section['criteria'].append(criterion)

        if current_section:
            sections.append(current_section)

        return sections

    def _section_to_task(self, section: Dict) -> Task:
        """セクションをTaskオブジェクトに変換"""
        # タイトルからタスクIDを生成
        task_id = self._generate_task_id(section['title'])

        # target_filesを推論
        target_files = self._infer_target_files(section)

        # 優先度を推論
        priority = self._infer_priority(section)

        return Task(
            id=task_id,
            title=section['title'],
            description=self._generate_description(section),
            target_files=target_files,
            acceptance_criteria=section['criteria'],
            priority=priority,
            dependencies=[]  # 後で推論
        )

    def _infer_target_files(self, section: Dict) -> List[str]:
        """
        セクション内容からtarget_filesを推論

        戦略:
        1. エンドポイント記述から対応するルーターファイルを推論
           例: "POST /auth/register" → "backend/routers/auth.py"

        2. モデル定義からモデルファイルを推論
           例: "Userモデル" → "backend/models.py"

        3. データベース記述からdatabase.pyを推論

        4. テスト記述からテストファイルを推論
           例: "ユーザー登録のテスト" → "tests/test_auth.py"
        """
        files = []
        content = section['title'] + ' ' + ' '.join(section['criteria'])

        # エンドポイント検出
        if re.search(r'POST|GET|PUT|DELETE|PATCH', content):
            endpoint_match = re.search(r'/([\w-]+)', content)
            if endpoint_match:
                resource = endpoint_match.group(1)
                files.append(f"backend/routers/{resource}.py")

        # モデル検出
        if 'モデル' in content or 'Model' in content:
            files.append("backend/models.py")

        # データベース検出
        if 'データベース' in content or 'DB' in content or 'SQLAlchemy' in content:
            files.append("backend/database.py")

        # スキーマ検出
        if 'スキーマ' in content or 'Schema' in content or 'Pydantic' in content:
            files.append("backend/schemas.py")

        # テスト検出
        if 'テスト' in content or 'test' in content.lower():
            files.append("tests/test_integration.py")

        return list(set(files))  # 重複削除

    def _infer_dependencies(self, tasks: List[Task]) -> List[Task]:
        """
        タスク間の依存関係を推論

        戦略:
        1. ファイルベース依存: 同じファイルを編集するタスクは順序付け
        2. レイヤー依存: models → schemas → routers の順序
        3. 機能依存: 認証 → 認証が必要な機能
        """
        # ファイルごとのタスクをグルーピング
        file_to_tasks = {}
        for task in tasks:
            for file in task.target_files:
                if file not in file_to_tasks:
                    file_to_tasks[file] = []
                file_to_tasks[file].append(task)

        # レイヤー定義
        layer_order = {
            'database.py': 1,
            'models.py': 2,
            'schemas.py': 3,
            'auth.py': 4,
            'dependencies.py': 5,
            'routers': 6,
            'main.py': 7,
            'tests': 8,
            'requirements.txt': 0,
            'README.md': 9
        }

        for task in tasks:
            # レイヤーベース依存
            task_layer = self._get_task_layer(task, layer_order)

            for other_task in tasks:
                if task.id == other_task.id:
                    continue

                other_layer = self._get_task_layer(other_task, layer_order)

                # 下位レイヤーが依存元
                if other_layer < task_layer:
                    # ファイルが関連している場合のみ依存追加
                    if self._has_file_relation(task, other_task):
                        if other_task.id not in task.dependencies:
                            task.dependencies.append(other_task.id)

        return tasks

    def _get_task_layer(self, task: Task, layer_order: Dict) -> int:
        """タスクのレイヤーを取得"""
        max_layer = 0
        for file in task.target_files:
            for pattern, layer in layer_order.items():
                if pattern in file:
                    max_layer = max(max_layer, layer)
        return max_layer

    def _has_file_relation(self, task1: Task, task2: Task) -> bool:
        """2つのタスクのファイルが関連しているか判定"""
        # 同じファイルを編集
        if set(task1.target_files) & set(task2.target_files):
            return True

        # 同じディレクトリ内
        dirs1 = {Path(f).parent for f in task1.target_files}
        dirs2 = {Path(f).parent for f in task2.target_files}
        if dirs1 & dirs2:
            return True

        return False
```

#### 5.2 CLIコマンド追加

```bash
# requirements.mdからタスクを自動生成
cmw tasks generate

# 生成されたタスクをプレビュー
cmw tasks preview

# タスク定義を手動編集後、検証
cmw tasks validate
```

#### 5.3 テスト (tests/test_requirements_parser.py)

```python
def test_parse_todo_api_requirements():
    """実際のtodo-api要件書を解析"""
    parser = RequirementsParser()
    tasks = parser.parse(Path("examples/todo-api/requirements.md"))

    assert len(tasks) >= 15  # 少なくとも15タスク生成

    # データベースタスクの検証
    db_task = next(t for t in tasks if 'database' in t.title.lower())
    assert 'backend/database.py' in db_task.target_files
    assert 'backend/models.py' in db_task.target_files

    # 依存関係の検証
    auth_endpoint_task = next(t for t in tasks if '登録' in t.title)
    assert any('database' in t or 'model' in t
               for dep_id in auth_endpoint_task.dependencies
               for t in [next(task.title.lower()
                             for task in tasks if task.id == dep_id)])
```

**期待される効果:**
- タスク定義時間: 20分 → 1分（95%削減）
- エラー率: 人為的ミス削減
- 再現性: 同じrequirementsから同じタスク生成

---

### Phase 6: ファイル競合検出強化 (優先度: 🟡 中)

**目標**: ファイルレベルの依存関係を自動検出

**実装内容:**

#### 6.1 ConflictDetector (1-2時間)

```python
# src/cmw/conflict_detector.py

from typing import List, Dict, Set, Tuple
from .models import Task
import networkx as nx

class ConflictDetector:
    """ファイル競合の検出と解決提案"""

    def detect_conflicts(self, tasks: List[Task]) -> List[Dict]:
        """
        ファイル競合を検出

        Returns:
            競合情報のリスト [
                {
                    'file': 'backend/routers/auth.py',
                    'tasks': ['TASK-004', 'TASK-005'],
                    'conflict_type': 'write-write',
                    'severity': 'high'
                }
            ]
        """
        conflicts = []
        file_to_tasks = self._group_by_file(tasks)

        for file, task_ids in file_to_tasks.items():
            if len(task_ids) > 1:
                conflict = {
                    'file': file,
                    'tasks': task_ids,
                    'conflict_type': self._determine_conflict_type(task_ids, tasks),
                    'severity': 'high' if len(task_ids) > 2 else 'medium'
                }
                conflicts.append(conflict)

        return conflicts

    def suggest_execution_order(self, tasks: List[Task]) -> List[List[str]]:
        """
        競合を避ける実行順序を提案

        Returns:
            並列実行グループのリスト [
                ['TASK-001', 'TASK-002'],  # グループ1: 並列実行可能
                ['TASK-003'],               # グループ2: 依存あり
                ['TASK-004', 'TASK-005']    # グループ3: 並列実行可能
            ]
        """
        # 依存関係グラフを構築
        G = nx.DiGraph()
        for task in tasks:
            G.add_node(task.id)
            for dep in task.dependencies:
                G.add_edge(dep, task.id)

        # トポロジカルソート
        sorted_tasks = list(nx.topological_sort(G))

        # レベルごとにグループ化（並列実行可能なタスク）
        groups = []
        remaining = set(sorted_tasks)

        while remaining:
            # 依存が全て解決済みのタスクを取得
            ready = [t for t in remaining
                    if all(dep not in remaining for dep in tasks_by_id[t].dependencies)]

            groups.append(ready)
            remaining -= set(ready)

        return groups
```

**期待される効果:**
- ファイル競合の事前検出
- 最適な実行順序の提案
- 並列実行の最大化

---

### Phase 7: リアルタイム進捗UI (優先度: 🟡 中)

**目標**: ターミナルUIで進捗を可視化

**実装内容:**

#### 7.1 ProgressDashboard (2-3時間)

```python
# src/cmw/dashboard.py

from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.table import Table
from rich.live import Live
from datetime import datetime, timedelta
from typing import Dict, List
from .models import Task, TaskStatus

class ProgressDashboard:
    """リアルタイム進捗ダッシュボード"""

    def __init__(self, tasks: List[Task], progress_data: Dict):
        self.console = Console()
        self.tasks = tasks
        self.progress_data = progress_data

    def render(self) -> Table:
        """ダッシュボードをレンダリング"""
        table = Table(title="プロジェクト進捗", show_header=True)
        table.add_column("項目", style="cyan")
        table.add_column("値", style="green")

        # 統計情報
        stats = self._calculate_stats()

        table.add_row("総タスク数", str(stats['total']))
        table.add_row("完了", f"[green]{stats['completed']}[/green]")
        table.add_row("進行中", f"[yellow]{stats['in_progress']}[/yellow]")
        table.add_row("保留", f"[blue]{stats['pending']}[/blue]")
        table.add_row("失敗", f"[red]{stats['failed']}[/red]")
        table.add_row("進捗率", f"{stats['progress_percent']:.1f}%")
        table.add_row("推定残り時間", stats['eta'])

        return table

    def show_live(self):
        """ライブ更新ダッシュボード"""
        with Live(self.render(), refresh_per_second=1) as live:
            while not self._is_complete():
                live.update(self.render())
                time.sleep(1)

    def _calculate_eta(self) -> str:
        """推定残り時間を計算"""
        completed_tasks = [t for t in self.progress_data['tasks'].values()
                          if t['status'] == 'completed']

        if not completed_tasks:
            return "不明"

        # 平均タスク時間を計算
        total_time = 0
        for task in completed_tasks:
            if task.get('started_at') and task.get('completed_at'):
                start = datetime.fromisoformat(task['started_at'])
                end = datetime.fromisoformat(task['completed_at'])
                total_time += (end - start).total_seconds()

        avg_time = total_time / len(completed_tasks)

        # 残タスク数
        remaining = len([t for t in self.progress_data['tasks'].values()
                        if t['status'] in ['pending', 'in_progress']])

        eta_seconds = avg_time * remaining
        eta = timedelta(seconds=int(eta_seconds))

        return str(eta)
```

#### 7.2 CLIコマンド

```bash
# ダッシュボードを表示
cmw dashboard

# ライブ更新
cmw dashboard --live

# タスクタイムライン表示
cmw timeline
```

**期待される効果:**
- 進捗の即座の把握
- 残り時間の見積もり
- モチベーション向上

---

### Phase 8: Claude Code統合の最適化 (優先度: 🟢 低)

**目標**: Claude Codeとのシームレスな統合

**実装内容:**

#### 8.1 プロンプトテンプレート

```python
# src/cmw/prompts.py

class PromptGenerator:
    """Claude Code用プロンプト生成"""

    def generate_task_prompt(self, task: Task, context: Dict) -> str:
        """
        タスク実行用プロンプトを生成

        Args:
            task: 実行するタスク
            context: TaskProvider.get_task_context()の結果

        Returns:
            Claude Codeに渡すプロンプト
        """
        prompt = f"""
# タスク: {task.title}

## 概要
{task.description}

## 対象ファイル
{chr(10).join(f"- {f}" for f in task.target_files)}

## 受け入れ基準
{chr(10).join(f"- {c}" for c in task.acceptance_criteria)}

## 依存タスク
{chr(10).join(f"- {dep}: {context['dependencies'][dep]['title']}"
              for dep in task.dependencies)}

## 関連成果物
{chr(10).join(f"- {f}" for f in context['related_artifacts'])}

## 実装ガイド
1. 上記の受け入れ基準を全て満たすコードを実装してください
2. 既存のコードスタイルに従ってください
3. 適切なエラーハンドリングを含めてください
4. テストコードも合わせて作成してください

実装を開始してください。
"""
        return prompt
```

---

## 📅 実装スケジュール

### 優先順位

| Phase | 優先度 | 期待工数 | 期待効果 | 開始条件 |
|-------|--------|----------|----------|----------|
| Phase 5 | 🔴 最高 | 5-7時間 | タスク定義時間95%削減 | すぐ開始可能 |
| Phase 6 | 🟡 中 | 3-4時間 | 並列実行の安全性向上 | Phase 5完了後 |
| Phase 7 | 🟡 中 | 4-5時間 | UX大幅改善 | Phase 5完了後 |
| Phase 8 | 🟢 低 | 2-3時間 | Claude Code統合改善 | Phase 5-7完了後 |

### 推奨実装順序

**Week 1: Phase 5 (自動タスク生成)**
- Day 1-2: RequirementsParser実装
- Day 3: テスト作成と実例検証
- Day 4: CLIコマンド統合
- Day 5: ドキュメント更新

**Week 2: Phase 6 & 7 (並列で実装可能)**
- Day 1-2: ConflictDetector実装
- Day 3-4: ProgressDashboard実装
- Day 5: 統合テストと検証

**Week 3: Phase 8 & 統合**
- Day 1-2: PromptGenerator実装
- Day 3: 全機能の統合テスト
- Day 4-5: 実プロジェクトでの検証

---

## 🎯 成功指標

### Phase 5完了時
- [ ] requirements.mdからタスクを1分以内に生成
- [ ] todo-apiプロジェクトで17タスク自動生成
- [ ] 依存関係の自動推論が80%以上の精度
- [ ] target_filesの推論が70%以上の精度

### Phase 6完了時
- [ ] ファイル競合を100%検出
- [ ] 最適な実行順序を提案
- [ ] 並列実行可能タスクを正確に判定

### Phase 7完了時
- [ ] リアルタイムで進捗を表示
- [ ] 推定残り時間の誤差が±20%以内
- [ ] ターミナルUIが見やすい

### Phase 8完了時
- [ ] Claude Codeとの統合がスムーズ
- [ ] プロンプト生成が自動化
- [ ] タスク実行が完全自動化

---

## 📊 検証データ (todo-api)

### タスク分布
```
高優先度 (high):     7タスク (41%)
中優先度 (medium):   8タスク (47%)
低優先度 (low):      2タスク (12%)
```

### ファイル編集頻度
```
routers/tasks.py:    6タスク (最多)
routers/auth.py:     2タスク
models.py:           2タスク
database.py:         2タスク
schemas.py:          1タスク
```

### 依存関係の深さ
```
レベル0 (依存なし):  3タスク
レベル1 (1階層):     5タスク
レベル2 (2階層):     6タスク
レベル3 (3階層):     3タスク
```

---

## 🔗 参考リンク

- [todo-api検証プロジェクト](https://github.com/nakishiyaman/todo-api)
- [cmwフレームワーク](https://github.com/nakishiyaman/claude-multi-worker-framework)
- [Claude Code統合ガイド](./CLAUDE_CODE_INTEGRATION.md)

---

**次のステップ**: Phase 5 (自動タスク生成) の実装を開始
