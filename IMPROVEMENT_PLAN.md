# CMW v0.2.0 改善計画

**基準日**: 2025-10-16
**対象バージョン**: v0.1.0 → v0.2.0
**参照**: LESSONS_LEARNED.md (blog-api検証結果)

---

## 🎯 改善の目標

Blog API検証で発見された **6つの課題** のうち、**Phase 1の4項目**を修正し、CMWの基本機能を安定化させる。

### 成功基準
1. ✅ 循環依存が自動検出・修正される
2. ✅ 非タスク項目が自動除外される
3. ✅ blog-apiプロジェクトで17→12タスクに最適化
4. ✅ 手動修正なしでタスク分析が成功

---

## 📋 Phase 1: 基本機能の安定化（v0.2.0）

### Phase 1.1: 循環依存の自動検出 ⭐⭐⭐ CRITICAL

#### 目的
NetworkX例外が発生する前に循環依存を検出し、ユーザーに通知する。

#### 実装ファイル
- `src/cmw/dependency_validator.py` (新規作成)

#### 実装内容

```python
"""
Dependency Validator - 依存関係の検証と修正
"""
from typing import List, Set, Tuple, Optional
import networkx as nx
from cmw.models import Task

class DependencyValidator:
    """タスク依存関係の検証と修正を行うクラス"""

    def detect_cycles(self, tasks: List[Task]) -> List[List[str]]:
        """
        循環依存を検出

        Returns:
            循環依存のリスト（各要素はタスクIDのリスト）
            例: [['TASK-004', 'TASK-005'], ['TASK-024', 'TASK-025']]
        """
        G = self._build_dependency_graph(tasks)

        try:
            # サイクル検出
            cycles = list(nx.simple_cycles(G))
            return cycles
        except nx.NetworkXNoCycle:
            return []

    def _build_dependency_graph(self, tasks: List[Task]) -> nx.DiGraph:
        """依存関係グラフを構築"""
        G = nx.DiGraph()

        for task in tasks:
            G.add_node(task.id)
            for dep_id in task.dependencies:
                G.add_edge(task.id, dep_id)

        return G

    def suggest_fixes(self, cycles: List[List[str]], tasks: List[Task]) -> List[dict]:
        """
        循環依存の修正案を提案

        Returns:
            修正案のリスト
            [
                {
                    'cycle': ['TASK-004', 'TASK-005'],
                    'suggestions': [
                        {
                            'action': 'remove_dependency',
                            'from_task': 'TASK-004',
                            'to_task': 'TASK-005',
                            'reason': 'モデル定義はDB初期化の前に必要'
                        }
                    ]
                }
            ]
        """
        suggestions = []

        for cycle in cycles:
            cycle_suggestions = self._analyze_cycle(cycle, tasks)
            suggestions.append({
                'cycle': cycle,
                'suggestions': cycle_suggestions
            })

        return suggestions

    def _analyze_cycle(self, cycle: List[str], tasks: List[Task]) -> List[dict]:
        """循環依存を分析して修正案を生成"""
        suggestions = []
        task_map = {t.id: t for t in tasks}

        # サイクル内の各エッジを評価
        for i in range(len(cycle)):
            from_id = cycle[i]
            to_id = cycle[(i + 1) % len(cycle)]

            from_task = task_map.get(from_id)
            to_task = task_map.get(to_id)

            if not from_task or not to_task:
                continue

            # セマンティック分析で削除すべきエッジを判定
            reason = self._should_remove_edge(from_task, to_task)

            if reason:
                suggestions.append({
                    'action': 'remove_dependency',
                    'from_task': from_id,
                    'to_task': to_id,
                    'reason': reason,
                    'confidence': self._calculate_confidence(from_task, to_task)
                })

        # 信頼度順にソート
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)

        return suggestions

    def _should_remove_edge(self, from_task: Task, to_task: Task) -> Optional[str]:
        """
        エッジを削除すべきかセマンティック分析で判定

        Returns:
            削除すべき理由（削除不要ならNone）
        """
        # パターン1: 定義 → 初期化 の逆依存
        if any(kw in from_task.title for kw in ['定義', 'モデル', 'スキーマ']) and \
           any(kw in to_task.title for kw in ['初期化', 'セットアップ', '設定']):
            return f"{from_task.title}は{to_task.title}の前に必要"

        # パターン2: 実装 → 実装ガイドライン の依存
        if any(kw in to_task.title for kw in ['技術スタック', '推奨', '非機能要件']):
            return f"{to_task.title}は実装タスクではなくガイドライン"

        # パターン3: 番号が小さい方が先行すべき
        from_num = self._extract_section_number(from_task.title)
        to_num = self._extract_section_number(to_task.title)

        if from_num and to_num and from_num < to_num:
            return f"セクション順序: {from_num} < {to_num}"

        return None

    def _extract_section_number(self, title: str) -> Optional[float]:
        """タイトルからセクション番号を抽出（例: "2.1" → 2.1）"""
        import re
        match = re.match(r'^(\d+)\.(\d+)', title)
        if match:
            return float(f"{match.group(1)}.{match.group(2)}")
        return None

    def _calculate_confidence(self, from_task: Task, to_task: Task) -> float:
        """修正提案の信頼度を計算（0.0-1.0）"""
        confidence = 0.5

        # セマンティックマッチがある場合は高信頼度
        if self._should_remove_edge(from_task, to_task):
            confidence += 0.3

        # ファイルの依存関係を考慮
        if self._has_file_dependency(from_task, to_task):
            confidence += 0.2

        return min(confidence, 1.0)

    def _has_file_dependency(self, from_task: Task, to_task: Task) -> bool:
        """ファイルレベルの依存関係を判定"""
        # from_taskのtarget_filesがto_taskのファイルに依存しているか
        # （簡易実装: 共通ファイルがあれば依存あり）
        from_files = set(from_task.target_files or [])
        to_files = set(to_task.target_files or [])
        return bool(from_files & to_files)

    def auto_fix_cycles(self, tasks: List[Task], cycles: List[List[str]],
                        auto_apply: bool = False) -> List[Task]:
        """
        循環依存を自動修正

        Args:
            tasks: タスクリスト
            cycles: 検出された循環依存
            auto_apply: Trueの場合は自動適用、Falseの場合は確認を求める

        Returns:
            修正後のタスクリスト
        """
        suggestions = self.suggest_fixes(cycles, tasks)
        task_map = {t.id: t for t in tasks}

        for suggestion in suggestions:
            cycle = suggestion['cycle']
            fixes = suggestion['suggestions']

            if not fixes:
                continue

            # 最も信頼度の高い修正を適用
            best_fix = fixes[0]

            if best_fix['confidence'] < 0.7 and not auto_apply:
                # 信頼度が低い場合はスキップ（ユーザー確認が必要）
                continue

            # 依存関係を削除
            from_task = task_map[best_fix['from_task']]
            to_task_id = best_fix['to_task']

            if to_task_id in from_task.dependencies:
                from_task.dependencies.remove(to_task_id)
                print(f"✅ 修正: {best_fix['from_task']} → {to_task_id} を削除")
                print(f"   理由: {best_fix['reason']}")

        return list(task_map.values())
```

