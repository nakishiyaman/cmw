# Changelog

All notable changes to Claude Multi-Worker Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **循環依存の自動修正で無限ループを防止**
  - `auto_fix_cycles` に最大反復回数チェックを追加（デフォルト10回）
  - 修正が進まない場合は早期に停止
  - 無限ループのリスクを完全に排除

### Added
- **無限ループ防止のテストケース**
  - `test_auto_fix_no_progress_stops`: 進捗がない場合の停止テスト
  - `test_auto_fix_max_iterations`: 最大反復回数テスト

## [0.6.3] - 2025-10-18

### Fixed
- **グラフ可視化の循環依存検出を改善**
  - `cmw task graph` コマンドで循環依存を正確に検出・報告するように修正
  - 循環依存がある場合、明確なエラーメッセージと修正方法を表示
  - Mermaid形式でも循環依存を警告として表示
  - 誤解を招く「No tasks or circular dependencies detected」メッセージを削除

### Changed
- **ドキュメント整理と再構成**
  - README.mdの開発者向けドキュメントセクションを更新
  - 古い計画ドキュメント（Phase 1実装ガイド、アーキテクチャ設計v3.0）をアーカイブに移動
  - 現在メンテナンスされているドキュメントのみを記載
  - ユーザー向けと開発者向けを明確に分離
  - 壊れたリンク（IMPROVEMENTS.md）を削除

## [0.6.2] - 2025-10-18

### Fixed
- **クリティカルなパフォーマンス問題の修正**
  - 循環依存検出時のハング問題を解決
    - `nx.simple_cycles()` を `nx.find_cycle()` に置き換え（指数関数的な時間複雑度を回避）
    - 最大10サイクルまで検出する制限を追加
    - 複雑な依存関係グラフ（25タスク、10サイクル）でも3秒以内で完了
  - 無限再帰の防止
    - `GraphVisualizer.get_task_depth()` に循環検出機能を追加
    - 訪問済みノード追跡により無限ループを防止
    - 循環依存検出時は `-1` を返す

### Added
- **包括的なテストスイートの追加（+66テスト）**
  - `test_performance.py` (10テスト): パフォーマンス問題の早期検出
    - 複雑グラフでの循環検出テスト（<3秒制約）
    - 密なグラフでのハング防止テスト（<5秒制約）
    - 深い依存関係チェーン（30+レベル）のテスト
    - 大規模requirements.mdパーステスト（<30秒制約）

  - `test_integration.py` (11テスト): エンドツーエンドワークフロー検証
    - 完全フロー（パース → 検証 → 可視化）
    - エラーリカバリー（不正/空ファイル、不正Markdown）
    - 並行処理（4スレッド同時実行）
    - メモリ管理（100タスク、50段階の依存関係）
    - JSON永続化のround-tripテスト

  - `test_edge_cases.py` (22テスト): 境界条件と特殊ケース
    - 境界値（0タスク、単一タスク、完全グラフ）
    - Unicode/日本語/絵文字対応
    - 不正入力（重複ID、自己依存、存在しない依存先）
    - 切断されたサブグラフ
    - 各コンポーネントのエッジケース

  - `test_security.py` (18テスト): セキュリティ脆弱性の検出
    - パストラバーサル攻撃の防止（`../../etc/passwd`）
    - コマンドインジェクション防止
    - ファイル権限の検証
    - 入力バリデーション（長大入力、nullバイト）
    - DoS防止（10,000依存関係、100段階ネスト）
    - データ漏洩防止
    - 競合状態のテスト

  - `test_reliability.py` (16テスト): システム信頼性の検証
    - ファイル破損からの復旧
    - 不正なUTF-8エンコーディング対応
    - ディスク容量の考慮
    - 読み取り専用ファイルシステム
    - シンボリックリンク対応
    - 特殊ファイル名の処理（スペース、日本語、ドット）
    - バックアップと復元
    - 冪等性の保証
    - タイムアウト防止

