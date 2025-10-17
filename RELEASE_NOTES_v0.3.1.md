# v0.3.1 - Claude Code Integration Release

**リリース日**: 2025年10月17日

## 🎉 主要機能

### Claude Code統合 - Requirements自動生成
Claude Codeと連携してrequirements.mdを効率的に生成できるようになりました。

```bash
# ワンライナーでプロンプト生成
cmw requirements generate --with-claude --prompt "Blog API with authentication"

# 対話形式で詳細入力
cmw requirements generate
```

### 自動タスク生成と循環依存解決
requirements.mdから実装タスクを自動生成し、循環依存を自動修正します。

```bash
cmw task generate
```

### Git統合とコミット管理
タスク完了時に自動的にGitコミットを作成できます。

```bash
cmw task complete <task-id> --commit
```

### 進捗可視化
リアルタイムで進捗状況を確認できます。

```bash
cmw status
cmw status --tree  # 依存関係ツリー表示
```

## 🔧 技術仕様

- **Python**: 3.9以上
- **依存関係**: click, rich, networkx
- **テストカバレッジ**: 288テスト全てパス
- **検証済み環境**: 実プロジェクトで動作確認済み

## 📦 インストール

### PyPIから（推奨）
```bash
pip install claude-multi-worker
```

### GitHubから
```bash
pip install git+https://github.com/nakishiyaman/cmw.git
```

### ソースから
```bash
git clone https://github.com/nakishiyaman/cmw.git
cd cmw
pip install -e .
```

## 🚀 クイックスタート

```bash
# 1. プロジェクト初期化
cmw init --name my-project

# 2. Requirements生成（Claude Code統合）
cmw requirements generate --with-claude --prompt "Your project idea"

# 3. Claude Codeでrequirements.md作成
# （.cmw_prompt.mdをClaude Codeに渡す）

# 4. タスク自動生成
cmw task generate

# 5. 次のタスクを取得
cmw task next

# 6. タスク完了
cmw task complete <task-id> --commit
```

## 📚 ドキュメント

- **README**: https://github.com/nakishiyaman/cmw/blob/main/README.md
- **Wiki**: https://github.com/nakishiyaman/cmw/wiki
- **Issues**: https://github.com/nakishiyaman/cmw/issues

## 🛠️ 主な変更点

### 新機能
- ✨ Claude Code統合によるrequirements.md自動生成 (fe76938)
- ✨ 対話形式のrequirements生成ウィザード (fe76938)
- ✨ requirements.mdテンプレートの自動出力 (fe76938)

### 改善
- 📝 デモGIF更新 - 新ワークフロー対応 (e3bb920)
- 🔧 リポジトリ名短縮: claude-multi-worker-framework → cmw (d3eec33)
- 🔒 個人情報削除とセキュリティ監査完了 (c616691, 4841c06)

### バグ修正
- 🐛 デモGIFの文字化け修正 - UTF-8/絵文字フォント対応 (98956b5, 18841fd)
- 🐛 ホームディレクトリパスの完全除去 (2960817, 507e093)

## 🚧 次期バージョン予告（v0.4.0）

### MCP (Model Context Protocol) 統合
Claude Codeとのシームレスな統合を実現します。

- 🔌 MCP Server実装
  - `get_next_task()`, `complete_task()` などのTools
  - タスク一覧、進捗状況などのResources

- 📦 Claude Code Plugin化
  - ワンコマンドインストール: `/plugin install cmw`
  - スラッシュコマンド: `/next-task`, `/complete-task`

- ⚡ ワークフロー自動化
  - Claude Codeが自動的にタスクを取得・完了マーク
  - 手動コマンド実行不要

**リリース予定**: 2025年11月中旬
**進捗追跡**: https://github.com/nakishiyaman/cmw/issues

## 🙏 謝辞

cmwを使っていただきありがとうございます。フィードバックやバグ報告は[GitHub Issues](https://github.com/nakishiyaman/cmw/issues)までお願いします。

## 📄 ライセンス

MIT License - Copyright (c) 2025 Nakishiyama
