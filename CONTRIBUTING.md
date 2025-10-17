# Contributing to Claude Multi-Worker Framework (cmw)

まず、このプロジェクトへの貢献を検討していただき、ありがとうございます！

このドキュメントでは、プロジェクトへの貢献方法について説明します。

## 🚀 開発環境のセットアップ

### 1. リポジトリをフォーク

GitHubで[cmwリポジトリ](https://github.com/nakishiyaman/claude-multi-worker-framework)をフォークしてください。

### 2. ローカルにクローン

```bash
git clone https://github.com/<your-username>/claude-multi-worker-framework.git
cd claude-multi-worker-framework
```

### 3. 仮想環境を作成

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows
```

### 4. 依存パッケージをインストール

```bash
# 本番依存関係
pip install -r requirements.txt

# 開発依存関係を含めてインストール
pip install -e .[dev]
```

### 5. テストを実行して動作確認

```bash
pytest tests/ -v
```

全てのテストが通れば、開発環境のセットアップは完了です！

## 📝 コード規約

### Python コードスタイル

- **フォーマッター**: Black (line-length=100)
- **リンター**: Ruff
- **型チェック**: mypy（型ヒントを必須とします）

コードを書いた後、以下を実行してください：

```bash
# フォーマット
black src/ tests/

# リント
ruff check src/ tests/

# 型チェック
mypy src/
```

### コミットメッセージ

コミットメッセージは[Conventional Commits](https://www.conventionalcommits.org/)に従ってください：

```
<type>(<scope>): <subject>

<body>
```

**Type:**
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント変更のみ
- `style`: コードの意味に影響しない変更（空白、フォーマット等）
- `refactor`: リファクタリング
- `test`: テストの追加・修正
- `chore`: ビルドプロセスやツールの変更

**例:**
```
feat(parser): requirements.mdのネストセクション対応

複数レベルのネストされたセクションを正しく解析できるようになりました。

- セクション深度の計算を追加
- 親セクションの参照を保持
- 20個の新規テストを追加
```

## 🧪 テスト

### テストの実行

```bash
# 全テスト実行
pytest tests/ -v

# カバレッジ付き
pytest tests/ -v --cov=src/cmw --cov-report=term

# 特定のテストファイルのみ
pytest tests/test_task_provider.py -v
```

### テストの追加

新機能やバグ修正には、必ずテストを追加してください：

1. `tests/`ディレクトリに`test_<module_name>.py`を作成
2. テスト関数は`test_`で始める
3. エッジケースを含む複数のテストケースを書く
4. カバレッジ85%以上を目指す

**例:**
```python
# tests/test_new_feature.py

import pytest
from cmw.new_feature import NewFeature

def test_new_feature_basic():
    """基本的な動作のテスト"""
    feature = NewFeature()
    result = feature.process("input")
    assert result == "expected_output"

def test_new_feature_edge_case():
    """エッジケースのテスト"""
    feature = NewFeature()
    with pytest.raises(ValueError):
        feature.process(None)
```

## 🔧 プルリクエストの作成

### 1. ブランチを作成

```bash
git checkout -b feature/your-feature-name
# または
git checkout -b fix/your-bug-fix
```

### 2. 変更をコミット

```bash
git add .
git commit -m "feat(scope): your feature description"
```

### 3. プッシュ

```bash
git push origin feature/your-feature-name
```

### 4. プルリクエストを作成

GitHubでプルリクエストを作成してください。以下を含めてください：

- **タイトル**: 簡潔で分かりやすいタイトル
- **説明**:
  - 何を変更したか
  - なぜ変更したか
  - どのようにテストしたか
- **Issue番号**: 関連するIssueがあれば`Closes #123`のように記載

**プルリクエストのチェックリスト:**
- [ ] テストが全て通る（`pytest tests/ -v`）
- [ ] コードがフォーマットされている（`black src/ tests/`）
- [ ] リントエラーがない（`ruff check src/ tests/`）
- [ ] 型チェックが通る（`mypy src/`）
- [ ] 新機能には適切なテストが追加されている
- [ ] ドキュメントが更新されている（必要に応じて）

## 🐛 バグ報告

バグを発見した場合、[GitHubのIssues](https://github.com/nakishiyaman/claude-multi-worker-framework/issues)で報告してください。

**含めるべき情報:**
- **タイトル**: 簡潔で分かりやすいタイトル
- **説明**:
  - バグの詳細な説明
  - 再現手順
  - 期待される動作
  - 実際の動作
- **環境情報**:
  - OS（Linux, macOS, Windows）
  - Pythonバージョン（`python --version`）
  - cmwバージョン（`cmw --version`）
- **エラーメッセージ**: 該当する場合
- **スクリーンショット**: 該当する場合

**例:**
```markdown
## バグの説明
`cmw tasks generate`を実行すると、requirements.mdのネストセクションが正しく解析されない。

## 再現手順
1. requirements.mdに3レベル以上のネストセクションを作成
2. `cmw tasks generate`を実行
3. tasks.jsonを確認

## 期待される動作
全てのセクションが正しくタスクとして生成される。

## 実際の動作
3レベル目以降のセクションが無視される。

## 環境
- OS: Ubuntu 22.04
- Python: 3.11.5
- cmw: 0.3.1
```

## 💡 機能リクエスト

新機能のアイデアがある場合、[GitHubのIssues](https://github.com/nakishiyaman/claude-multi-worker-framework/issues)で提案してください。

**含めるべき情報:**
- **タイトル**: 簡潔で分かりやすいタイトル
- **説明**:
  - 機能の詳細な説明
  - なぜこの機能が必要か
  - どのように使うか（ユースケース）
  - 実装のアイデア（あれば）

## 📚 ドキュメントへの貢献

ドキュメントの改善も大歓迎です！

- README.mdの改善
- ドキュメントの追加（`docs/`ディレクトリ）
- コードコメントの改善
- 例の追加

## ❓ 質問

質問がある場合：
1. まず[README.md](README.md)と[ドキュメント](docs/)を確認
2. [GitHubのIssues](https://github.com/nakishiyaman/claude-multi-worker-framework/issues)で既存の議論を検索
3. 見つからない場合、新しいIssueを作成

## 🙏 行動規範

このプロジェクトは[Contributor Covenant](CODE_OF_CONDUCT.md)の行動規範を採用しています。参加することで、この規範を守ることに同意したものとみなされます。

## 📄 ライセンス

貢献したコードは、プロジェクトと同じMITライセンスでライセンスされます。

---

貢献してくださり、ありがとうございます！一緒にcmwをより良いツールにしていきましょう。