### Changed
- テストカバレッジ: 434 → 500テスト (+15%)
- テストカバレッジ率: 88%維持
- テスト実行時間: ~11秒 → ~14秒（新規テスト追加による増加）

### Technical Details
- `dependency_validator.py:17-54`: 循環検出アルゴリズムの最適化
- `graph_visualizer.py:311-343`: 再帰関数への循環検出機能追加
- テストファイル: 24 → 29ファイル (+5)

## [0.6.1] - 2025-10-18

### Fixed
- **`cmw init`コマンドの動作改善**
  - 引数なしで実行した場合、カレントディレクトリで初期化するように修正（以前は常に`new-project`サブディレクトリを作成していた）
  - `cmw init`: カレントディレクトリで初期化（空でない場合は確認プロンプト表示）
  - `cmw init project-name`: 指定したサブディレクトリを作成して初期化
  - 既存のcmwプロジェクトでの初期化を防止

### Changed
- initコマンドの引数を`--name`オプションから位置引数に変更（より直感的な使い方）
- Python 3.9互換性のため型アノテーションを修正（`str | None` → `Optional[str]`）

## [0.6.0] - 2025-10-18

### Added
- **インテリジェント・タスク管理機能**
  - `DependencyAnalyzer`: 依存関係解析とクリティカルパス計算
    - 実行可能なタスクの自動判定
    - クリティカルパスの計算
    - ボトルネック検出
    - 並行実行プランの生成
    - プロジェクト完了予測

  - `SmartPromptGenerator`: 文脈を理解したプロンプト生成
    - タスクの重要度を視覚的に強調
    - 依存関係の詳細表示（前提・後続タスク）
    - 関連ファイルの自動推測
    - requirements.mdからの情報抽出
    - 実装手順の自動生成
    - 完了条件チェックリスト
    - テストコマンドの提示
    - 次のステップの提案

- **新規CLIコマンド**
  - `cmw task next`: 実行可能な次のタスクを提案
    - 依存関係が解決済みのタスクのみ表示
    - クリティカルパス上のタスクを強調
    - ブロックしているタスク数を表示
    - 優先度順にソート

  - `cmw task critical`: クリティカルパス分析
    - プロジェクト完了予測（楽観的・悲観的）
    - クリティカルパスの可視化
    - ボトルネック警告
    - 並行作業の効率化提案

  - `cmw task exec <TASK-ID>`: スマートタスク実行
    - ステータスを自動で`in_progress`に更新
    - スマートプロンプトを生成・表示
    - `.cmw_prompt.md`にプロンプトを保存

### Changed
- **README.md更新**
  - インテリジェント・タスク管理セクション追加
  - 実践的な使い方の追加
  - クリティカルパスを意識した進行例
  - チートシート追加

### Technical Details
- 新規ファイル:
  - `src/cmw/dependency_analyzer.py`: 依存関係解析機能
  - `src/cmw/smart_prompt_generator.py`: スマートプロンプト生成機能
  - `tests/test_dependency_analyzer.py`: 12テスト
  - `tests/test_smart_prompt_generator.py`: 13テスト
- 変更ファイル:
  - `src/cmw/cli.py`: 3つの新規コマンド追加
  - `src/cmw/__init__.py`: バージョン 0.5.6 → 0.6.0、新モジュールのエクスポート
  - `README.md`: 新機能のドキュメント追加
- テスト: 424テスト全パス (399 → 424, +25テスト)
- 型安全性: mypy 100%クリーン
- コード品質: ruff lint/format クリーン

## [0.5.6] - 2025-10-18

### Fixed
- **Package resource not found**: Fixed `cmw requirements generate --with-claude` command failing to find prompts template
  - Error: `プロンプトテンプレートが見つかりません: .../prompts/requirements_generator.md`
  - Root cause: `prompts/requirements_generator.md` was not included in the package
  - Solution: Moved template to `src/cmw/prompts/` and updated package data configuration