#### テストケース
```python
# tests/test_dependency_validator.py
def test_detect_cycles():
    """循環依存の検出テスト"""
    tasks = [
        Task(id="TASK-004", dependencies=["TASK-005"]),
        Task(id="TASK-005", dependencies=["TASK-004"]),
    ]
    validator = DependencyValidator()
    cycles = validator.detect_cycles(tasks)
    assert len(cycles) == 1
    assert set(cycles[0]) == {"TASK-004", "TASK-005"}

def test_suggest_fixes():
    """修正提案のテスト"""
    tasks = [
        Task(id="TASK-004", title="2.1 モデル定義", dependencies=["TASK-005"]),
        Task(id="TASK-005", title="2.2 データベース初期化", dependencies=["TASK-004"]),
    ]
    validator = DependencyValidator()
    cycles = validator.detect_cycles(tasks)
    suggestions = validator.suggest_fixes(cycles, tasks)

    assert len(suggestions) == 1
    assert suggestions[0]['suggestions'][0]['from_task'] == "TASK-004"
    assert "定義" in suggestions[0]['suggestions'][0]['reason']
```

---

### Phase 1.2: 循環依存の自動修正 ⭐⭐⭐ CRITICAL

#### 目的
検出された循環依存を自動修正し、タスク分析を成功させる。

