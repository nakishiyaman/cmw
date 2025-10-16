# アーカイブドキュメント

このディレクトリには、旧アーキテクチャ（v1.0およびv2.0）のドキュメントが保管されています。

## アーカイブされたファイル

- **ARCHITECTURE.md** - v1.0/v2.0のアーキテクチャ設計
- **CONTRIBUTING.md** - 旧バージョンの貢献ガイド
- **DIRECTORY_LAYOUT.md** - 旧ディレクトリ構造
- **GETTING_STARTED.md** - 旧クイックスタートガイド
- **SETUP.md** - 旧セットアップガイド
- **PHASE_1_2_COMPLETED.md** - Phase 1.2完了レポート

## 現在のアーキテクチャ（v3.0）

現在のアーキテクチャは**Claude Code統合設計**です。最新のドキュメントは以下を参照してください：

- **[README.md](../../README.md)** - プロジェクト概要とクイックスタート
- **[docs/CLAUDE_CODE_INTEGRATION.md](../CLAUDE_CODE_INTEGRATION.md)** - Claude Code統合ガイド
- **[docs/planning/multiworker-framework-plan-v3.md](../planning/multiworker-framework-plan-v3.md)** - アーキテクチャv3.0設計書

## アーキテクチャの変遷

### v1.0: 初期設計
- Claude APIを直接呼び出す実行エンジン
- マルチワーカーによる並列実行

### v2.0: 改善版
- エラーハンドリング強化
- フィードバック機能追加

### v3.0: Claude Code統合（現在）
- **役割分担**: cmw（タスク管理・メタデータ層） + Claude Code（実行層）
- **APIコスト削減**: Claude Codeが自身の機能でコード生成
- **シンプル化**: API呼び出しコードを削除、タスク管理に専念

---

**アーカイブ日**: 2025-10-16
