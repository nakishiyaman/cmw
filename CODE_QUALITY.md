# Code Quality Improvement Tracking

## 概要

このドキュメントは、コードの品質改善項目を追跡します。

## ✅ 完了項目

### v0.5.1 Phase 1: Lint/Format修正 (2025-10-18)

- **Auto-fix lint errors**: 42件のlintエラーを修正 (W293, C414)
- **Code formatting**: 21ファイルにruff formatを適用
- **Line length**: E501エラー (100文字超過) を全て修正
- **PR**: #14 - 全CI checks passed ✅

## 🚧 改善が必要な項目

### 1. 関数の複雑度 (C901)

以下の関数が複雑度10を超えており、リファクタリングが推奨されます:

#### 最優先 (Complexity > 15)

1. **`validate_tasks`** (complexity: 19)
   - ファイル: `src/cmw/cli.py:331`
   - 理由: 検証ロジックが1つの関数に集中
   - 提案: 以下に分割
     - `_validate_circular_dependencies()` - 循環依存チェック
     - `_validate_non_task_items()` - 非タスク項目チェック
     - `_validate_dependency_validity()` - 依存関係妥当性チェック
     - `_show_validation_summary()` - サマリー表示

2. **`_generate_markdown`** (complexity: 19)
   - ファイル: `src/cmw/requirements_generator.py:299`
   - 理由: Markdown生成ロジックが1つの関数に集中
   - 提案: 以下に分割
     - `_generate_header()` - ヘッダー生成
     - `_generate_tech_stack_section()` - 技術スタック
     - `_generate_data_models_section()` - データモデル
     - `_generate_api_features_section()` - API機能
     - `_generate_non_functional_section()` - 非機能要件

3. **`_infer_target_files`** (complexity: 17)
   - ファイル: `src/cmw/requirements_parser.py:220`
   - 理由: ファイル推論ロジックが複雑
   - 提案: パターンマッチング部分を別関数に分離

#### 高優先度 (Complexity 14-15)

4. **`sync`** (complexity: 14)
   - ファイル: `src/cmw/cli.py:793`
   - 理由: Git同期ロジックとUI表示が混在
   - 提案: ロジックとUIを分離

5. **`_load_tasks`** (complexity: 14)
   - ファイル: `src/cmw/coordinator.py:32`
   - 理由: タスク読み込みと状態マージが複雑
   - 提案: JSONパース、状態マージ、バリデーションを分離

6. **`parse`** (complexity: 14)
   - ファイル: `src/cmw/requirements_parser.py:25`
   - 理由: Markdown解析ロジックが複雑
   - 提案: セクション抽出、タスク生成、依存関係推論を分離

7. **`_infer_dependencies`** (complexity: 14)
   - ファイル: `src/cmw/requirements_parser.py:367`
   - 理由: 依存関係推論ロジックが複雑
   - 提案: ルールベース推論を別関数に分離

#### 中優先度 (Complexity 11-13)

8. **`get_task_summary`** (complexity: 12)
   - ファイル: `src/cmw/feedback.py:258`
   - 理由: タスクサマリー生成が複雑
   - 提案: フォーマット処理を分離

9. **`_extract_sections`** (complexity: 11)
   - ファイル: `src/cmw/requirements_parser.py:102`
   - 理由: Markdownセクション抽出ロジックが複雑
   - 提案: ヘッダー解析を別関数に分離

10. **`analyze_file_dependencies`** (complexity: 11)
    - ファイル: `src/cmw/static_analyzer.py:25`
    - 理由: AST解析ロジックが複雑
    - 提案: インポート抽出を別関数に分離

11. **`infer_task_dependencies`** (complexity: 11)
    - ファイル: `src/cmw/static_analyzer.py:232`
    - 理由: タスク依存関係推論が複雑
    - 提案: ファイル依存関係マッピングを分離

12. **`detect_circular_imports`** (complexity: 11)
    - ファイル: `src/cmw/static_analyzer.py:292`
    - 理由: 循環インポート検出が複雑
    - 提案: グラフトラバーサルを別関数に分離

### リファクタリング指針

1. **単一責任の原則**: 各関数は1つの責任のみを持つ
2. **抽出メソッドパターン**: 長い関数は意味のある単位で分割
3. **早期リターン**: ネストを減らすため、早期リターンを活用
4. **戦略パターン**: 複雑な条件分岐はポリモーフィズムで置き換え

### 影響範囲の評価

- **テストカバレッジ**: 現在288テスト
- **リファクタリング前**: 全テストがパスすることを確認
- **リファクタリング後**: 既存の動作を保証するためテストを再実行
- **優先順位**: 変更頻度が高く、バグリスクが高い関数から着手

## 次のステップ

1. ✅ Phase 1完了: Lint/Format修正
2. 📝 Phase 2準備中: ドキュメント整備
   - MYPY_IMPROVEMENTS.md 作成
   - CONTRIBUTING.md 更新
3. ⏳ Phase 3計画中: テストカバレッジ向上
   - 現在のカバレッジ測定
   - 90%目標に向けたテスト追加

## 参考資料

- [Ruff Rules Documentation](https://docs.astral.sh/ruff/rules/)
- [PEP 8 - Style Guide for Python Code](https://pep8.org/)
- [Refactoring: Improving the Design of Existing Code](https://refactoring.com/)