#### 実装ファイル
- `src/cmw/requirements_parser.py` (既存ファイルを修正)

#### 実装内容

```python
class RequirementsParser:
    """既存クラスに追加"""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.validator = DependencyValidator()  # 新規追加

    def parse(self, requirements_path: Optional[Path] = None) -> List[Task]:
        """
        requirements.mdをパースしてタスクを生成

        v0.2.0: 循環依存の自動検出と修正を追加
        """
        # 既存のパース処理
        tasks = self._parse_requirements_file(requirements_path)

        # 🆕 循環依存の検出と修正
        cycles = self.validator.detect_cycles(tasks)

        if cycles:
            print(f"\n⚠️  {len(cycles)}件の循環依存を検出しました:")
            for i, cycle in enumerate(cycles, 1):
                print(f"  {i}. {' ↔ '.join(cycle)}")

            # 修正提案を生成
            suggestions = self.validator.suggest_fixes(cycles, tasks)

            print("\n💡 推奨される修正:")
            for suggestion in suggestions:
                for fix in suggestion['suggestions'][:1]:  # 最良の提案のみ表示
                    print(f"  - {fix['from_task']} → {fix['to_task']} を削除")
                    print(f"    理由: {fix['reason']}")
                    print(f"    信頼度: {fix['confidence']:.0%}")

            # 自動修正を適用
            print("\n🔧 自動修正を適用中...")
            tasks = self.validator.auto_fix_cycles(tasks, cycles, auto_apply=True)

            # 修正後の確認
            remaining_cycles = self.validator.detect_cycles(tasks)
            if remaining_cycles:
                print(f"\n⚠️  {len(remaining_cycles)}件の循環依存が残っています")
                print("   手動での確認と修正が必要です")
            else:
                print("\n✅ 全ての循環依存を解決しました")

        return tasks
```

---

### Phase 1.3: 非タスク項目の除外 ⭐⭐⭐ CRITICAL

#### 目的
「技術スタック」「非機能要件」などの非タスク項目を自動除外する。

#### 実装ファイル
- `src/cmw/task_filter.py` (新規作成)

#### 実装内容

```python
"""
Task Filter - タスクと非タスクを判別
"""
from typing import List
from cmw.models import Task

class TaskFilter:
    """タスク/非タスクを判別し、適切にフィルタリング"""

    # 非タスクを示すキーワード
    NON_TASK_KEYWORDS = [
        '技術スタック', '推奨', '前提条件', '概要',
        '非機能要件', '制約', '想定', '注意',
        '背景', '目的', 'について', 'とは',
        '説明', '紹介', 'まとめ'
    ]

    # タスクを示す動詞
    TASK_VERBS = [
        '実装', '作成', '構築', '開発', '設計',
        '追加', '修正', '更新', '削除', '統合',
        'テスト', '検証', 'デプロイ', '設定'
    ]

    def is_implementation_task(self, task: Task) -> bool:
        """
        実装タスクかどうかを判定

        Args:
            task: 判定対象のタスク

        Returns:
            True: 実装タスク、False: 非タスク項目
        """
        title = task.title.lower()
        description = (task.description or '').lower()

        # 1. 非タスクキーワードチェック
        for keyword in self.NON_TASK_KEYWORDS:
            if keyword in title:
                return False

        # 2. タスク動詞チェック
        has_task_verb = any(verb in description for verb in self.TASK_VERBS)
        if not has_task_verb:
            return False

        # 3. 受入基準チェック（具体的な基準があればタスク）
        if task.acceptance_criteria:
            # 受入基準が具体的か判定
            if self._has_concrete_criteria(task.acceptance_criteria):
                return True

        # 4. target_filesチェック（具体的なファイルがあればタスク）
        if task.target_files and len(task.target_files) > 0:
            # ファイルパスが具体的か判定
            if self._has_concrete_files(task.target_files):
                return True

        return False

    def _has_concrete_criteria(self, criteria: List[str]) -> bool:
        """受入基準が具体的かどうか判定"""
        # 抽象的なキーワードが含まれていないか
        abstract_keywords = ['推奨', '想定', '例えば', 'など']

        for criterion in criteria:
            if any(kw in criterion for kw in abstract_keywords):
                return False

        # 少なくとも1つは具体的な動詞を含むか
        return any(any(verb in criterion for verb in self.TASK_VERBS)
                   for criterion in criteria)

    def _has_concrete_files(self, files: List[str]) -> bool:
        """ファイルパスが具体的かどうか判定"""
        # すべてのファイルが実在のパスっぽいか
        for file_path in files:
            if file_path.startswith('backend/') or file_path.startswith('tests/'):
                return True
        return False

    def filter_tasks(self, tasks: List[Task]) -> tuple[List[Task], List[Task]]:
        """
        タスクをフィルタリング

        Returns:
            (実装タスクのリスト, 除外された非タスクのリスト)
        """
        implementation_tasks = []
        non_tasks = []

        for task in tasks:
            if self.is_implementation_task(task):
                implementation_tasks.append(task)
            else:
                non_tasks.append(task)

        return implementation_tasks, non_tasks

    def convert_to_references(self, non_tasks: List[Task]) -> List[dict]:
        """
        非タスクを参照情報に変換

        Returns:
            参照情報のリスト
            [
                {
                    'id': 'REF-001',
                    'title': '技術スタック',
                    'content': '...',
                    'applies_to': ['TASK-001', 'TASK-004']
                }
            ]
        """
        references = []

        for i, non_task in enumerate(non_tasks, 1):
            ref = {
                'id': f'REF-{i:03d}',
                'title': non_task.title,
                'content': non_task.description or '',
                'criteria': non_task.acceptance_criteria or [],
                'applies_to': []  # 後で関連タスクを推論
            }
            references.append(ref)

        return references
```

