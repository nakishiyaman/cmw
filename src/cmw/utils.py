"""
Utility classes for the framework
"""
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class Logger:
    """シンプルなロガー"""
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _log(self, level: str, message: str):
        """ログメッセージを記録"""
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] [{level}] {message}\n"
        
        # ファイルに追記
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_line)
        
        # コンソールにも出力
        print(log_line.rstrip())
    
    def info(self, message: str):
        self._log("INFO", message)
    
    def warning(self, message: str):
        self._log("WARNING", message)
    
    def error(self, message: str):
        self._log("ERROR", message)


class DocumentParser:
    """ドキュメント解析"""
    
    def __init__(self, docs_path: Path):
        self.docs_path = docs_path
    
    def parse_requirements(self, file_path: Path) -> Dict[str, Any]:
        """requirements.md を解析"""
        if not file_path.exists():
            return {'sections': []}
        
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
        
        sections = []
        current_section = None
        
        for line in content.split('\n'):
            # 見出しを検出
            if line.startswith('##'):
                if current_section:
                    sections.append(current_section)
                
                title = line.lstrip('#').strip()
                current_section = {
                    'id': self._slugify(title),
                    'title': title,
                    'content': [],
                    'keywords': []
                }
            elif current_section and line.strip():
                current_section['content'].append(line)
                # キーワード抽出
                keywords = self._extract_keywords(line)
                current_section['keywords'].extend(keywords)
        
        if current_section:
            sections.append(current_section)
        
        return {'sections': sections}
    
    def _slugify(self, text: str) -> str:
        """テキストをスラッグに変換"""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_-]+', '-', text)
        return text.strip('-')
    
    def _extract_keywords(self, text: str) -> List[str]:
        """テキストからキーワードを抽出"""
        # 簡易的な実装
        keywords = []
        tech_terms = [
            'api', 'database', 'frontend', 'backend', 'ui', 'ux',
            'authentication', 'authorization', 'security', 'test'
        ]
        
        text_lower = text.lower()
        for term in tech_terms:
            if term in text_lower:
                keywords.append(term)
        
        return keywords
    
    def load_api_spec(self) -> Dict[str, Any]:
        """API仕様を読み込み"""
        api_spec_file = self.docs_path / "api-specification.yaml"
        
        if not api_spec_file.exists():
            return {}
        
        with open(api_spec_file, encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def load_data_models(self) -> Dict[str, Any]:
        """データモデルを読み込み"""
        data_models_file = self.docs_path / "data-models.json"
        
        if not data_models_file.exists():
            return {}
        
        with open(data_models_file, encoding='utf-8') as f:
            return json.load(f)


class ConsistencyChecker:
    """整合性チェッカー"""
    
    def __init__(self, docs_path: Path, artifacts_path: Path):
        self.docs_path = docs_path
        self.artifacts_path = artifacts_path
        self.doc_parser = DocumentParser(docs_path)
    
    def check_api_consistency(self) -> List[Dict[str, Any]]:
        """API仕様の整合性をチェック"""
        inconsistencies = []
        
        # API仕様を読み込み
        api_spec = self.doc_parser.load_api_spec()
        
        if not api_spec:
            return inconsistencies
        
        # Frontend の実装をチェック
        frontend_path = self.artifacts_path / "frontend"
        if frontend_path.exists():
            frontend_calls = self._extract_api_calls_from_frontend(frontend_path)
            
            # 仕様と照合
            spec_endpoints = self._extract_endpoints_from_spec(api_spec)
            
            for call in frontend_calls:
                endpoint_key = f"{call['method']} {call['path']}"
                if endpoint_key not in spec_endpoints:
                    inconsistencies.append({
                        'type': 'missing_in_spec',
                        'frontend_call': call,
                        'message': f"Frontend が呼び出している {endpoint_key} が仕様に存在しません"
                    })
        
        # Backend の実装をチェック
        backend_path = self.artifacts_path / "backend"
        if backend_path.exists():
            backend_endpoints = self._extract_endpoints_from_backend(backend_path)
            
            spec_endpoints = self._extract_endpoints_from_spec(api_spec)
            
            for endpoint_key in spec_endpoints:
                if endpoint_key not in backend_endpoints:
                    inconsistencies.append({
                        'type': 'missing_implementation',
                        'endpoint': endpoint_key,
                        'message': f"仕様に定義された {endpoint_key} が Backend に実装されていません"
                    })
        
        return inconsistencies
    
    def _extract_api_calls_from_frontend(self, frontend_path: Path) -> List[Dict[str, str]]:
        """Frontend のコードからAPI呼び出しを抽出"""
        calls = []
        
        # 簡易的な実装（実際には AST 解析が必要）
        for file_path in frontend_path.rglob("*.ts"):
            try:
                with open(file_path, encoding='utf-8') as f:
                    content = f.read()
                
                # fetch や axios の呼び出しを検出
                patterns = [
                    r'fetch\([\'"]([^\'"]+)[\'"]',
                    r'axios\.(get|post|put|delete)\([\'"]([^\'"]+)[\'"]'
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        if 'axios' in pattern:
                            calls.append({
                                'method': match.group(1).upper(),
                                'path': match.group(2),
                                'file': str(file_path)
                            })
                        else:
                            calls.append({
                                'method': 'GET',  # デフォルト
                                'path': match.group(1),
                                'file': str(file_path)
                            })
            except Exception:
                continue
        
        return calls
    
    def _extract_endpoints_from_spec(self, api_spec: Dict[str, Any]) -> Dict[str, Any]:
        """OpenAPI仕様からエンドポイントを抽出"""
        endpoints = {}
        
        if 'paths' not in api_spec:
            return endpoints
        
        for path, methods in api_spec['paths'].items():
            for method, details in methods.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    endpoint_key = f"{method.upper()} {path}"
                    endpoints[endpoint_key] = details
        
        return endpoints
    
    def _extract_endpoints_from_backend(self, backend_path: Path) -> Dict[str, Any]:
        """Backend のコードからエンドポイントを抽出"""
        endpoints = {}
        
        # 簡易的な実装（実際には AST 解析が必要）
        for file_path in backend_path.rglob("*.py"):
            try:
                with open(file_path, encoding='utf-8') as f:
                    content = f.read()
                
                # FastAPI のルートデコレータを検出
                patterns = [
                    r'@app\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]',
                    r'@router\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]'
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        endpoint_key = f"{match.group(1).upper()} {match.group(2)}"
                        endpoints[endpoint_key] = {'file': str(file_path)}
            except Exception:
                continue
        
        return endpoints
    
    def check_data_model_consistency(self) -> List[Dict[str, Any]]:
        """データモデルの整合性をチェック"""
        inconsistencies = []
        
        # データモデル定義を読み込み
        data_models = self.doc_parser.load_data_models()
        
        if not data_models:
            return inconsistencies
        
        # TODO: Backend のモデル定義と照合
        # TODO: Database のスキーマと照合
        
        return inconsistencies
    
    def check_security_compliance(self) -> List[Dict[str, Any]]:
        """セキュリティポリシーへの準拠をチェック"""
        inconsistencies = []
        
        security_policy_file = self.docs_path / "security-policy.md"
        
        if not security_policy_file.exists():
            return inconsistencies
        
        # TODO: セキュリティポリシーの解析と実装のチェック
        
        return inconsistencies


class FileWatcher:
    """ファイル変更監視（watchdogを使用）"""
    
    def __init__(self, path: Path):
        self.path = path
        self.handlers = {}
    
    def on_change(self, pattern: str):
        """デコレータ：ファイル変更時のハンドラを登録"""
        def decorator(func):
            self.handlers[pattern] = func
            return func
        return decorator
    
    def start(self):
        """監視を開始"""
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        class ChangeHandler(FileSystemEventHandler):
            def __init__(self, watcher):
                self.watcher = watcher
            
            def on_modified(self, event):
                if event.is_directory:
                    return
                
                file_path = Path(event.src_path)
                
                for pattern, handler in self.watcher.handlers.items():
                    if pattern in file_path.name:
                        handler({'path': file_path})
        
        observer = Observer()
        handler = ChangeHandler(self)
        observer.schedule(handler, str(self.path), recursive=True)
        observer.start()
        
        return observer
