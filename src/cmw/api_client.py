"""
Claude APIクライアント

Anthropic APIとの通信を管理し、タスク実行のためのコード生成を行います。
"""
import os
from typing import Optional
from anthropic import Anthropic


class ClaudeAPIClient:
    """Claude APIとの通信を管理するクライアント"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Claude APIクライアントを初期化
        
        Args:
            api_key: Anthropic API key（Noneの場合は環境変数から取得）
            
        Raises:
            ValueError: API keyが設定されていない場合
        """
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError(
                "API keyが設定されていません。"
                "環境変数 ANTHROPIC_API_KEY を設定するか、"
                "api_key 引数で指定してください。"
            )
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"
    
    def generate_code(
        self, 
        prompt: str, 
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> str:
        """
        プロンプトからコードを生成
        
        Args:
            prompt: コード生成の指示プロンプト
            max_tokens: 最大トークン数（デフォルト: 4000）
            temperature: 生成の創造性（0.0-1.0、デフォルト: 0.7）
            
        Returns:
            生成されたコード（文字列）
            
        Raises:
            RuntimeError: API呼び出しに失敗した場合
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # レスポンスからテキストを抽出
            if message.content and len(message.content) > 0:
                return message.content[0].text
            else:
                raise RuntimeError("APIからの応答が空です")
            
        except Exception as e:
            raise RuntimeError(f"Claude API呼び出しエラー: {str(e)}")
    
    def validate_api_key(self) -> bool:
        """
        API keyが有効かどうかを確認
        
        Returns:
            True: API keyが有効
            False: API keyが無効
        """
        try:
            # 簡単なテストリクエストを送信
            self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception:
            return False