### Changed
- **Prompts template location**: Moved from project root to package directory
  - `prompts/requirements_generator.md` → `src/cmw/prompts/requirements_generator.md`
  - Updated `cli.py` to use `Path(__file__).parent / "prompts"` for correct package-relative path
  - Added `"prompts/*.md"` to `pyproject.toml` package data configuration

### Technical Details
- Modified files:
  - `src/cmw/cli.py:967`: Changed path from `Path(__file__).parent.parent.parent / "prompts"` to `Path(__file__).parent / "prompts" / "requirements_generator.md"`
  - `src/cmw/prompts/requirements_generator.md`: Created (copied from project root)
  - `pyproject.toml:61`: Updated package-data to include `["py.typed", "prompts/*.md"]`
  - `src/cmw/__init__.py`: Version updated to 0.5.6
  - `README.md`: Title updated to v0.5.6
- Impact:
  - `cmw requirements generate --with-claude` now works correctly in installed packages
  - Template file is properly included in wheel and sdist distributions
  - No changes to template content, only location
- All 399 tests passing
- 100% type safety maintained (mypy clean)
- 90% test coverage maintained

## [0.5.5] - 2025-10-18

### Fixed
- **CLI version hardcode**: Fixed `cmw --version` to dynamically use `__version__` from `src/cmw/__init__.py`
  - Changed `@click.version_option(version="0.3.1")` to `@click.version_option(version=__version__)`
  - Updated CLI docstring to use f-string with `__version__`
  - Now `cmw --version` correctly displays the current package version

### Added
- **PEP 561 compliance**: Created `src/cmw/py.typed` marker file
  - Enables type information export for downstream packages
  - Other projects can now use cmw's type annotations via mypy
  - Improves IDE autocomplete and type checking for library users

### Improved
- **Development environment**: Upgraded pip from 24.0 to 25.2
  - Latest pip version for improved package management
  - Better dependency resolution and performance

### Technical Details
- Modified files:
  - `src/cmw/cli.py`: Added `from . import __version__` and dynamic version usage
  - `src/cmw/py.typed`: Created empty marker file (PEP 561)
  - `src/cmw/__init__.py`: Version updated to 0.5.5
  - `pyproject.toml`: Version and description updated
  - `README.md`: Title updated to v0.5.5
- Benefits:
  - Single source of truth for version number (`__init__.py`)
  - Simpler release process (only update one file)
  - Type information now exportable to other packages
- All 399 tests passing
- 100% type safety maintained (mypy clean)
- 90% test coverage maintained

## [0.5.4] - 2025-10-18

### Fixed
- **`__version__` inconsistency**: Updated `src/cmw/__init__.py` `__version__` to 0.5.4
  - Fixed `cmw --version` to display correct version number
  - Ensured consistency with package metadata in `pyproject.toml`

### Technical Details
- Modified file: `src/cmw/__init__.py:8`
- Issue: `cmw --version` was displaying 0.3.1 instead of actual package version
- Root cause: `__version__` variable was not updated during v0.5.0-v0.5.3 releases
- Resolution: Updated `__version__ = "0.5.4"` and added version check to release checklist

## [0.5.3] - 2025-10-18

### Code Quality - Complexity Reduction

#### Complexity Improvements
- **Reduced high-complexity functions** from 12 to 10 (-2 functions)
- **Successfully refactored 2 most complex functions**:
  - `requirements_parser.py:parse()` - Complexity 27 → <10 (-17)
  - `cli.py:generate_tasks()` - Complexity 21 → <10 (-11)

#### Refactoring Details