#### RequirementsParserへの統合

```python
class RequirementsParser:
    """既存クラスに追加"""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.validator = DependencyValidator()
        self.task_filter = TaskFilter()  # 🆕 追加

    def parse(self, requirements_path: Optional[Path] = None) -> List[Task]:
        """
        requirements.mdをパースしてタスクを生成

        v0.2.0: 非タスク項目のフィルタリングを追加
        """
        # 既存のパース処理
        all_items = self._parse_requirements_file(requirements_path)

        # 🆕 非タスク項目をフィルタリング
        tasks, non_tasks = self.task_filter.filter_tasks(all_items)

        if non_tasks:
            print(f"\n📋 {len(non_tasks)}件の非タスク項目を検出:")
            for non_task in non_tasks:
                print(f"  - {non_task.id}: {non_task.title}")

            # 参照情報に変換
            references = self.task_filter.convert_to_references(non_tasks)
            print(f"\n💡 これらは参照情報として保存されます")

            # references.jsonに保存
            self._save_references(references)

        print(f"\n✅ {len(tasks)}個の実装タスクを生成しました")

        # 循環依存の検出と修正
        cycles = self.validator.detect_cycles(tasks)
        # ... (Phase 1.2の処理)

        return tasks
```

---

### Phase 1.4: 依存関係推論ロジックの改善 ⭐⭐

#### 目的
セクション番号だけでなく、セマンティック分析も考慮した依存関係推論。

#### 実装内容

```python
class DependencyInference:
    """依存関係の推論ロジック"""

    def infer_dependencies(self, tasks: List[Task]) -> List[Task]:
        """
        タスク間の依存関係を推論

        ロジック:
        1. セクション階層による依存
        2. セマンティック分析（キーワードベース）
        3. ファイル依存関係
        4. 循環参照のチェックと除外
        """
        # 1. セクション階層
        tasks = self._infer_from_hierarchy(tasks)

        # 2. セマンティック分析
        tasks = self._infer_from_semantics(tasks)

        # 3. ファイル依存関係
        tasks = self._infer_from_files(tasks)

        # 4. 循環参照を除外
        validator = DependencyValidator()
        cycles = validator.detect_cycles(tasks)
        if cycles:
            tasks = validator.auto_fix_cycles(tasks, cycles, auto_apply=True)

        return tasks

    def _infer_from_semantics(self, tasks: List[Task]) -> List[Task]:
        """セマンティック分析で依存関係を推論"""
        patterns = [
            # (先行タスクのキーワード, 後続タスクのキーワード)
            (['モデル', '定義', 'スキーマ'], ['初期化', 'セットアップ']),
            (['データベース', 'DB'], ['マイグレーション']),
            (['認証', 'ログイン'], ['プロフィール', '更新']),
            (['API', 'エンドポイント'], ['テスト']),
            (['実装', '作成'], ['テスト', '検証']),
        ]

        task_map = {t.id: t for t in tasks}

        for task in tasks:
            for prerequisite_kws, dependent_kws in patterns:
                # このタスクが後続タスクか？
                if any(kw in task.title for kw in dependent_kws):
                    # 先行タスクを探す
                    for other_task in tasks:
                        if other_task.id == task.id:
                            continue
                        if any(kw in other_task.title for kw in prerequisite_kws):
                            # 依存関係を追加
                            if other_task.id not in task.dependencies:
                                task.dependencies.append(other_task.id)

        return tasks
```

