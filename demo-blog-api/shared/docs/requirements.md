# Blog API プロジェクト要件書

## 1. プロジェクト概要
FastAPIを使用したシンプルなブログ記事管理REST API

## 2. データモデル

### 2.1 記事（Article）モデル定義
- id: UUID（自動生成）
- title: 文字列（必須、最大200文字）
- content: 文字列（必須）
- author: 文字列（必須）
- created_at: 日時（自動生成）
- updated_at: 日時（自動更新）
- published: 真偽値（デフォルト: False）

**対象ファイル**: `shared/artifacts/backend/models.py`

**受入基準**:
- Pydanticモデルとして定義
- バリデーション設定を含む
- テストコードが存在する

## 3. データベース

### 3.1 データベース接続設定
- SQLiteを使用
- 接続プール設定
- マイグレーション対応

**対象ファイル**: `shared/artifacts/backend/database.py`

**受入基準**:
- SQLAlchemy ORMを使用
- テーブル自動作成機能
- トランザクション管理

### 3.2 記事テーブルスキーマ定義
- Articleモデルに対応するテーブル
- インデックス設定

**対象ファイル**: `shared/artifacts/backend/database.py`

**受入基準**:
- SQLAlchemyで定義
- 適切なカラム型

**依存タスク**: 2.1

## 4. APIエンドポイント

### 4.1 記事作成API（POST /articles）
- リクエスト: title, content, author
- レスポンス: 作成された記事情報
- ステータスコード: 201

**対象ファイル**: `shared/artifacts/backend/routers/articles.py`

**受入基準**:
- バリデーションエラー処理
- 作成日時の自動設定
- テストコードが存在する

**依存タスク**: 2.1, 3.1, 3.2

### 4.2 記事一覧取得API（GET /articles）
- クエリパラメータ: page, limit, published
- レスポンス: 記事リスト、総件数
- ページネーション対応

**対象ファイル**: `shared/artifacts/backend/routers/articles.py`

**受入基準**:
- フィルタリング機能
- ページネーション実装
- テストコードが存在する

**依存タスク**: 2.1, 3.1, 3.2

### 4.3 記事詳細取得API（GET /articles/{id}）
- パスパラメータ: id（UUID）
- レスポンス: 記事詳細情報
- ステータスコード: 200 or 404

**対象ファイル**: `shared/artifacts/backend/routers/articles.py`

**受入基準**:
- 存在しない記事への対応
- テストコードが存在する

**依存タスク**: 2.1, 3.1, 3.2

### 4.4 記事更新API（PUT /articles/{id}）
- パスパラメータ: id（UUID）
- リクエスト: title, content, published
- レスポンス: 更新後の記事情報

**対象ファイル**: `shared/artifacts/backend/routers/articles.py`

**受入基準**:
- 部分更新対応
- updated_atの自動更新
- テストコードが存在する

**依存タスク**: 2.1, 3.1, 3.2

### 4.5 記事削除API（DELETE /articles/{id}）
- パスパラメータ: id（UUID）
- レスポンス: なし
- ステータスコード: 204

**対象ファイル**: `shared/artifacts/backend/routers/articles.py`

**受入基準**:
- 論理削除または物理削除
- テストコードが存在する

**依存タスク**: 2.1, 3.1, 3.2

## 5. アプリケーション設定

### 5.1 FastAPIアプリケーション初期化
- CORSミドルウェア設定
- ルーター登録
- 起動時のデータベース初期化

**対象ファイル**: `shared/artifacts/backend/main.py`

**受入基準**:
- 全ルーターが登録されている
- OpenAPIドキュメント生成
- テストコードが存在する

**依存タスク**: 4.1, 4.2, 4.3, 4.4, 4.5

### 5.2 環境設定ファイル
- データベースURL
- CORSオリジン設定
- その他環境変数

**対象ファイル**: `shared/artifacts/backend/config.py`

**受入基準**:
- pydantic-settingsを使用
- .envファイル対応

## 6. テスト

### 6.1 モデルテスト
- Articleモデルのバリデーションテスト
- フィールド制約テスト

**対象ファイル**: `shared/artifacts/tests/test_models.py`

**受入基準**:
- 正常系・異常系のテスト
- カバレッジ80%以上

**依存タスク**: 2.1

### 6.2 APIエンドポイントテスト
- 各エンドポイントの統合テスト
- エラーケースのテスト

**対象ファイル**: `shared/artifacts/tests/test_api.py`

**受入基準**:
- pytest-asyncioを使用
- 全エンドポイントのテスト
- カバレッジ80%以上

**依存タスク**: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1

## 7. ドキュメント

### 7.1 README作成
- プロジェクト概要
- セットアップ手順
- API使用例
- テスト実行方法

**対象ファイル**: `README.md`

**受入基準**:
- 初見の開発者が理解できる
- コードサンプル付き

**依存タスク**: 5.1, 6.2

### 7.2 依存パッケージ定義
- FastAPI
- SQLAlchemy
- pytest
- その他必要なパッケージ

**対象ファイル**: `requirements.txt`

**受入基準**:
- バージョン固定
- 開発用・本番用の分離
