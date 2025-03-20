from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv
from nfc_reader import NFCReader
from umbrella_service import UmbrellaService
from websocket_handler import register_websocket_handlers
from config import Config

# .envファイルから環境変数をロード
load_dotenv()

# Flaskアプリケーションとソケット初期化
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 設定の適用
app.config.from_object(Config)

# サービスの初期化
umbrella_service = UmbrellaService()

# NFCリーダーの初期化
nfc_reader = NFCReader(socketio, umbrella_service)

# WebSocketハンドラーの登録
register_websocket_handlers(socketio, nfc_reader)

# NFCリーダー APIエンドポイント

@app.route('/api/nfc/status', methods=['GET'])
def get_nfc_status():
    """NFCリーダーの状態を取得"""
    return jsonify({
        'active': nfc_reader.is_active(),
        'processing': nfc_reader.is_processing(),
        'last_tag_read': nfc_reader.get_last_tag_read()
    })

@app.route('/api/nfc/start', methods=['POST'])
def start_nfc_reader():
    """NFCリーダーを起動"""
    result = nfc_reader.start_reader()
    return jsonify(result)

@app.route('/api/nfc/stop', methods=['POST'])
def stop_nfc_reader():
    """NFCリーダーを停止"""
    result = nfc_reader.stop_reader()
    return jsonify(result)

@app.route('/api/nfc/set-action', methods=['POST'])
def set_nfc_action():
    """NFCリーダーのアクション（借りる/返す）を設定"""
    try:
        data = request.json
        action = data.get('action')
        
        if not action or action not in ['borrow', 'return']:
            return jsonify({'error': '無効なアクションです'}), 400
        
        # NFCリーダーにアクションを設定
        result = nfc_reader.set_action(action)
        
        if result:
            return jsonify({'status': 'success', 'action': action})
        else:
            return jsonify({'status': 'error', 'message': '無効なアクションです'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/nfc/restart', methods=['POST'])
def restart_nfc_reader():
    """NFCリーダーを再起動"""
    result = nfc_reader.restart_reader()
    return jsonify(result)

# WebSocketイベントハンドラの追加
@socketio.on('request_nfc_restart')
def handle_nfc_restart_request(data):
    """クライアントからのNFCリーダー再起動リクエストを処理"""
    reason = data.get('reason', 'client_request')
    print(f"NFCリーダー再起動リクエスト受信: {reason}")
    
    # リーダーを再起動
    result = nfc_reader.restart_reader()
    
    # 再起動の結果をクライアントに通知
    return {'status': result['status'], 'message': 'NFCリーダーを再起動しました'}

# 傘管理 APIエンドポイント

@app.route('/api/umbrella/status/<student_id>', methods=['GET'])
def get_umbrella_status(student_id):
    """学生の傘貸出状態を取得"""
    try:
        status = umbrella_service.check_student_status(student_id)
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/umbrella/borrow', methods=['POST'])
def borrow_umbrella():
    """傘を借りる"""
    try:
        data = request.json
        student_id = data.get('student_id')
        
        if not student_id:
            return jsonify({'error': '学籍番号が必要です'}), 400
            
        result = umbrella_service.borrow_umbrella(student_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/umbrella/return', methods=['POST'])
def return_umbrella():
    """傘を返却する"""
    try:
        data = request.json
        student_id = data.get('student_id')
        
        if not student_id:
            return jsonify({'error': '学籍番号が必要です'}), 400
            
        result = umbrella_service.return_umbrella(student_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/umbrella/history/<student_id>', methods=['GET'])
def get_student_history(student_id):
    """学生の傘貸出履歴を取得"""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = umbrella_service.get_student_history(student_id, limit)
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/umbrella/recent', methods=['GET'])
def get_recent_activities():
    """最近の活動履歴を取得"""
    try:
        limit = request.args.get('limit', 20, type=int)
        activities = umbrella_service.get_recent_activities(limit)
        return jsonify(activities)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """ヘルスチェック"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # サーバー起動
    socketio.run(app, host='0.0.0.0', port=5050, debug=Config.DEBUG)