---

## 📋 Phase 2: ユーザビリティ向上（v0.2.0）

### Phase 2.1: タスク検証コマンド ⭐⭐

#### コマンド実装
```bash
cmw tasks validate
```

#### 機能
1. 循環依存の検出
2. 非タスク項目の警告
3. ファイルパスの妥当性チェック
4. 依存関係の論理的整合性検証
5. 修正提案の出力

#### 実装
```python
# src/cmw/cli.py

@tasks.command('validate')
@click.option('--fix', is_flag=True, help='自動修正を適用')
def validate_tasks(fix: bool):
    """タスクの妥当性を検証"""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()

    # タスクを読み込み
    coordinator = Coordinator(Path.cwd())
    tasks_list = list(coordinator.tasks.values())

    console.print(Panel("[bold]タスク検証を実行中...[/bold]"))

    # 1. 循環依存チェック
    validator = DependencyValidator()
    cycles = validator.detect_cycles(tasks_list)

    if cycles:
        console.print(f"\n[red]❌ {len(cycles)}件の循環依存を検出[/red]")
        for cycle in cycles:
            console.print(f"  {' ↔ '.join(cycle)}")

        if fix:
            tasks_list = validator.auto_fix_cycles(tasks_list, cycles, auto_apply=True)
            console.print("[green]✅ 循環依存を自動修正しました[/green]")
    else:
        console.print("[green]✅ 循環依存なし[/green]")

    # 2. 非タスク項目チェック
    task_filter = TaskFilter()
    impl_tasks, non_tasks = task_filter.filter_tasks(tasks_list)

    if non_tasks:
        console.print(f"\n[yellow]⚠️  {len(non_tasks)}件の非タスク項目を検出[/yellow]")
        for nt in non_tasks:
            console.print(f"  {nt.id}: {nt.title}")
    else:
        console.print("[green]✅ 全て実装タスク[/green]")

    # 3. サマリー
    table = Table(title="検証結果")
    table.add_column("項目")
    table.add_column("結果")

    table.add_row("総タスク数", str(len(tasks_list)))
    table.add_row("実装タスク", str(len(impl_tasks)))
    table.add_row("非タスク項目", str(len(non_tasks)))
    table.add_row("循環依存", str(len(cycles)))

    console.print(table)
```

---

### Phase 2.2: Git連携による進捗自動更新 ⭐⭐

#### 機能
Gitコミットメッセージからタスク完了を自動検出

