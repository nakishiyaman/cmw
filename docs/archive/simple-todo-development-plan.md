# simple-todo 開発計画（検証用ソフトウェア）

**作成日**: 2025-10-15  
**目的**: マルチワーカーフレームワークの検証基準となる「正解例」を手動で作成

---

## 🎯 開発の目的

このsimple-todoアプリは：
1. **正解例**: マルチワーカーが生成すべき「目標」
2. **比較基準**: Worker生成コードの品質評価
3. **検証手段**: Workerの精度を測定

---

## 📊 現状の実装状況

### ✅ 完成している部分

#### フロントエンド（React + Vite + TypeScript + Tailwind CSS）
- ✅ プロジェクト構造
- ✅ package.json、vite.config.ts、tailwind.config.js
- ✅ ログインページ（LoginPage.tsx）
- ✅ サインアップページ（SignupPage.tsx）
- ✅ タスク管理ページ（TasksPage.tsx）
- ✅ 認証コンテキスト（AuthContext.tsx）
- ✅ プライベートルート（PrivateRoute.tsx）
- ✅ 型定義（types/index.ts）
- ✅ APIクライアント（services/api.ts）
- ✅ ルーティング（App.tsx）
- ✅ Vite起動（ポート3001）

**動作確認**:
- ✅ `http://localhost:3001/` でログイン画面表示

#### バックエンド（FastAPI + Python）
- ✅ プロジェクト構造
- ✅ main.py（FastAPIアプリ）
- ✅ config.py（設定管理）
- ✅ routers/auth.py（認証エンドポイント）
- ✅ routers/tasks.py（タスクエンドポイント）
- ✅ schemas/（Pydanticスキーマ）
- ✅ crud/（CRUD操作）
- ✅ core/security.py（JWT、パスワードハッシュ）
- ✅ core/deps.py（依存性注入）
- ✅ CORS設定（ポート3001対応）
- ✅ .env ファイル

**動作確認**:
- ✅ `http://localhost:8000/docs` でSwagger UI表示
- ✅ 全エンドポイント定義確認済み

---

## ❌ 未実装の部分

### 最優先：データベース層
**推定時間**: 30分

#### タスク1: database.py 作成
**ファイル**: `backend/core/database.py`

**実装内容**:
```python
"""
データベース接続とセッション管理
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..config import settings

# SQLAlchemyエンジン作成
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# セッションローカル
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースクラス
Base = declarative_base()

# 依存性注入用
def get_db():
    """データベースセッションを取得"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**検証**:
```bash
cd backend
python3 -c "from core.database import engine; print(engine)"
```

---

#### タスク2: models.py 作成
**ファイル**: `backend/core/models.py`

**実装内容**:
```python
"""
SQLAlchemyモデル定義
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from .database import Base

class User(Base):
    """ユーザーモデル"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーション
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")

class PriorityEnum(str, enum.Enum):
    """優先度"""
    high = "high"
    medium = "medium"
    low = "low"

class Task(Base):
    """タスクモデル"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False, index=True)
    priority = Column(SQLEnum(PriorityEnum), default=PriorityEnum.medium, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    category = Column(String(50), nullable=True, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # リレーション
    owner = relationship("User", back_populates="tasks")
    
    # インデックス
    __table_args__ = (
        Index('ix_tasks_user_completed', 'user_id', 'is_completed'),
        Index('ix_tasks_user_category', 'user_id', 'category'),
    )
```

**検証**:
```bash
cd backend
python3 -c "from core.models import User, Task; print('Models loaded')"
```

---

#### タスク3: データベース初期化スクリプト
**ファイル**: `backend/init_db.py`

**実装内容**:
```python
"""
データベース初期化スクリプト
"""
from core.database import engine, Base
from core.models import User, Task

def init_db():
    """データベーステーブルを作成"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
```

**実行**:
```bash
cd backend
python3 init_db.py
```

**検証**:
```bash
# SQLiteファイルが作成されたことを確認
ls -la simple_todo.db

# テーブルが作成されたことを確認
sqlite3 simple_todo.db ".tables"
# 期待される出力: users  tasks
```

---

#### タスク4: ルーターでdatabase接続を使用
**ファイル**: 既存の `routers/auth.py`, `routers/tasks.py`

**変更点**:
現在のルーターはすでに `get_db` を使用しているはずなので、確認のみ。

**確認**:
```bash
grep "get_db" backend/routers/auth.py
grep "get_db" backend/routers/tasks.py
```

---

### タスク5: 動作確認（エンドツーエンド）
**推定時間**: 15分

#### 5.1 バックエンド起動確認
```bash
cd backend
uvicorn main:app --reload --port 8000
```

#### 5.2 新規登録テスト
**ブラウザ操作**:
1. `http://localhost:3001/` を開く
2. 「新規登録」リンクをクリック
3. メールアドレス: `test@example.com`
4. パスワード: `password123`
5. 登録ボタンをクリック

**期待される結果**:
- ✅ 登録成功
- ✅ 自動的にログイン状態になる
- ✅ タスク管理画面にリダイレクト

**確認方法**:
```bash
# データベースにユーザーが作成されたか確認
sqlite3 backend/simple_todo.db "SELECT * FROM users;"
```