**requirements_parser.py refactoring**:
- Extracted `parse()` method into 8 focused helper methods:
  - `_load_requirements()` - File loading
  - `_generate_tasks_from_sections()` - Task generation
  - `_filter_non_tasks()` - Filtering
  - `_print_non_task_report()` - Reporting
  - `_detect_and_fix_cycles()` - Cycle detection
  - `_print_cycles_report()` - Cycle reporting
  - `_print_fix_suggestions()` - Fix suggestions
  - `_verify_cycles_fixed()` - Verification
- Also refactored `_infer_target_files()` (complexity 11) by extracting:
  - `_detect_router_files()`
  - `_detect_backend_files()`
  - `_detect_test_files()`
  - `_detect_documentation_files()`

**cli.py refactoring**:
- Extracted `generate_tasks()` into 8 helper functions:
  - `_validate_requirements_exists()` - Existence check
  - `_confirm_overwrite()` - Overwrite confirmation
  - `_parse_requirements()` - Parsing
  - `_save_tasks_to_file()` - File saving
  - `_print_task_summary()` - Summary display
  - `_print_priority_summary()` - Priority breakdown
  - `_print_assignment_summary()` - Assignment breakdown
  - `_print_next_steps()` - Next steps

#### Testing
- **399 tests passing** - All tests continue to pass after refactoring
- **90% code coverage maintained** - No regression in test coverage
- Refactoring validated through comprehensive test suite

#### Remaining High-Complexity Functions (10)
- `cli.py:validate_tasks()` - Complexity 19
- `cli.py:sync()` - Complexity 14
- `requirements_parser.py:_extract_sections()` - Complexity 11
- `requirements_parser.py:_infer_dependencies()` - Complexity 14
- And 6 other functions documented in CODE_QUALITY.md

### Code Quality
- Applied Extract Method pattern for better maintainability
- Improved code readability with Single Responsibility Principle
- Maintained backward compatibility (no API changes)

### Technical Details
- Refactored 2 core functions using Extract Method pattern
- All helper methods are private (_prefix) to preserve public API
- Zero test modifications required (API unchanged)

## [0.5.2] - 2025-10-18

### Testing - 90% Coverage Achievement

#### Coverage Improvements
- **Achieved 90% test coverage** (72% → 90%, +18% improvement)
- **Total tests: 399** (288 → 399, +111 tests)
- **Total statements: 2988** (447 missing → 298 missing, -149 missing)

#### New Test Coverage
- **requirements_generator.py**: 0% → 100% (+21 tests)
  - Interactive generation with mocked user input
  - All project types and configuration options
  - Edge cases and error handling

- **dashboard.py**: 17% → 100% (+21 tests)
  - Summary panel creation and formatting
  - Velocity calculations and time tracking
  - Priority and worker tables
  - Progress visualization
  - All status display modes

- **task_filter.py**: 60% → 98% (+26 tests)
  - Implementation task detection logic
  - File and criteria validation
  - All keyword patterns (task verbs, non-task keywords)
  - Reference conversion

- **requirements_parser.py**: 73% → 91% (+20 tests)
  - Circular dependency detection
  - File relation detection
  - Various import patterns
  - Section parsing edge cases

- **static_analyzer.py**: 78% → 99% (+11 tests)
  - Import detection (ast.Import, relative imports)
  - sys.path modification handling
  - Complexity analysis
  - Module resolution

- **cli.py**: 45% → 72% (+12 tests)
  - tasks generate command with custom paths
  - status command (basic and compact modes)
  - task graph command (ASCII, Mermaid, stats)
  - task prompt command
  - tasks analyze command
  - init command

### Code Quality
- All 399 tests passing
- Comprehensive test suite covering critical functionality
- Better code reliability and maintainability

### Technical Details
- Added test_requirements_generator.py (21 tests)
- Added test_dashboard.py (21 tests)
- Added test_task_filter.py (26 tests)
- Extended test_requirements_parser.py (+20 tests)
- Extended test_static_analyzer.py (+11 tests)
- Added test_cli_basic.py (12 tests)

