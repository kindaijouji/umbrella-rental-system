import os

class Config:
    """アプリケーション設定"""
    
    # 基本設定
    DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'nfc-reader-secret-key')
    
    # NFCリーダー設定
    NFC_READER_PATH = os.environ.get('NFC_READER_PATH', 'usb')
    
    # データファイルのパス
    STUDENT_DATA_FILE = os.environ.get('STUDENT_DATA_FILE', 'data/students.json')
    ATTENDANCE_DATA_FILE = os.environ.get('ATTENDANCE_DATA_FILE', 'data/attendance.json')