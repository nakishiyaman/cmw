# ディレクトリ配置ガイド

このドキュメントでは、Claude Multi-Worker Framework（ツール）と、実際の開発プロジェクトの配置関係を詳しく説明します。

## 🎯 重要な原則

### フレームワーク ≠ プロジェクト

```
フレームワーク（ツール）    プロジェクト（開発する場所）
        ↓                           ↓
  このリポジトリ              cmw init で作成
  1箇所だけ                   複数作れる
  再利用可能                  独立している
```

**簡単な例え：**
- **フレームワーク** = Wordアプリ本体（1つインストール）
- **プロジェクト** = Word文書ファイル（何個でも作れる）

## 📁 全体構造

### 推奨配置A: すべて同じ階層

```
~/workspace/
│
├── 📦 cmw/    # フレームワーク（このリポジトリ）
│   ├── src/cmw/                         # Pythonパッケージ
│   │   ├── coordinator.py
│   │   ├── workers.py
│   │   ├── cli.py
│   │   └── ...
│   ├── tests/
│   ├── pyproject.toml
│   ├── README.md
│   └── .git/                            # Gitリポジトリ1
│
└── 📂 my-projects/                      # プロジェクト置き場
    │
    ├── 📁 ecommerce-site/               # プロジェクト1
    │   ├── shared/
    │   │   ├── docs/
    │   │   │   ├── requirements.md      # ← あなたが編集
    │   │   │   ├── api-specification.yaml
    │   │   │   └── ...
    │   │   ├── coordination/
    │   │   │   ├── tasks.json           # ← 自動生成
    │   │   │   ├── progress.json
    │   │   │   └── ...
    │   │   └── artifacts/
    │   │       ├── frontend/            # ← 生成されたコード
    │   │       ├── backend/
    │   │       └── ...
    │   ├── workers-config.yaml          # ← あなたが設定
    │   ├── README.md
    │   └── .git/                        # Gitリポジトリ2
    │
    ├── 📁 ml-pipeline/                  # プロジェクト2
    │   ├── shared/
    │   ├── workers-config.yaml
    │   └── .git/                        # Gitリポジトリ3
    │
    └── 📁 data-analytics/               # プロジェクト3
        └── ...
```

### 推奨配置B: 場所を分ける

```
~/tools/
└── 📦 cmw/    # フレームワーク

~/work/
├── 📂 client-a/
│   ├── ecommerce-site/                  # プロジェクト1
│   └── admin-panel/                     # プロジェクト2
│
└── 📂 client-b/
    └── data-pipeline/                   # プロジェクト3

~/personal/
└── 📂 side-projects/
    └── my-app/                          # プロジェクト4
```

### 推奨配置C: グローバルインストール

```bash
# フレームワークをシステム全体にインストール
cd cmw
pip install .  # -e なしで永続インストール

# その後、フレームワークのディレクトリは削除してもOK
# cmw コマンドは残る
```

```
~/anywhere/
├── 📁 project-a/    # どこでもプロジェクト作成可能
├── 📁 project-b/
└── 📁 project-c/
```

## 🚀 実際の使い方

### 初回セットアップ（1回だけ）

```bash
# ステップ1: フレームワークを配置
cd ~/workspace  # または好きな場所
# cmw/ をここに配置

# ステップ2: インストール
cd cmw
python -m venv venv           # 仮想環境（推奨）
source venv/bin/activate      # 有効化
pip install -e .              # 開発モードでインストール

# ステップ3: 確認
cmw --version
# → "cmw, version 0.1.0"

# これでシステム全体で cmw が使える！
```

### プロジェクトを作成（プロジェクトごと）

```bash
# ステップ1: プロジェクト置き場に移動
cd ~/workspace/my-projects  # フレームワークの外！

# ステップ2: プロジェクト作成
cmw init ecommerce-site --template web-app

# ステップ3: 確認
cd ecommerce-site
ls -la
# → shared/ workers-config.yaml README.md
```

### 開発作業

```bash
# プロジェクトディレクトリで作業
cd ~/workspace/my-projects/ecommerce-site

# 要件を書く
vim shared/docs/requirements.md

# Coordinator起動
cmw start

# 別ターミナルで進捗確認
cmw status
```

## 🔄 Git管理

### フレームワーク（1つのリポジトリ）

