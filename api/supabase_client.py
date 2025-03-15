import os
from supabase import create_client, Client

class SupabaseClient:
    """Supabaseデータベースクライアント"""
    
    _instance = None
    
    def __new__(cls):
        """シングルトンパターン実装"""
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初期化（シングルトンなので一度だけ実行）"""
        if self._initialized:
            return
            
        self._initialized = True
        
        # Supabase認証情報
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("環境変数 SUPABASE_URL と SUPABASE_KEY を設定してください")
        
        self.supabase = create_client(url, key)
    
    def get_client(self) -> Client:
        """Supabaseクライアントを取得"""
        return self.supabase