#### 5.3 ログインテスト
1. ログアウト
2. `http://localhost:3001/login` を開く
3. 先ほど登録した情報でログイン

**期待される結果**:
- ✅ ログイン成功
- ✅ タスク管理画面表示

#### 5.4 タスクCRUDテスト
**タスク作成**:
1. タスク管理画面で「新規タスク」をクリック
2. タイトル: `テストタスク`
3. 説明: `これはテストです`
4. 優先度: `高`
5. 作成ボタンをクリック

**期待される結果**:
- ✅ タスクが一覧に表示される

**タスク編集**:
1. タスクをクリック
2. タイトルを変更
3. 保存

**期待される結果**:
- ✅ 変更が反映される

**タスク完了**:
1. チェックボックスをクリック

**期待される結果**:
- ✅ 完了マークが表示される
- ✅ 完了日時が記録される

**タスク削除**:
1. 削除ボタンをクリック
2. 確認ダイアログで「はい」

**期待される結果**:
- ✅ タスクが一覧から消える

**データベース確認**:
```bash
sqlite3 backend/simple_todo.db "SELECT * FROM tasks;"
```

---

## 📋 実装チェックリスト

### データベース層
- [ ] `backend/core/database.py` 作成
- [ ] `backend/core/models.py` 作成
- [ ] `backend/init_db.py` 作成
- [ ] データベース初期化実行
- [ ] テーブル作成確認

### 動作確認
- [ ] バックエンド起動（ポート8000）
- [ ] フロントエンド起動（ポート3001）
- [ ] 新規登録成功
- [ ] ログイン成功
- [ ] タスク作成成功
- [ ] タスク一覧表示
- [ ] タスク編集成功
- [ ] タスク完了切り替え
- [ ] タスク削除成功
- [ ] ログアウト成功

### 完成の定義
**以下のすべてが動作すること**:
1. ✅ ユーザー登録
2. ✅ ログイン・ログアウト
3. ✅ タスクCRUD（作成・一覧・編集・削除）
4. ✅ タスク完了状態の切り替え
5. ✅ フィルタリング（完了/未完了）
6. ✅ カテゴリー別表示
7. ✅ 優先度別表示

---

## 🎯 マイルストーン

| タスク | 内容 | 推定時間 | 完成度 |
|--------|------|----------|--------|
| Task 1 | database.py | 5分 | 0% ❌ |
| Task 2 | models.py | 15分 | 0% ❌ |
| Task 3 | init_db.py | 5分 | 0% ❌ |
| Task 4 | 初期化実行 | 2分 | 0% ❌ |
| Task 5 | 動作確認 | 15分 | 0% ❌ |

**合計推定時間**: 42分

---

## 🚀 実装の手順（ステップバイステップ）

### Step 1: database.py 作成
```bash
cd ~/workspace/projects/simple-todo/shared/artifacts/backend
vi core/database.py
# 上記の内容をコピペ
```

### Step 2: models.py 作成
```bash
vi core/models.py
# 上記の内容をコピペ
```

### Step 3: init_db.py 作成
```bash
vi init_db.py
# 上記の内容をコピペ
```

### Step 4: データベース初期化
```bash
python3 init_db.py
```

### Step 5: 動作確認
```bash
# バックエンド起動（別ターミナル）
cd ~/workspace/projects/simple-todo/shared/artifacts
uvicorn backend.main:app --reload --port 8000

# フロントエンド起動（別ターミナル）
cd ~/workspace/projects/simple-todo/shared/artifacts/frontend
npm run dev
```

ブラウザで `http://localhost:3001/` を開いて、全機能をテスト。

---

## 📝 完成後の確認事項

### コード品質
- [ ] すべてのファイルが正しく配置されている
- [ ] インポートエラーがない
- [ ] 型定義が正しい
- [ ] SQLAlchemyのリレーションが正しい

### 機能確認
- [ ] すべてのユーザーフローが動作する
- [ ] エラーハンドリングが適切
- [ ] レスポンスが高速

### ドキュメント
- [ ] README.mdに起動手順を記載
- [ ] API仕様が最新
- [ ] データモデルが最新

---

## 🎓 完成後の成果物

### 1. 動作するアプリケーション
- フロントエンド + バックエンド + データベース
- すべての機能が動作

### 2. 「正解例」としての価値
- Workerが生成すべきコードの基準
- 比較・評価の対象

### 3. 学習データ
- 良いコードの実例
- プロンプト設計の参考

---

## 📌 次回セッションの開始手順

```bash
# プロジェクトディレクトリに移動
cd ~/workspace/projects/simple-todo

# 現状確認
ls -la shared/artifacts/backend/core/

# 未作成ファイルを確認
# database.py, models.py, init_db.py があるか？

# なければ作成開始
vi shared/artifacts/backend/core/database.py
```

---

## ⚠️ 注意事項

1. **バックアップ**
   - 既存のファイルを上書きしないよう注意
   - Git commit してから作業開始

2. **依存関係**
   - SQLAlchemy がインストールされているか確認
   - 必要なら: `pip install sqlalchemy --break-system-packages`

3. **データベースファイル**
   - `.gitignore` に `*.db` を追加
   - 本番環境ではPostgreSQLを使用