## [0.5.1] - 2025-10-18

### Code Quality

#### Lint and Format Improvements
- **Fixed 42 lint errors** (W293 whitespace, C414 unnecessary list())
- **Applied ruff format to 21 files** - Consistent code formatting across entire codebase
- **Fixed all E501 line length violations** - All lines now within 100 character limit
- Improved code readability and maintainability

### Documentation

#### New Documentation
- **CODE_QUALITY.md** - Comprehensive tracking of code quality issues
  - Documents 12 functions with high complexity (C901 > 10)
  - Provides refactoring recommendations categorized by priority
  - Tracks improvement progress and next steps

- **MYPY_IMPROVEMENTS.md** - Complete type safety achievement documentation
  - Updated to reflect 100% type safety (142 → 0 errors)
  - Documents all phases of type safety improvements
  - Provides best practices and examples for future development

#### Updated Documentation
- **CONTRIBUTING.md** - Enhanced with comprehensive type safety guidelines
  - 5 mandatory type annotation rules with examples
  - 4 best practices for maintainable type hints
  - Updated to use ruff format instead of black

### Testing
- **288 tests passing** - All existing tests continue to pass
- **72% code coverage** - Measured and documented baseline coverage
- Coverage report identifies areas for improvement in future releases

### Improvements
- All CI/CD checks passing
- Cleaner, more maintainable codebase
- Better developer experience with consistent formatting
- Comprehensive documentation for contributors

### Technical Details
- PR #14: Lint/format fixes
- PR #15: Documentation improvements

## [0.5.0] - 2025-10-18

### Added

#### Complete Type Safety - mypy 100% Clean
- **142 → 0 mypy errors** - Achieved 100% type safety across all 22 source files
- Added comprehensive type annotations throughout the codebase:
  - `Optional[Type]` for all parameters with `None` defaults (PEP 484 compliant)
  - `Dict[str, Any]` for heterogeneous dictionaries
  - `List[Dict[str, Any]]` for complex data structures
  - `nx.DiGraph` type annotations for NetworkX graphs
  - `Priority` enum usage instead of string literals
- Fixed type inference issues:
  - Lambda function return types in sort operations
  - json.loads return types with `cast()`
  - Collection type assignments (dict_values vs List vs Iterable)
  - datetime handling in dictionaries

#### CI/CD Improvements
- Added mypy type checking to GitHub Actions CI pipeline
- All PRs now automatically validated for type safety
- Prevents type errors from being introduced in the future

### Improved

- **Code Quality**: Enhanced type safety improves IDE autocomplete and catches bugs at development time
- **Documentation**: Type annotations serve as inline documentation for function signatures
- **Maintainability**: Easier refactoring with confidence thanks to type checking

### Dependencies

- Added `types-networkx>=3.0` to dev dependencies for NetworkX type stubs

### Configuration

- Updated `pyproject.toml` with mypy overrides for optional dependencies (pygraphviz)
- Configured strict mypy settings: `disallow_untyped_defs = true`

### Technical Details

**Phase 4 Part 1**: Optional and Collection fixes (29→21 errors)
- static_analyzer.py: Fixed Optional[List[Path]], variable naming, Dict annotations
- task_provider.py: Added Dict type annotations
- progress_tracker.py: Fixed lambda timestamp handling

**Phase 4 Part 2**: requirements_parser.py fixes (21→19 errors)
- Added type annotations for section dictionaries
- Changed _infer_priority() to return Priority enum
- Fixed Any return types with explicit conversions

**Phase 4 Part 3**: Final fixes (19→0 errors)
- cli.py: Fixed Iterable type for tasks_to_show
- state_manager.py: Added cast() for json.loads
- dependency_validator.py: Fixed Dict[str, Any] and lambda sort keys
- conflict_detector.py: Added Dict[str, Any] annotations
- progress_tracker.py: Replaced lambda with proper function for datetime sorting
- graph_visualizer.py: Fixed max() key function and added nx.DiGraph annotations

