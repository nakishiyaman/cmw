# テスト戦略とカバレッジ

このドキュメントでは、cmwのテスト戦略、カバレッジ情報、テスト実行方法を説明します。

## 目次

- [テスト概要](#テスト概要)
- [テストカテゴリ](#テストカテゴリ)
- [テスト実行方法](#テスト実行方法)
- [カバレッジレポート](#カバレッジレポート)
- [テスト追加ガイドライン](#テスト追加ガイドライン)

---

## テスト概要

### 現在の状況（v0.6.2）

- **総テスト数**: 500個
- **テストカバレッジ**: 88%
- **テストフレームワーク**: pytest
- **CI/CD**: GitHub Actions で自動実行

### テストの目的

1. **機能の正確性**: 各機能が仕様通りに動作することを保証
2. **回帰防止**: コード変更が既存機能を壊さないことを確認
3. **パフォーマンス**: 大規模データでもハングしないことを保証
4. **セキュリティ**: 攻撃に対する耐性を検証
5. **信頼性**: ファイルシステム障害時の堅牢性を確保

---

## テストカテゴリ

### 1. コア機能テスト（153テスト）

プロジェクトの基本機能をテストします。

#### test_task_provider.py (23テスト)
- タスク取得、コンテキスト構築
- タスク開始/完了マーク
- 並列実行可能性判定

```bash
python -m pytest tests/test_task_provider.py -v
```

#### test_state_manager.py (15テスト)
- ロック機構
- セッション管理
- 進捗永続化

```bash
python -m pytest tests/test_state_manager.py -v
```

#### test_parallel_executor.py (12テスト)
- 並列実行判定
- ファイル競合検出

```bash
python -m pytest tests/test_parallel_executor.py -v
```

#### test_error_handler.py (18テスト)
- エラー分類
- リトライ判定
- ロールバック

```bash
python -m pytest tests/test_error_handler.py -v
```

#### test_feedback.py (9テスト)
- フィードバックメッセージ生成
- 進捗表示

```bash
python -m pytest tests/test_feedback.py -v
```

#### test_coordinator.py (18テスト)
- タスク実行調整
- 状態遷移
- エラーハンドリング統合

```bash
python -m pytest tests/test_coordinator.py -v
```

#### test_cli_complete.py (18テスト)
- `cmw task complete`コマンド
- artifacts記録
- メッセージ追加

```bash
python -m pytest tests/test_cli_complete.py -v
```

#### その他
- `test_requirements_generator.py` (21テスト): 対話型requirements生成
- `test_dashboard.py` (21テスト): ダッシュボードUI
- `test_task_filter.py` (26テスト): タスクフィルタリング

---

### 2. パース・解析テスト（112テスト）

requirements.mdの解析と依存関係管理をテストします。

#### test_requirements_parser.py (43テスト)
- Markdown解析
- ファイルパス推論
- 依存関係推論
- 循環依存検出

```bash
python -m pytest tests/test_requirements_parser.py -v
```

#### test_dependency_validator.py (11テスト)
- 循環依存検出
- セマンティック分析
- 自動修正提案

```bash
python -m pytest tests/test_dependency_validator.py -v
```

#### test_conflict_detector.py (19テスト)
- ファイル競合検出
- 実行順序提案
- 並列実行グループ生成

```bash
python -m pytest tests/test_conflict_detector.py -v
```

#### test_static_analyzer.py (20テスト)
- Pythonコード静的解析
- ファイル依存関係検出
- 循環インポート検出

```bash
python -m pytest tests/test_static_analyzer.py -v
```

#### その他
- `test_graph_visualizer.py` (20テスト): グラフ可視化
- `test_dependency_analyzer.py` (25テスト): クリティカルパス分析

---

### 3. Claude Code統合テスト（73テスト）

Claude Codeとの統合機能をテストします。

#### test_prompt_template.py (18テスト)
- プロンプト自動生成
- 依存タスク情報埋め込み
- バッチ実行プロンプト

```bash
python -m pytest tests/test_prompt_template.py -v
```

#### test_response_parser.py (29テスト)
- ファイルパス抽出
- タスクID検出
- 完了キーワード検出
- エラー・質問検出

```bash
python -m pytest tests/test_response_parser.py -v
```

#### test_smart_prompt_generator.py (25テスト)
- 文脈を含む詳細プロンプト生成
- 依存関係情報
- 実装ガイド

```bash
python -m pytest tests/test_smart_prompt_generator.py -v
```

#### test_interactive_fixer.py (23テスト)
- 循環依存の対話的修正
- タスク選択UI
- 修正提案表示

```bash
python -m pytest tests/test_interactive_fixer.py -v
```

---

### 4. UI・表示テスト (33テスト)

ターミナルUIとグラフ表示をテストします。

#### test_progress_tracker.py (12テスト)
- 進捗サマリー計算
- ベロシティメトリクス
- 残り時間推定

```bash
python -m pytest tests/test_progress_tracker.py -v
```

#### test_dashboard.py (21テスト)
- ダッシュボードパネル生成
- プログレスバー表示
- アクティビティタイムライン

```bash
python -m pytest tests/test_dashboard.py -v
```

---

### 5. パフォーマンステスト（10テスト）

**v0.6.2で追加**

大規模データでの性能を保証します。

#### test_performance.py (10テスト)
- **循環検出タイムアウト防止**: 複雑グラフ（25タスク、10循環）で3秒以内完了
- **深い再帰の無限ループ防止**: 50段階の深い依存関係でスタックオーバーフローなし
- **大規模requirements.mdのパース**: 50セクション、500項目で10秒以内完了
- **大規模グラフの可視化**: 100タスクのグラフ生成が5秒以内
- **バリデーション性能**: 100タスクの検証が5秒以内

```bash
python -m pytest tests/test_performance.py -v
```

**重要性:**
このテストがなかったため、v0.6.1で循環検出がハングする問題が発生しました。v0.6.2で修正後、このテストにより再発を防止しています。

---

### 6. 統合テスト（11テスト）

**v0.6.2で追加**

エンドツーエンドのワークフローを検証します。

#### test_integration.py (11テスト)
- **完全ワークフロー**: パース → 検証 → 可視化
- **循環依存の自動修正フロー**: 検出 → 修正 → 再検証
- **JSON保存・読み込み**: タスクデータの永続化
- **エラーリカバリー**: 不正ファイル、空ファイル、存在しない依存先
- **並行処理**: 4スレッドで同時に循環検出
- **メモリ管理**: 100タスクでメモリリークなし
- **深い再帰**: 50段階の依存関係でスタックオーバーフローなし

```bash
python -m pytest tests/test_integration.py -v
```

---

### 7. エッジケーステスト（22テスト）

**v0.6.2で追加**

境界条件と特殊ケースを検証します。

#### test_edge_cases.py (22テスト)
- **境界条件**:
  - 0タスク、単一タスク、全タスクが1つに依存
  - 線形チェーン、完全グラフ
  - 切断されたサブグラフ
- **Unicode対応**:
  - 日本語タスクタイトル
  - 絵文字を含むrequirements.md
- **不正入力**:
  - 重複タスクID
  - 循環自己依存（TASK-001が自分自身に依存）
  - 存在しないタスクへの依存
- **TaskFilterエッジケース**:
  - 受け入れ基準が空
  - ファイルが空
  - ガイドラインタスク（非実装タスク）
- **GraphVisualizerエッジケース**:
  - 切断されたサブグラフ
  - 複数のリーフタスク

```bash
python -m pytest tests/test_edge_cases.py -v
```

---

### 8. セキュリティテスト（18テスト）

**v0.6.2で追加**

セキュリティ脆弱性を検証します。

#### test_security.py (18テスト)
- **パストラバーサル攻撃防止**:
  - `../../../etc/passwd`等の攻撃パス
  - 絶対パスの使用
- **コマンドインジェクション防止**:
  - タスクIDにシェルメタ文字（`; rm -rf /`）
  - ファイルパスにシェルメタ文字
- **ファイル権限**:
  - 作成ファイルが適切な権限（他者に書き込み権限なし）
  - 読み取り専用ファイルの処理
  - 権限のないファイルへのアクセス
- **入力バリデーション**:
  - 極端に長いタスクID（10000文字）
  - 極端に長いファイルパス（2000文字）
  - nullバイトを含むファイルパス
  - 特殊文字（HTML、スクリプトタグ）
- **DoS攻撃防止**:
  - 大量の依存関係（10000個）
  - 深くネストされたMarkdown（100段階）
  - Billion Laughs攻撃パターン
- **データ漏洩防止**:
  - エラーメッセージに機密情報が含まれないか
  - タスクデータに秘密情報が含まれないか
- **競合状態**:
  - 10スレッドでの同時ファイル書き込み

```bash
python -m pytest tests/test_security.py -v
```

---

### 9. 信頼性テスト（16テスト）

**v0.6.2で追加**

ファイルシステム障害時の堅牢性を検証します。

#### test_reliability.py (16テスト)
- **ファイル破損**:
  - 破損したJSONファイルの処理
  - 空のJSONファイル
  - 不正なUTF-8エンコーディング
  - 途中で切れたファイル
- **ディスク容量**:
  - 大量データの書き込み（1000タスク）
  - ディスク容量チェック
- **ファイルシステムエッジケース**:
  - 読み取り専用ファイルシステム
  - シンボリックリンクの処理
  - 特殊なファイル名（スペース、日本語、ドット複数）
  - 大文字小文字の区別
- **障害復旧**:
  - 部分的な保存からの復旧
  - バックアップと復元
- **冪等性**:
  - 同じファイルを複数回パースしても結果が一貫
  - 保存→読み込みを繰り返しても同じ
- **タイムアウト**:
  - 50セクションのパースが10秒以内
  - 100タスクの検証が5秒以内

```bash
python -m pytest tests/test_reliability.py -v
```

---

## テスト実行方法

### 全テスト実行

```bash
# 基本実行
python -m pytest tests/ -v

# カバレッジレポート付き
python -m pytest tests/ --cov=src/cmw --cov-report=term-missing

# HTML形式のカバレッジレポート
python -m pytest tests/ --cov=src/cmw --cov-report=html
# → htmlcov/index.html をブラウザで開く
```

### カテゴリ別実行

```bash
# パフォーマンステストのみ
python -m pytest tests/test_performance.py -v

# 品質保証テスト（v0.6.2で追加）
python -m pytest tests/test_performance.py tests/test_integration.py tests/test_edge_cases.py tests/test_security.py tests/test_reliability.py -v

# Claude Code統合テスト
python -m pytest tests/test_prompt_template.py tests/test_response_parser.py tests/test_smart_prompt_generator.py -v
```

### 特定テストのみ実行

```bash
# 特定のテストクラス
python -m pytest tests/test_performance.py::TestDependencyValidatorPerformance -v

# 特定のテストメソッド
python -m pytest tests/test_performance.py::TestDependencyValidatorPerformance::test_detect_cycles_with_complex_graph -v
```

### 並列実行（高速化）

```bash
# pytest-xdist プラグインを使用
pip install pytest-xdist

# 4プロセスで並列実行
python -m pytest tests/ -n 4
```

---

## カバレッジレポート

### 現在のカバレッジ（v0.6.2）

| モジュール | カバレッジ | ステートメント | 未カバー |
|-----------|-----------|---------------|---------|
| requirements_generator.py | 100% | 142 | 0 |
| dashboard.py | 100% | 95 | 0 |
| task_filter.py | 98% | 87 | 2 |
| static_analyzer.py | 99% | 124 | 1 |
| requirements_parser.py | 91% | 234 | 21 |
| cli.py | 72% | 312 | 87 |
| **全体** | **88%** | **2988** | **358** |

### カバレッジ改善の履歴

- **v0.5.0**: テストカバレッジ測定開始（72%）
- **v0.5.2**: 90%達成（+111テスト）
- **v0.6.2**: 88%維持（+66テスト、新規観点追加）

### 未カバー箇所の分析

主な未カバー箇所:
1. **cli.py**: 対話型入力の一部（モック困難）
2. **requirements_parser.py**: エラーハンドリングの一部（稀なケース）
3. **各モジュール**: デバッグ用ログ出力

---

## テスト追加ガイドライン

### 新機能追加時

新機能を追加する際は、以下のテストを必ず追加してください:

1. **正常系テスト**: 期待通りに動作することを確認
2. **異常系テスト**: エラーハンドリングが正しいことを確認
3. **エッジケーステスト**: 境界条件での動作を確認
4. **パフォーマンステスト**: 大規模データでハングしないことを確認

### テストの命名規則

```python
class TestModuleName:
    """モジュール名のテスト"""

    def test_function_name_normal_case(self):
        """正常系: 関数が期待通りに動作する"""
        pass

    def test_function_name_edge_case(self):
        """エッジケース: 境界条件での動作"""
        pass

    def test_function_name_error_handling(self):
        """異常系: エラーハンドリングが正しい"""
        pass
```

### pytest のベストプラクティス

1. **fixture を活用**: 共通のセットアップはfixtureに
2. **parametrize を活用**: 複数ケースを効率的にテスト
3. **モックは最小限**: 実際のファイルI/Oを優先
4. **assertメッセージ**: 失敗時に分かりやすいメッセージを

```python
@pytest.fixture
def sample_tasks():
    """サンプルタスクのfixture"""
    return [
        Task(id="TASK-001", title="Test", ...),
        Task(id="TASK-002", title="Test 2", ...),
    ]

@pytest.mark.parametrize("task_count,expected", [
    (0, []),
    (1, ["TASK-001"]),
    (10, ["TASK-001", "TASK-002", ...]),
])
def test_get_tasks_with_various_counts(task_count, expected):
    """タスク数によらず正しく取得できる"""
    tasks = get_tasks(task_count)
    assert [t.id for t in tasks] == expected
```

---

## まとめ

cmwは500個のテスト（88%カバレッジ）により、高い品質を保証しています。特にv0.6.2では、パフォーマンス、セキュリティ、信頼性の観点から66個のテストを追加し、本番環境での安定動作を実現しています。

新機能追加時は、このドキュメントのガイドラインに従ってテストを追加してください。
