# Security Policy

## Supported Versions

現在サポートされているバージョン:

| Version | Supported          |
| ------- | ------------------ |
| 0.3.x   | :white_check_mark: |
| 0.2.x   | :white_check_mark: |
| < 0.2   | :x:                |

## Reporting a Vulnerability

セキュリティ脆弱性を発見した場合は、以下の方法で報告してください：

### 報告方法

1. **非公開報告（推奨）**: noreply@example.com にメールで報告
2. **GitHub Security Advisory**: [こちら](https://github.com/nakishiyaman/claude-multi-worker-framework/security/advisories/new)から報告

### 含めるべき情報

- 脆弱性の詳細な説明
- 再現手順
- 影響範囲（どのバージョンに影響するか）
- 可能であれば、修正案

### 対応プロセス

1. **24時間以内**: 報告の受領確認
2. **7日以内**: 脆弱性の確認と影響範囲の評価
3. **30日以内**: 修正版のリリース（深刻度による）

## セキュリティ対策

### 現在の対策

1. **ファイル操作の制限**
   - プロジェクトディレクトリ内のファイルのみ操作
   - パストラバーサル攻撃の防止

2. **コマンド実行の制限**
   - Gitコマンドのみを許可
   - リスト形式でsubprocess.run()を使用（シェルインジェクション防止）

3. **入力検証**
   - タスクIDのパターンマッチング（`TASK-\d{3}`）
   - JSONスキーマバリデーション

4. **機密情報の保護**
   - ハードコードされた秘密情報なし
   - 環境変数からの読み込みを推奨

### 既知の制限事項

1. **Git連携**
   - `branch`と`since`パラメータのバリデーションは限定的
   - 信頼できる入力元からの使用を前提

2. **ファイルパーミッション**
   - プロジェクトディレクトリの読み書き権限が必要
   - マルチユーザー環境では適切な権限設定が必要

## Best Practices

### ユーザー向け

1. **プロジェクトディレクトリの保護**
   ```bash
   chmod 700 my-project/
   ```

2. **信頼できるrequirements.mdのみ使用**
   - 第三者が作成したrequirements.mdを使用する場合は内容を確認

3. **定期的なアップデート**
   ```bash
   pip install --upgrade claude-multi-worker
   ```

### 開発者向け

1. **依存関係の脆弱性チェック**
   ```bash
   pip install safety
   safety check -r requirements.txt
   ```

2. **静的解析ツールの使用**
   ```bash
   bandit -r src/
   ```

3. **テストの実行**
   ```bash
   pytest tests/ -v
   ```

## 謝辞

セキュリティ脆弱性を報告してくださった方々に感謝します。

---

最終更新: 2025-10-17