```bash
cd ~/workspace/cmw

# 初回
git init
git add .
git commit -m "Initial framework"
git remote add origin https://github.com/you/cmw.git
git push -u origin main

# 更新があったとき
git add .
git commit -m "Add new feature"
git push
```

**他のマシンで使う：**
```bash
git clone https://github.com/you/cmw.git
cd cmw
pip install -e .
```

### プロジェクト（複数の独立したリポジトリ）

```bash
# プロジェクト1
cd ~/workspace/my-projects/ecommerce-site
git init
git add .
git commit -m "Initial project setup"
git remote add origin https://github.com/you/ecommerce-site.git
git push -u origin main

# プロジェクト2
cd ~/workspace/my-projects/ml-pipeline
git init
# ... (同様に独立して管理)
```

## ⚠️ よくある間違い

### ❌ やってはいけないこと

```bash
# ❌ フレームワークの中にプロジェクトを作る
cd cmw
cmw init my-project  # ← ダメ！

# ❌ プロジェクトをフレームワークのサブディレクトリに
cmw/
└── my-project/  # ← ダメ！

# ❌ フレームワークをプロジェクトにコピー
cp -r cmw/ my-project/tools/  # ← ダメ！
```

### ✅ 正しい方法

```bash
# ✅ フレームワークの外で作成
cd ~/my-projects  # 完全に別の場所
cmw init my-project

# ✅ 任意の場所でOK
cd /tmp
cmw init test-project

cd ~/Desktop
cmw init another-project
```

## 📊 ファイルの役割分担

### フレームワークのファイル（編集しない）

```
cmw/
├── src/cmw/
│   ├── coordinator.py        # ← 編集しない（フレームワークのコア）
│   ├── workers.py            # ← 編集しない
│   └── ...
```

**あなたが触るのは：**
- フレームワークの機能追加や改善をする場合のみ
- 通常の開発では触らない

### プロジェクトのファイル（編集する）

```
ecommerce-site/
├── shared/docs/
│   ├── requirements.md       # ← あなたが書く
│   ├── api-specification.yaml # ← あなたが書く
│   └── ...
├── workers-config.yaml       # ← あなたが設定
└── README.md                 # ← あなたが書く
```

**あなたが触るのは：**
- ドキュメント（docs/）
- ワーカー設定（workers-config.yaml）
- プロジェクトのREADME

**自動生成されるもの：**
```
├── shared/coordination/
│   ├── tasks.json            # ← Coordinatorが生成
│   ├── progress.json         # ← Coordinatorが更新
│   └── decisions-log.json    # ← Coordinatorが記録
└── shared/artifacts/         # ← Workerが生成
```

## 🎓 理解度チェック

以下の質問に答えられますか？

1. **Q: フレームワークは何個必要？**
   - A: 1個だけ。どこでも使い回せる

2. **Q: プロジェクトは何個作れる？**
   - A: 何個でも。それぞれ独立している

3. **Q: cmw init はどこで実行する？**
   - A: フレームワークの外の任意の場所

4. **Q: フレームワークとプロジェクトは同じGitリポジトリ？**
   - A: 違う。それぞれ別のリポジトリ

5. **Q: 新しいマシンでプロジェクトを開発するには？**
   - A: ①フレームワークをcloneしてインストール、②プロジェクトをclone

## 🔗 関連ドキュメント

- [README.md](README.md) - 基本的な使い方
- [ARCHITECTURE.md](ARCHITECTURE.md) - フレームワークの内部構造
- [SETUP.md](SETUP.md) - GitHubへのプッシュ方法

## 💡 まとめ

```
┌─────────────────────────────────────┐
│ フレームワーク (Tool)                │
│ - 1箇所にインストール                │
│ - システム全体で cmw コマンド使用   │
│ - 複数プロジェクトで再利用           │
└─────────────────────────────────────┘
              ↓ creates
┌─────────────────────────────────────┐
│ プロジェクト (Workspace)             │
│ - 任意の場所に複数作成可能           │
│ - それぞれ独立したGitリポジトリ      │
│ - 実際の開発はここで行う             │
└─────────────────────────────────────┘
```

**この分離により：**
- ✅ フレームワークの更新が全プロジェクトに反映
- ✅ プロジェクトごとに独立して管理
- ✅ チームでの共有が容易
- ✅ 複数プロジェクトの並行開発が可能

---

まだ不明な点があれば、遠慮なくIssueで質問してください！