## [0.3.1] - 2025-10-16

### Added

#### Phase 8.6: Task Completion Command
- **`cmw task complete` コマンド実装**
  - タスクを完了としてマーク
  - `--artifacts` オプションで生成ファイルを記録（JSON配列形式）
  - `--message` オプションで完了メッセージを追加
  - 既に完了済みのタスクに対する警告表示
  - エラーハンドリング（存在しないタスク、不正なJSON形式）

### Improved

- **Coordinator進捗管理の強化**
  - progress.jsonからの進捗読み込み機能
  - tasks.jsonとprogress.jsonの自動マージ
  - 完了状態がコマンド間で永続化
  - completed_at, started_at, failed_at のタイムスタンプサポート

### Testing

- 総テスト数: 273 → 291（+18テスト）
  - test_cli_complete.py: 10個の新規テスト
  - test_coordinator.py: 8個の新規テスト
- 全てのテストがパス

### Validation

- todo-apiプロジェクトでTASK-014を完了マーク
- ResponseParserが提案するコマンドが実際に動作することを確認
- 完了状態がコマンド間で正しく保持されることを検証

### Fixed

- Coordinatorがprogress.jsonを読み込まない問題を修正
- タスクの完了状態が次のコマンド実行時に失われる問題を解決

## [0.3.0] - 2025-10-16

### Added

#### Phase 8.1: GraphVisualizer
- タスク依存関係グラフの可視化機能
  - ASCII形式での依存関係ツリー表示
  - Mermaid形式での出力（図表生成対応）
  - グラフ統計情報の表示（タスク数、依存関係数、最大並列度など）
- クリティカルパスの自動計算
- 並列実行グループの自動生成
- CLIコマンド：`cmw task graph`, `cmw task graph --format mermaid`, `cmw task graph --stats`
- 20個のユニットテスト

#### Phase 8.2: PromptTemplate
- Claude Code用タスク実行プロンプトの自動生成
  - 依存タスク情報の自動埋め込み
  - 受入基準と実装手順の構造化
  - タスクコンテキストの自動収集
- バッチ実行用プロンプトの生成
- レビュー用プロンプトの生成
- Rich UIによる美しい出力フォーマット
- CLIコマンド：`cmw task prompt TASK-XXX`
- 18個のユニットテスト

#### Phase 8.3: StaticAnalyzer
- Pythonコードの静的解析機能（ASTベース）
  - ファイル間の依存関係自動検出
  - sys.path動的変更の検出と対応
  - 相対インポート・絶対インポートの完全サポート
- タスク間依存関係の自動推論
- 循環インポートの検出
- API endpointの自動抽出（FastAPI対応）
- コード複雑度の分析
- 20個のユニットテスト
- todo-apiプロジェクトで実証済み

#### Phase 8.4: InteractiveFixer
- 対話的な問題修正UI
  - 循環依存の対話的修正（Rich Table UI）
  - タスク選択インターフェース
  - 修正提案の表示と適用
  - 不足依存関係の修正
- バリデーション結果の視覚的表示
- 23個のユニットテスト

#### Phase 8.5: ResponseParser
- Claude Code応答の自動解析
  - ファイルパスの自動抽出（日本語・英語対応）
  - タスクID（TASK-XXX）の自動検出
  - 完了キーワードの検出（日英対応）
  - 完了コマンドの自動提案
- エラーメッセージの検出
- 質問の検出
- 応答要約の生成
- 29個のユニットテスト
- todo-apiで実際のワークフローを検証済み

### Improved
- StaticAnalyzer: sys.path動的変更に対応（`sys.path.insert()`パターンを検出）
- StaticAnalyzer: 現在のファイルのディレクトリを検索パスに追加
- StaticAnalyzer: `from X import Y` で Y がサブモジュールの場合も解決
- StaticAnalyzer: 自己参照の除外機能

