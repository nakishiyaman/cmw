# タスク管理API - プロジェクト要件書

## 概要
RESTful APIを使用したタスク管理システムを構築します。ユーザー認証機能を備え、各ユーザーが自分のタスクを管理できるシステムです。

## 技術スタック
- **Backend**: Python 3.12+ with FastAPI
- **Database**: SQLite (開発用)
- **ORM**: SQLAlchemy
- **認証**: JWT (python-jose)
- **パスワードハッシュ**: bcrypt (passlib)
- **テスト**: pytest

## 1. データモデル設計

### 1.1 ユーザーモデル (User)
- id: 整数型、主キー、自動採番
- email: 文字列、ユニーク制約、メールアドレス形式
- hashed_password: 文字列、bcryptでハッシュ化
- created_at: 日時型、作成日時
- is_active: ブール型、アクティブフラグ

### 1.2 タスクモデル (Task)
- id: 整数型、主キー、自動採番
- title: 文字列、必須、最大100文字
- description: テキスト、オプション
- is_completed: ブール型、完了フラグ、デフォルトFalse
- priority: 列挙型 (low, medium, high)、デフォルトmedium
- due_date: 日付型、オプション
- user_id: 整数型、外部キー (Userテーブル参照)
- created_at: 日時型、作成日時
- updated_at: 日時型、更新日時

## 2. 認証機能

### 2.1 ユーザー登録
- エンドポイント: POST /auth/register
- リクエストボディ: email, password
- バリデーション:
  - メールアドレス形式チェック
  - パスワード強度チェック（最低8文字）
  - 既存ユーザーの重複チェック
- レスポンス: ユーザー情報（パスワード除く）

### 2.2 ログイン
- エンドポイント: POST /auth/login
- リクエストボディ: email, password
- 処理:
  - 認証情報の検証
  - JWTアクセストークンの発行
  - トークン有効期限: 24時間
- レスポンス: access_token, token_type

### 2.3 パスワードハッシュ化
- bcrypt使用（passlib経由）
- ソルト自動生成
- ハッシュ検証機能

## 3. タスク管理API

### 3.1 タスク一覧取得
- エンドポイント: GET /tasks
- 認証: 必須（JWTトークン）
- クエリパラメータ:
  - completed: ブール型、完了フラグでフィルタ（オプション）
  - priority: 文字列、優先度でフィルタ（オプション）
  - sort_by: 文字列、ソート項目（created_at, due_date, priority）
  - order: 文字列、ソート順（asc, desc）
- レスポンス: ログインユーザーのタスクリスト

### 3.2 タスク詳細取得
- エンドポイント: GET /tasks/{task_id}
- 認証: 必須
- バリデーション: タスクの所有者確認
- レスポンス: タスク詳細情報

### 3.3 タスク作成
- エンドポイント: POST /tasks
- 認証: 必須
- リクエストボディ: title, description (opt), priority (opt), due_date (opt)
- バリデーション:
  - タイトル必須チェック
  - タイトル長チェック（最大100文字）
  - 優先度の有効値チェック
- レスポンス: 作成されたタスク情報

### 3.4 タスク更新
- エンドポイント: PUT /tasks/{task_id}
- 認証: 必須
- バリデーション: タスクの所有者確認
- リクエストボディ: title, description, priority, due_date（全てオプション）
- レスポンス: 更新されたタスク情報

### 3.5 タスク削除
- エンドポイント: DELETE /tasks/{task_id}
- 認証: 必須
- バリデーション: タスクの所有者確認
- レスポンス: 204 No Content

### 3.6 タスク完了切り替え
- エンドポイント: PATCH /tasks/{task_id}/toggle
- 認証: 必須
- バリデーション: タスクの所有者確認
- 処理: is_completedフラグの反転
- レスポンス: 更新されたタスク情報

## 4. エラーハンドリング

### 4.1 HTTPステータスコード
- 200 OK: 成功
- 201 Created: リソース作成成功
- 204 No Content: 削除成功
- 400 Bad Request: バリデーションエラー
- 401 Unauthorized: 認証エラー
- 403 Forbidden: 権限エラー
- 404 Not Found: リソース未検出
- 422 Unprocessable Entity: データ検証エラー
- 500 Internal Server Error: サーバーエラー

### 4.2 エラーレスポンス形式
```json
{
  "detail": "エラーメッセージ"
}
```

## 5. テスト要件

### 5.1 ユニットテスト
- モデルのバリデーションテスト
- パスワードハッシュ化・検証テスト
- JWT生成・検証テスト

### 5.2 統合テスト
- 各APIエンドポイントのテスト
- 認証フローのテスト
- エラーケースのテスト

### 5.3 テストカバレッジ
- 目標: 80%以上

## 6. セキュリティ要件

### 6.1 認証・認可
- JWTトークンによる認証
- パスワードのハッシュ化（平文保存禁止）
- ユーザー所有権の検証

### 6.2 入力検証
- SQLインジェクション対策（ORM使用）
- XSS対策（適切なエスケープ）
- 入力値のバリデーション

## 7. パフォーマンス要件
- APIレスポンスタイム: 平均200ms以内
- データベースクエリの最適化
- N+1問題の回避

## 8. ドキュメント要件
- OpenAPI (Swagger) 自動生成
- README.md（セットアップ手順）
- API使用例
