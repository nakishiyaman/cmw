# セットアップとデプロイメントガイド

## GitHubへのプッシュ手順

### 1. GitHubでリポジトリを作成

1. GitHub (https://github.com) にログイン
2. 右上の `+` → `New repository` をクリック
3. Repository name: `cmw`
4. Description: `Document-Driven Multi-Agent Development Orchestration Framework`
5. Public または Private を選択
6. **Initialize this repository with a README のチェックを外す**
7. `Create repository` をクリック

### 2. ローカルリポジトリを初期化

```bash
# プロジェクトディレクトリに移動
cd cmw

# Gitリポジトリを初期化
git init

# すべてのファイルを追加
git add .

# 初回コミット
git commit -m "Initial commit: Claude Multi-Worker Framework v0.1.0"
```

### 3. リモートリポジトリに接続

```bash
# リモートリポジトリを追加（URLは自分のものに変更）
git remote add origin https://github.com/yourusername/cmw.git

# デフォルトブランチ名を確認（mainまたはmaster）
git branch -M main

# プッシュ
git push -u origin main
```

## PyPI への公開（オプション）

フレームワークを公開して、`pip install` で利用可能にする場合：

### 1. PyPI アカウント作成

- https://pypi.org/ でアカウントを作成
- API Token を生成

### 2. ビルドツールをインストール

```bash
pip install build twine
```

### 3. パッケージをビルド

```bash
python -m build
```

これで `dist/` ディレクトリに以下が作成されます：
- `claude_multi_worker-0.1.0.tar.gz`
- `claude_multi_worker-0.1.0-py3-none-any.whl`

### 4. TestPyPI でテスト（推奨）

```bash
# TestPyPI にアップロード
twine upload --repository testpypi dist/*

# インストールテスト
pip install --index-url https://test.pypi.org/simple/ claude-multi-worker
```

### 5. PyPI に公開

```bash
twine upload dist/*
```

公開後、誰でも以下でインストール可能：
```bash
pip install claude-multi-worker
```

## GitHub Actions でCI/CD設定

### 1. `.github/workflows/ci.yml` を作成

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    
    - name: Lint with ruff
      run: |
        ruff check src/cmw tests/
    
    - name: Type check with mypy
      run: |
        mypy src/cmw
    
    - name: Test with pytest
      run: |
        pytest tests/ --cov=cmw --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### 2. `.github/workflows/publish.yml` を作成

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

## ドキュメントサイトの作成（オプション）

### MkDocs を使用

```bash
# MkDocs をインストール
pip install mkdocs mkdocs-material

# ドキュメント構造を作成
mkdocs new .

# docs/ ディレクトリにマークダウンファイルを配置

# ローカルでプレビュー
mkdocs serve

# GitHub Pages にデプロイ
mkdocs gh-deploy
```

## リリースプロセス

### バージョンアップ手順

1. **バージョン番号を更新**
   - `src/cmw/__init__.py` の `__version__`
   - `pyproject.toml` の `version`

2. **CHANGELOG を更新**
   ```markdown
   ## [0.2.0] - 2025-10-20
   ### Added
   - 新機能A
   - 新機能B
   
   ### Fixed
   - バグ修正C
   ```

3. **コミットとタグ**
   ```bash
   git add .
   git commit -m "Bump version to 0.2.0"
   git tag v0.2.0
   git push origin main --tags
   ```

4. **GitHub Release を作成**
   - GitHub の Releases ページで新しいリリースを作成
   - Tag: `v0.2.0`
   - Release title: `v0.2.0 - 新機能追加`
   - 説明: CHANGELOGから転記

5. **PyPI に公開**（自動または手動）

## プロジェクト構造の説明

```
cmw/
├── src/
│   └── cmw/                    # メインパッケージ
│       ├── __init__.py         # パッケージ初期化
│       ├── models.py           # データモデル
│       ├── coordinator.py      # Coordinator実装
│       ├── workers.py          # Worker実装
│       ├── utils.py            # ユーティリティ
│       ├── cli.py              # CLIツール
│       └── templates.py        # テンプレート管理
│
├── tests/                      # テストコード
│   ├── test_coordinator.py
│   ├── test_workers.py
│   └── test_utils.py
│
├── docs/                       # ドキュメント（オプション）
│   ├── index.md
│   ├── getting-started.md
│   └── api-reference.md
│
├── .github/                    # GitHub設定
│   └── workflows/
│       ├── ci.yml              # CI/CDパイプライン
│       └── publish.yml         # PyPI公開
│
├── pyproject.toml              # プロジェクト設定
├── requirements.txt            # 依存関係
├── README.md                   # プロジェクト概要
├── LICENSE                     # ライセンス
├── CONTRIBUTING.md             # 貢献ガイド
├── CHANGELOG.md                # 変更履歴
└── .gitignore                  # Git除外設定
```

## 継続的なメンテナンス

### 定期的なタスク

- [ ] 依存関係の更新（月1回）
- [ ] セキュリティ脆弱性チェック
- [ ] Issueへの対応
- [ ] PRのレビュー
- [ ] ドキュメントの更新

### 依存関係の更新

```bash
# 古い依存関係をチェック
pip list --outdated

# 更新
pip install --upgrade <package-name>

# requirements.txt を更新
pip freeze > requirements.txt
```

## トラブルシューティング

### インポートエラー

```bash
# 開発モードで再インストール
pip install -e .
```

### テストが失敗する

```bash
# キャッシュをクリア
pytest --cache-clear

# 詳細出力
pytest -vv
```

### ビルドエラー

```bash
# ビルドキャッシュをクリア
rm -rf build/ dist/ *.egg-info

# 再ビルド
python -m build
```

---

**次のステップ:**
1. GitHubにプッシュ
2. CI/CDを設定
3. 実際のプロジェクトで使用してフィードバック収集
4. コミュニティからのコントリビューションを受け入れ