### Testing
- 総テスト数: 153 → 273（+120テスト）
- 全てのテストがパス

### Documentation
- README.md を v0.3.0 に更新
- Phase 8 の全機能を追加
- CLIコマンドリファレンスを更新

### Validation
- todo-apiプロジェクトで実ワークフロー検証
- TASK-014（認証テスト）の実装を通して全機能を確認
  - プロンプト生成
  - テスト実装
  - ResponseParser動作確認

## [0.2.0] - 2025-XX-XX

### Added

#### Phase 1.4: DependencyValidator
- 循環依存の自動検出と修正
  - NetworkXによる高精度な循環検出
  - セマンティック分析による修正提案
  - 信頼度スコアリング
  - 自動修正機能（信頼度100%で即座に適用）
- 11個のユニットテスト

#### Phase 1.5: TaskFilter
- 非タスク項目の自動除外
  - 「技術スタック」「非機能要件」などを自動判定
  - タスク動詞・受入基準の具体性を評価
- blog-apiで17→15タスクに最適化

#### Phase 2.1: タスク検証コマンド
- `cmw tasks validate`コマンド
  - 循環依存チェック
  - 非タスク項目チェック
  - 依存関係の妥当性チェック（存在しない依存先、自己依存）
  - `--fix`オプションで自動修正
  - Rich UIで視覚的に結果表示
- 9個のユニットテスト

#### Phase 2.2: Git連携
- `cmw sync --from-git`コマンド
  - Gitコミットメッセージから進捗を自動同期
  - `TASK-XXX`パターンの自動検出
  - タスク参照の妥当性検証
  - `--since`, `--branch`, `--dry-run`オプション
- 14個のユニットテスト

### Testing
- 総テスト数: 153
- 全てのテストがパス

### Validation
- blog-apiで実証完了
- todo-apiで実証完了

## [0.1.0] - 2025-XX-XX

### Added

#### Phase 0: 基盤構築
- プロジェクト初期化（`cmw init`）
- タスク定義（tasks.json）
- 依存関係管理
- 進捗管理
- CLI実装

#### Phase 1: タスク管理層
- TaskProvider: タスク情報の提供、コンテキスト構築、状態管理
- StateManager: ロック機構、セッション管理、進捗永続化
- ParallelExecutor: 並列実行判定、ファイル競合検出

#### Phase 3: エラーハンドリング
- ErrorHandler: エラー対応決定、ロールバック、復旧提案

#### Phase 4: フィードバック機能
- FeedbackManager: リアルタイムフィードバック

#### Phase 5: 自動タスク生成
- RequirementsParser: requirements.mdからタスク自動生成
- CLIコマンド: `cmw tasks generate`
- 23個のユニットテスト

#### Phase 6: ファイル競合検出
- ConflictDetector: タスク間のファイル競合を事前検出
- CLIコマンド: `cmw tasks analyze`
- 19個のユニットテスト

#### Phase 7: リアルタイム進捗UI
- ProgressTracker: 進捗メトリクスの計算と追跡
- Dashboard: 美しいターミナルダッシュボード
- CLIコマンド: `cmw status`, `cmw status --compact`
- 12個のユニットテスト

### Documentation
- Claude Code統合ガイド
- 改善計画ドキュメント
- Phase 1実装ガイド

### Validation
- todo-apiプロジェクトで検証完了
  - 17タスク、2000行コード、106テスト
  - 全タスク完了、全テストパス

[0.3.1]: https://github.com/nakishiyaman/cmw/releases/tag/v0.3.1
[0.3.0]: https://github.com/nakishiyaman/cmw/releases/tag/v0.3.0
[0.2.0]: https://github.com/nakishiyaman/cmw/releases/tag/v0.2.0
[0.1.0]: https://github.com/nakishiyaman/cmw/releases/tag/v0.1.0
