import time
from datetime import datetime
from supabase_client import SupabaseClient

class UmbrellaService:
    """傘の貸し出し管理サービス"""
    
    _instance = None
    
    def __new__(cls):
        """シングルトンパターン実装"""
        if cls._instance is None:
            cls._instance = super(UmbrellaService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初期化（シングルトンなので一度だけ実行）"""
        if self._initialized:
            return
            
        self._initialized = True
        self.supabase = SupabaseClient().get_client()
    
    def check_student_status(self, student_id):
        """学生の傘貸出状態を確認"""
        try:
            # 学生のレコードを取得
            response = self.supabase.table('students') \
                .select('*') \
                .eq('student_id', student_id) \
                .execute()
                
            if len(response.data) == 0:
                # 新規学生の場合は登録
                return {
                    'exists': False,
                    'has_umbrella': False,
                    'student_id': student_id
                }
            
            student = response.data[0]
            return {
                'exists': True,
                'has_umbrella': student['status'] == 'borrowed',
                'student_id': student_id,
                'status': student['status']
            }
            
        except Exception as e:
            print(f"学生状態確認エラー: {e}")
            raise
    
    def borrow_umbrella(self, student_id):
        """傘を借りる処理"""
        try:
            # 現在の状態を確認
            status = self.check_student_status(student_id)
            
            if status['has_umbrella']:
                return {
                    'success': False,
                    'message': '既に傘を借りています',
                    'status': 'already_borrowed'
                }
            
            # 現在時刻
            now = datetime.now().isoformat()
            
            if not status['exists']:
                # 学生レコードを新規作成
                self.supabase.table('students').insert({
                    'student_id': student_id,
                    'status': 'borrowed'
                }).execute()
            else:
                # 学生の状態を更新
                self.supabase.table('students') \
                    .update({'status': 'borrowed'}) \
                    .eq('student_id', student_id) \
                    .execute()
            
            # 履歴に記録
            self.supabase.table('history').insert({
                'student_id': student_id,
                'action': 'borrow',
                'timestamp': now
            }).execute()
            
            return {
                'success': True,
                'message': '傘の貸出に成功しました',
                'status': 'borrowed',
                'timestamp': now
            }
            
        except Exception as e:
            print(f"傘貸出エラー: {e}")
            raise
    
    def return_umbrella(self, student_id):
        """傘を返却する処理"""
        try:
            # 現在の状態を確認
            status = self.check_student_status(student_id)
            
            if not status['exists'] or not status['has_umbrella']:
                return {
                    'success': False,
                    'message': '借りている傘がありません',
                    'status': 'not_borrowed'
                }
            
            # 現在時刻
            now = datetime.now().isoformat()
            
            # 学生の状態を更新
            self.supabase.table('students') \
                .update({'status': 'returned'}) \
                .eq('student_id', student_id) \
                .execute()
            
            # 履歴に記録
            self.supabase.table('history').insert({
                'student_id': student_id,
                'action': 'return',
                'timestamp': now
            }).execute()
            
            return {
                'success': True,
                'message': '傘の返却に成功しました',
                'status': 'returned',
                'timestamp': now
            }
            
        except Exception as e:
            print(f"傘返却エラー: {e}")
            raise
    
    def get_student_history(self, student_id, limit=10):
        """学生の傘貸出履歴を取得"""
        try:
            response = self.supabase.table('history') \
                .select('*') \
                .eq('student_id', student_id) \
                .order('timestamp', desc=True) \
                .limit(limit) \
                .execute()
            
            return response.data
            
        except Exception as e:
            print(f"履歴取得エラー: {e}")
            raise
    
    def get_recent_activities(self, limit=20):
        """最近の活動履歴を取得"""
        try:
            response = self.supabase.table('history') \
                .select('*') \
                .order('timestamp', desc=True) \
                .limit(limit) \
                .execute()
            
            return response.data
            
        except Exception as e:
            print(f"最近の活動取得エラー: {e}")
            raise