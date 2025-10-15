"""
Template Manager - プロジェクトテンプレートの管理
"""
import shutil
from pathlib import Path
from typing import List, Dict, Any
import yaml


class TemplateManager:
    """プロジェクトテンプレートを管理"""
    
    def __init__(self):
        # パッケージ内のテンプレートディレクトリ
        self.templates_dir = Path(__file__).parent / "templates"
    
    def list_templates(self) -> List[Dict[str, str]]:
        """利用可能なテンプレート一覧"""
        templates = [
            {
                'id': 'web-app',
                'name': 'Web Application',
                'description': 'フルスタックWebアプリケーション（Frontend + Backend + DB）'
            },
            {
                'id': 'ml-pipeline',
                'name': 'ML Pipeline',
                'description': '機械学習パイプライン（Data Engineering + ML + Evaluation）'
            },
            {
                'id': 'data-analytics',
                'name': 'Data Analytics',
                'description': 'データ分析プロジェクト（ETL + Analysis + Visualization）'
            },
            {
                'id': 'microservices',
                'name': 'Microservices',
                'description': 'マイクロサービス構成（複数サービス + Gateway）'
            },
            {
                'id': 'api-only',
                'name': 'API Backend',
                'description': 'APIバックエンドのみ（Backend + DB + Test）'
            }
        ]
        return templates
    
    def create_project(self, project_name: str, template_id: str, base_path: Path):
        """テンプレートからプロジェクトを作成"""
        project_path = base_path / project_name
        project_path.mkdir(parents=True, exist_ok=True)
        
        # 基本ディレクトリ構造を作成
        self._create_directory_structure(project_path)
        
        # テンプレート固有の設定を適用
        self._apply_template(project_path, template_id, project_name)
        
        # README を作成
        self._create_project_readme(project_path, project_name, template_id)
    
    def _create_directory_structure(self, project_path: Path):
        """基本ディレクトリ構造を作成"""
        directories = [
            "shared/docs",
            "shared/coordination",
            "shared/contracts",
            "shared/artifacts/frontend",
            "shared/artifacts/backend",
            "shared/artifacts/database",
            "shared/artifacts/tests",
            "shared/artifacts/docs",
        ]
        
        for dir_path in directories:
            (project_path / dir_path).mkdir(parents=True, exist_ok=True)
    
    def _apply_template(self, project_path: Path, template_id: str, project_name: str):
        """テンプレート固有の設定を適用"""
        if template_id == 'web-app':
            self._create_web_app_template(project_path, project_name)
        elif template_id == 'ml-pipeline':
            self._create_ml_pipeline_template(project_path, project_name)
        elif template_id == 'data-analytics':
            self._create_data_analytics_template(project_path, project_name)
        elif template_id == 'microservices':
            self._create_microservices_template(project_path, project_name)
        elif template_id == 'api-only':
            self._create_api_only_template(project_path, project_name)
        else:
            raise ValueError(f"不明なテンプレート: {template_id}")
    
    def _create_web_app_template(self, project_path: Path, project_name: str):
        """Webアプリテンプレート"""
        config = {
            'project_name': project_name,
            'description': 'フルスタックWebアプリケーション',
            'version': '1.0',
            'settings': {
                'communication': {
                    'shared_space': '/shared/',
                    'progress_update_interval': '5分',
                    'status_format': 'json'
                },
                'quality': {
                    'code_review_required': True,
                    'test_coverage_minimum': 80,
                    'security_scan': True
                }
            },
            'workers': [
                {
                    'id': 'coordinator',
                    'role': 'プロジェクト統括',
                    'type': 'orchestrator'
                },
                {
                    'id': 'frontend',
                    'role': 'フロントエンド開発',
                    'type': 'implementation',
                    'skills': ['React', 'TypeScript', 'Tailwind CSS'],
                    'responsibilities': [
                        'UI/UXコンポーネント実装',
                        '状態管理',
                        'APIクライアント実装'
                    ],
                    'reads': [
                        '/shared/docs/requirements.md',
                        '/shared/docs/api-specification.yaml'
                    ],
                    'writes': ['/shared/artifacts/frontend/**/*'],
                    'depends_on': ['backend']
                },
                {
                    'id': 'backend',
                    'role': 'バックエンド開発',
                    'type': 'implementation',
                    'skills': ['Python', 'FastAPI', 'PostgreSQL'],
                    'responsibilities': [
                        'REST API実装',
                        'ビジネスロジック',
                        'データベース操作'
                    ],
                    'reads': [
                        '/shared/docs/requirements.md',
                        '/shared/docs/api-specification.yaml',
                        '/shared/docs/data-models.json'
                    ],
                    'writes': ['/shared/artifacts/backend/**/*'],
                    'depends_on': ['database']
                },
                {
                    'id': 'database',
                    'role': 'データベース設計',
                    'type': 'implementation',
                    'skills': ['PostgreSQL', 'データモデリング'],
                    'responsibilities': [
                        'スキーマ設計',
                        'マイグレーション管理'
                    ],
                    'reads': ['/shared/docs/data-models.json'],
                    'writes': ['/shared/artifacts/database/**/*'],
                    'depends_on': []
                },
                {
                    'id': 'test',
                    'role': '品質保証',
                    'type': 'quality_assurance',
                    'skills': ['pytest', 'Playwright', 'Jest'],
                    'responsibilities': [
                        'ユニットテスト',
                        '統合テスト',
                        'E2Eテスト'
                    ],
                    'reads': ['/shared/docs/test-strategy.md'],
                    'writes': ['/shared/artifacts/tests/**/*'],
                    'depends_on': ['frontend', 'backend']
                }
            ]
        }
        
        # workers-config.yaml を作成
        with open(project_path / 'workers-config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        
        # サンプルドキュメントを作成
        self._create_sample_documents(project_path, 'web-app')
    
    def _create_ml_pipeline_template(self, project_path: Path, project_name: str):
        """機械学習パイプラインテンプレート"""
        config = {
            'project_name': project_name,
            'project_type': 'ml_pipeline',
            'workers': [
                {'id': 'coordinator', 'role': '統括', 'type': 'orchestrator'},
                {
                    'id': 'data_engineer',
                    'role': 'データエンジニアリング',
                    'type': 'implementation',
                    'skills': ['Python', 'pandas', 'SQL', 'Airflow']
                },
                {
                    'id': 'ml_engineer',
                    'role': '機械学習モデル開発',
                    'type': 'implementation',
                    'skills': ['Python', 'scikit-learn', 'PyTorch'],
                    'depends_on': ['data_engineer']
                },
                {
                    'id': 'evaluation',
                    'role': 'モデル評価',
                    'type': 'quality_assurance',
                    'skills': ['評価指標', 'A/Bテスト'],
                    'depends_on': ['ml_engineer']
                }
            ]
        }
        
        with open(project_path / 'workers-config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        
        self._create_sample_documents(project_path, 'ml-pipeline')
    
    def _create_data_analytics_template(self, project_path: Path, project_name: str):
        """データ分析テンプレート"""
        # 実装省略（同様のパターン）
        pass
    
    def _create_microservices_template(self, project_path: Path, project_name: str):
        """マイクロサービステンプレート"""
        # 実装省略（同様のパターン）
        pass
    
    def _create_api_only_template(self, project_path: Path, project_name: str):
        """APIバックエンドのみテンプレート"""
        # 実装省略（同様のパターン）
        pass
    
    def _create_sample_documents(self, project_path: Path, template_type: str):
        """サンプルドキュメントを作成"""
        docs_path = project_path / "shared" / "docs"
        
        # requirements.md
        requirements_content = """# 要件定義

## プロジェクト概要
このドキュメントには、プロジェクトの要件を記述してください。

## 機能要件
### 機能1
- 詳細1
- 詳細2

### 機能2
- 詳細1
- 詳細2

## 非機能要件
- パフォーマンス
- セキュリティ
- スケーラビリティ
"""
        
        with open(docs_path / "requirements.md", 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        
        # architecture.md
        architecture_content = """# システムアーキテクチャ

## 概要
システムの全体構成を記述してください。

## コンポーネント
### フロントエンド
- 技術スタック
- 責務

### バックエンド
- 技術スタック
- 責務

## データフロー
1. ユーザー → Frontend
2. Frontend → Backend API
3. Backend → Database
"""
        
        with open(docs_path / "architecture.md", 'w', encoding='utf-8') as f:
            f.write(architecture_content)
        
        # api-specification.yaml
        api_spec_content = """openapi: 3.0.0
info:
  title: Project API
  version: 1.0.0
paths:
  /api/v1/example:
    get:
      summary: サンプルエンドポイント
      responses:
        '200':
          description: Success
"""
        
        with open(docs_path / "api-specification.yaml", 'w', encoding='utf-8') as f:
            f.write(api_spec_content)
        
        # data-models.json
        data_models = {
            "User": {
                "id": "integer",
                "email": "string",
                "created_at": "datetime"
            }
        }
        
        import json
        with open(docs_path / "data-models.json", 'w', encoding='utf-8') as f:
            json.dump(data_models, f, indent=2, ensure_ascii=False)
    
    def _create_project_readme(self, project_path: Path, project_name: str, template_id: str):
        """プロジェクトのREADMEを作成"""
        readme_content = f"""# {project_name}

プロジェクトテンプレート: {template_id}

## 使い方

### 1. 要件を記述
`shared/docs/requirements.md` に要件を記述してください。

### 2. Coordinator起動
```bash
cmw start
```

### 3. 進捗確認
```bash
cmw status
```

## ディレクトリ構造

```
{project_name}/
├── shared/
│   ├── docs/              # 設計ドキュメント
│   ├── coordination/      # タスク・進捗管理
│   └── artifacts/         # 成果物
└── workers-config.yaml    # ワーカー定義
```

## ドキュメント

- `shared/docs/requirements.md` - 要件定義
- `shared/docs/architecture.md` - アーキテクチャ
- `shared/docs/api-specification.yaml` - API仕様
- `shared/docs/data-models.json` - データモデル

---

Generated by Claude Multi-Worker Framework
"""
        
        with open(project_path / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
