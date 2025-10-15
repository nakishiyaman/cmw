# Contributing to Claude Multi-Worker Framework

まず、このプロジェクトへの貢献を検討していただきありがとうございます！

## 開発環境のセットアップ

### 1. リポジトリをフォーク・クローン

```bash
git clone https://github.com/yourusername/claude-multi-worker-framework.git
cd claude-multi-worker-framework
```

### 2. 仮想環境を作成

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 開発用の依存関係をインストール

```bash
pip install -e ".[dev]"
```

## 開発ワークフロー

### 1. ブランチを作成

```bash
git checkout -b feature/your-feature-name
```

ブランチ命名規則:
- `feature/`: 新機能
- `fix/`: バグ修正
- `docs/`: ドキュメント
- `refactor/`: リファクタリング

### 2. コードを書く

- PEP 8 スタイルガイドに従う
- 型ヒントを使用する
- ドキュメント文字列を書く

### 3. テストを実行

```bash
# すべてのテスト
pytest

# カバレッジ付き
pytest --cov=cmw tests/

# 特定のテスト
pytest tests/test_coordinator.py
```

### 4. コードフォーマット

```bash
# フォーマット
black src/cmw tests/

# リント
ruff check src/cmw tests/

# 型チェック
mypy src/cmw
```

### 5. コミット

コミットメッセージの規則:
```
<type>: <subject>

<body>

<footer>
```

例:
```
feat: Coordinatorに進捗ダッシュボード機能を追加

- リアルタイム進捗表示
- ワーカーステータスの可視化
- ブロッカー検出の強化

Closes #123
```

Types:
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント
- `style`: フォーマット
- `refactor`: リファクタリング
- `test`: テスト
- `chore`: ビルド、設定等

### 6. プッシュとPR

```bash
git push origin feature/your-feature-name
```

GitHubでPull Requestを作成。

## コーディングスタンダード

### Pythonスタイル

```python
# Good
def calculate_progress(completed: int, total: int) -> str:
    """進捗率を計算
    
    Args:
        completed: 完了数
        total: 全体数
    
    Returns:
        パーセンテージ文字列 (例: "75%")
    """
    if total == 0:
        return "0%"
    return f"{int(completed / total * 100)}%"


# Bad
def calc(c, t):
    return f"{int(c/t*100)}%"
```

### ドキュメント

- すべての公開API にドキュメント文字列
- 複雑なロジックにコメント
- READMEとwikiを更新

### テスト

- 新機能には必ずテストを追加
- 既存のテストを壊さない
- エッジケースをカバー

```python
def test_coordinator_initialization():
    """Coordinatorが正しく初期化されるかテスト"""
    coordinator = Coordinator(Path("test_project"))
    assert coordinator.config is not None
    assert len(coordinator.workers) > 0
```

## プルリクエストのガイドライン

### PRを作成する前に

- [ ] すべてのテストが通る
- [ ] コードがフォーマットされている
- [ ] 型チェックが通る
- [ ] ドキュメントが更新されている
- [ ] CHANGELOGに追加されている

### PR説明

良いPR説明:
```
## 概要
Coordinatorに進捗ダッシュボード機能を追加

## 変更内容
- リアルタイム進捗表示を実装
- Richライブラリを使用したUI
- WebSocketサポート（オプション）

## テスト
- ユニットテスト追加: test_dashboard.py
- 手動テスト: ダッシュボードが正常に表示されることを確認

## スクリーンショット
[スクリーンショットを添付]

## 関連Issue
Closes #123
```

## バグレポート

バグを見つけた場合:

1. 既存のIssueを確認
2. 新しいIssueを作成:
   - 明確なタイトル
   - 再現手順
   - 期待される動作
   - 実際の動作
   - 環境情報

テンプレート:
```
### バグの説明
簡潔に説明

### 再現手順
1. ...
2. ...
3. ...

### 期待される動作
...

### 実際の動作
...

### 環境
- OS: 
- Python: 
- Framework version: 
```

## 機能リクエスト

新機能の提案:

1. Discussionsで議論を開始
2. 承認されたらIssueを作成
3. 実装を開始

## コミュニティ

- GitHub Discussions: 質問・議論
- GitHub Issues: バグ・機能リクエスト
- Discord: リアルタイムチャット（将来的に）

## ライセンス

コントリビューションは MIT License の下で公開されます。

---

ありがとうございます！ 🎉
