"""
PromptGenerator - タスクから実行用プロンプトを生成
"""
from pathlib import Path
from typing import Dict, Any, List
from .models import Task


class PromptGenerator:
    """
    タスク情報から、Claude Codeで実行可能な
    詳細なプロンプトを生成する
    """
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.shared_path = project_path / "shared"
        self.docs_path = self.shared_path / "docs"
        self.artifacts_path = self.shared_path / "artifacts"
    
    def generate_prompt(self, task: Task) -> str:
        """タスクから実行用プロンプトを生成"""
        
        # ワーカーの役割に応じてプロンプトを生成
        if task.worker_id == "database":
            return self._generate_database_prompt(task)
        elif task.worker_id == "backend":
            return self._generate_backend_prompt(task)
        elif task.worker_id == "frontend":
            return self._generate_frontend_prompt(task)
        elif task.worker_id == "test":
            return self._generate_test_prompt(task)
        else:
            return self._generate_generic_prompt(task)
    
    def _generate_database_prompt(self, task: Task) -> str:
        """データベースタスク用プロンプト"""
        
        # 関連ドキュメントを読み込み
        context = self._load_context(task)
        
        prompt = f"""# データベース設計タスク

## タスク情報
- **タスクID**: {task.task_id}
- **タイトル**: {task.title}
- **優先度**: {task.priority}

## 目的
{task.instructions.get('description', 'データベーススキーマを設計・実装する')}

## 関連ドキュメント
{context}

## 実装すべきこと

### 1. データモデル定義
- SQLAlchemyモデルを作成
- 適切なフィールドとリレーションを定義
- バリデーションルールを設定

### 2. マイグレーションファイル
- Alembicマイグレーションスクリプトを作成
- アップグレード・ダウングレード処理を実装

### 3. インデックス設計
- パフォーマンス最適化のためのインデックスを定義

## 成果物の配置場所
{self._format_deliverables(task.deliverables)}

## 技術スタック
- SQLAlchemy (ORM)
- Alembic (マイグレーション)
- PostgreSQL 15+

## 実装時の注意点
- データ型は適切に選択する
- 外部キー制約を正しく設定する
- NOT NULL制約とデフォルト値を明示する
- created_at, updated_atは自動設定する

## 実行コマンド例
```bash
# マイグレーション作成
alembic revision --autogenerate -m "create {task.instructions.get('section', 'table')}"

# マイグレーション実行
alembic upgrade head
```

このタスクを完了してください。
"""
        return prompt
    
    def _generate_backend_prompt(self, task: Task) -> str:
        """バックエンドタスク用プロンプト"""
        
        context = self._load_context(task)
        
        prompt = f"""# バックエンドAPI実装タスク

## タスク情報
- **タスクID**: {task.task_id}
- **タイトル**: {task.title}
- **優先度**: {task.priority}

## 目的
{task.instructions.get('description', 'REST APIエンドポイントを実装する')}

## 関連ドキュメント
{context}

## 実装すべきこと

### 1. APIルーター
- FastAPIのルーターを作成
- 適切なHTTPメソッド（GET, POST, PUT, DELETE）を実装
- リクエスト/レスポンスモデルを定義（Pydantic）

### 2. ビジネスロジック
- CRUD操作を実装
- バリデーションロジック
- エラーハンドリング

### 3. 認証・認可
- JWT認証ミドルウェア（必要な場合）
- ユーザー権限チェック

### 4. レスポンス設計
- 適切なHTTPステータスコード
- 統一されたエラーレスポンス形式

## 成果物の配置場所
{self._format_deliverables(task.deliverables)}

## 技術スタック
- FastAPI
- Pydantic (バリデーション)
- SQLAlchemy (ORM)
- python-jose (JWT)

## API仕様
API仕様書（api-specification.yaml）を参照して、
仕様に完全準拠した実装を行うこと。

## 実装時の注意点
- エンドポイントのパスは仕様書と一致させる
- レスポンススキーマは仕様書通りに
- 適切なHTTPステータスコードを返す
- エラーハンドリングを必ず実装

## テスト
- 各エンドポイントの基本的なテストケースを含める
- 正常系・異常系のテストを実装

このタスクを完了してください。
"""
        return prompt
    
    def _generate_frontend_prompt(self, task: Task) -> str:
        """フロントエンドタスク用プロンプト"""
        
        context = self._load_context(task)
        
        prompt = f"""# フロントエンドUI実装タスク

## タスク情報
- **タスクID**: {task.task_id}
- **タイトル**: {task.title}
- **優先度**: {task.priority}

## 目的
{task.instructions.get('description', 'UIコンポーネントを実装する')}

## 関連ドキュメント
{context}

## 実装すべきこと

### 1. コンポーネント設計
- Reactコンポーネントを作成
- TypeScriptで型安全に実装
- 適切なPropsとStateを定義

### 2. UIデザイン
- Tailwind CSSでスタイリング
- レスポンシブデザイン対応
- アクセシビリティ（a11y）を考慮

### 3. API連携
- APIクライアントを実装（axios）
- ローディング状態の管理
- エラーハンドリングとユーザーフィードバック

### 4. 状態管理
- React Hooks（useState, useEffect）
- 必要に応じてContext APIやRedux

## 成果物の配置場所
{self._format_deliverables(task.deliverables)}

## 技術スタック
- React 18+
- TypeScript
- Tailwind CSS
- Axios (HTTP client)
- React Router (ルーティング)

## UI/UX要件
- 直感的な操作性
- 適切なローディング表示
- わかりやすいエラーメッセージ
- モバイルフレンドリー

## 実装時の注意点
- TypeScriptの型定義を正確に
- エラーバウンダリを実装
- 適切なバリデーション
- アクセシビリティ属性（aria-*）

このタスクを完了してください。
"""
        return prompt
    
    def _generate_test_prompt(self, task: Task) -> str:
        """テストタスク用プロンプト"""
        
        context = self._load_context(task)
        
        prompt = f"""# テスト実装タスク

## タスク情報
- **タスクID**: {task.task_id}
- **タイトル**: {task.title}
- **優先度**: {task.priority}

## 目的
{task.instructions.get('description', 'テストコードを作成する')}

## 関連ドキュメント
{context}

## 実装すべきこと

### 1. バックエンドテスト
- pytestでAPIテストを実装
- 正常系・異常系のテストケース
- カバレッジ80%以上を目指す

### 2. フロントエンドテスト
- Jest + React Testing Libraryでコンポーネントテスト
- ユーザーインタラクションのテスト
- スナップショットテスト

### 3. E2Eテスト（オプション）
- Playwrightでエンドツーエンドテスト
- 主要なユーザーフローをテスト

## 成果物の配置場所
{self._format_deliverables(task.deliverables)}

## 技術スタック
- pytest (バックエンド)
- Jest, React Testing Library (フロントエンド)
- Playwright (E2E)

## テスト指針
- 読みやすいテストコード
- 独立したテストケース
- 適切なアサーション
- モックの活用

このタスクを完了してください。
"""
        return prompt
    
    def _generate_generic_prompt(self, task: Task) -> str:
        """汎用プロンプト"""
        
        context = self._load_context(task)
        
        prompt = f"""# タスク実行

## タスク情報
- **タスクID**: {task.task_id}
- **タイトル**: {task.title}
- **ワーカー**: {task.worker_id}
- **優先度**: {task.priority}

## 実行内容
{task.instructions}

## 関連ドキュメント
{context}

## 成果物の配置場所
{self._format_deliverables(task.deliverables)}

このタスクを完了してください。
"""
        return prompt
    
    def _load_context(self, task: Task) -> str:
        """タスクに関連するドキュメントを読み込む"""
        context_parts = []

        for doc_ref in task.based_on:
            # /shared/docs/ → docs/ に変換
            doc_path = doc_ref.replace('/shared/docs/', 'docs/')

            # アンカー（#section）を削除
            if '#' in doc_path:
                doc_path = doc_path.split('#')[0]

            full_path = self.shared_path / doc_path

            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 長すぎる場合は要約
                        if len(content) > 3000:
                            content = content[:3000] + "\n\n... (以下省略)"
                        context_parts.append(f"\n### 📄 {doc_path}\n```\n{content}\n```\n")
                except Exception as e:
                    context_parts.append(f"\n### ⚠️ {doc_path}\n(読み込みエラー: {e})")
            else:
                # デバッグ情報
                context_parts.append(f"\n### ❌ {doc_path}\n(ファイルが見つかりません: {full_path})")

        if not context_parts:
            return "(関連ドキュメントなし)"

        return "\n".join(context_parts)
    
    def _format_deliverables(self, deliverables: List[str]) -> str:
        """成果物のリストをフォーマット"""
        if not deliverables:
            return "(成果物の指定なし)"
        
        formatted = []
        for item in deliverables:
            formatted.append(f"- `{item}`")
        
        return "\n".join(formatted)
    
    def generate_execution_guide(self, task: Task) -> str:
        """タスク実行ガイドを生成"""
        
        guide = f"""
# タスク実行ガイド: {task.task_id}

## 📋 タスク概要
**タイトル**: {task.title}
**ワーカー**: {task.worker_id}
**状態**: {task.status}

## 🎯 実行方法

### オプション1: プロンプトをコピーして手動実行

1. プロンプトを表示:
```bash
   cmw task execute {task.task_id} --show-prompt
```

2. プロンプトをコピー

3. Claude Code を起動:
```bash
   cd {self.artifacts_path / task.worker_id}
   # Claude Codeでプロンプトを実行
```

### オプション2: プロンプトをファイルに出力
```bash
cmw task execute {task.task_id} --output prompt-{task.task_id}.md
```

その後、ファイルを確認して実行。

## 📂 作業ディレクトリ
```
{self.artifacts_path / task.worker_id}/
```

## 📚 参照ドキュメント
"""
        for doc in task.based_on:
            guide += f"- {doc}\n"
        
        guide += f"""
## ✅ 完了条件
以下の成果物が作成されていること:
"""
        for deliverable in task.deliverables:
            guide += f"- {deliverable}\n"
        
        return guide