#### 実装
```python
# src/cmw/git_integration.py (新規)

class GitIntegration:
    """Git連携機能"""

    def sync_progress_from_git(self, project_path: Path, since: str = "1.day.ago"):
        """
        Gitコミット履歴から進捗を同期

        Args:
            project_path: プロジェクトパス
            since: コミット検索の開始時点（例: "1.day.ago", "1.week.ago"）
        """
        import subprocess
        import re

        # コミットログを取得
        result = subprocess.run(
            ['git', 'log', f'--since={since}', '--pretty=format:%H|||%s'],
            cwd=project_path,
            capture_output=True,
            text=True
        )

        commits = []
        for line in result.stdout.split('\n'):
            if not line:
                continue
            commit_hash, message = line.split('|||')
            commits.append({'hash': commit_hash, 'message': message})

        # コミットメッセージからタスクIDを抽出
        task_pattern = r'TASK-\d{3}'
        completed_tasks = set()

        for commit in commits:
            task_ids = re.findall(task_pattern, commit['message'])
            completed_tasks.update(task_ids)

        # 進捗を更新
        coordinator = Coordinator(project_path)
        for task_id in completed_tasks:
            if task_id in coordinator.tasks:
                task = coordinator.tasks[task_id]
                if task.status != TaskStatus.COMPLETED:
                    coordinator.mark_task_completed(task_id)
                    print(f"✅ {task_id} を完了にマーク")

        return len(completed_tasks)

# CLI統合
@click.command('sync')
@click.option('--from-git', is_flag=True, help='Gitから進捗を同期')
def sync_progress(from_git: bool):
    """進捗を同期"""
    if from_git:
        git = GitIntegration()
        count = git.sync_progress_from_git(Path.cwd())
        click.echo(f"✅ {count}個のタスクを完了にマークしました")
```

---

### Phase 2.3: 統合テストの実施 ⭐

#### テストシナリオ

**シナリオ1: Blog API再検証**
```bash
# 1. 新しいblog-apiプロジェクトを作成
cd /tmp
mkdir blog-api-v2
cd blog-api-v2

# 2. 同じrequirements.mdをコピー
cp ~/workspace/projects/blog-api/shared/docs/requirements.md .

# 3. タスク生成（v0.2.0）
cmw init --name blog-api-v2
cmw tasks generate

# 期待結果:
# - 17タスク → 12タスクに削減（非タスク項目除外）
# - 循環依存なし
# - 手動修正不要

# 4. 検証
cmw tasks validate
# 期待: 全チェックPASS

# 5. 競合分析
cmw tasks analyze
# 期待: NetworkX例外なし、正常に完了
```

**シナリオ2: Todo API再検証**
```bash
cd ~/workspace/projects/todo-api
cmw tasks validate
# 期待: 既存の17タスクも検証PASS
```

#### 成功基準
- ✅ Blog APIで手動修正なしでタスク分析成功
- ✅ 循環依存が0件
- ✅ 非タスク項目が除外される（17→12タスク）
- ✅ 全ての自動テストがPASS
- ✅ Todo APIでも問題なし

---

## 🔄 実装スケジュール

### Week 1: Phase 1実装
- Day 1-2: Phase 1.1（循環依存検出）
- Day 3-4: Phase 1.2（循環依存修正）
- Day 5: Phase 1.3（非タスク除外）

### Week 2: Phase 1完成とテスト
- Day 6: Phase 1.4（依存関係推論改善）
- Day 7-8: ユニットテスト作成
- Day 9: Phase 2.1（検証コマンド）
- Day 10: Phase 2.2（Git連携）

### Week 3: 統合テストとリリース
- Day 11-12: Phase 2.3（統合テスト）
- Day 13: バグ修正
- Day 14: ドキュメント更新
- Day 15: v0.2.0 リリース

---

## 📊 期待される効果

### Before (v0.1.0)
```
blog-api検証:
❌ 17タスク生成
❌ 2つの循環依存（手動修正必要）
❌ 非タスク項目が含まれる
❌ タスク分析失敗（NetworkX例外）
⚠️  進捗管理が手動
```

### After (v0.2.0)
```
blog-api検証:
✅ 12タスク生成（最適化）
✅ 循環依存0件（自動修正）
✅ 非タスク項目を除外
✅ タスク分析成功
✅ Git連携で進捗自動更新
```

### 改善率
- タスク数: 17 → 12 (-29%、最適化)
- 手動修正: 必要 → 不要
- 分析成功率: 0% → 100%
- ユーザー満足度: 向上予測 +50%

---

## 🎯 次のステップ（v0.3.0以降）

Phase 1が完了したら、Phase 2-3の残りの課題に取り組む：

- ファイル競合検出の精度向上（関数レベル）
- タスク説明の簡潔化
- 依存関係の静的分析
- インタラクティブな修正UI
- タスクグラフの可視化

---

**計画策定日**: 2025-10-16
**実装開始予定**: 2025-10-17
**リリース予定**: v0.2.0 (2025-11-01)
