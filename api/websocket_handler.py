def register_websocket_handlers(socketio, nfc_reader):
    """WebSocketイベントハンドラを登録する"""
    
    @socketio.on('connect')
    def handle_connect():
        """クライアント接続時の処理"""
        print('クライアント接続')
        # 現在のNFCリーダーの状態を送信
        socketio.emit('nfc_status', {
            'active': nfc_reader.is_active(),
            'processing': nfc_reader.is_processing(),
            'last_tag_read': nfc_reader.get_last_tag_read()
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """クライアント切断時の処理"""
        print('クライアント切断')
    
    @socketio.on('request_nfc_restart')
    def handle_restart_request(data):
        """NFCリーダー再起動リクエスト処理"""
        reason = data.get('reason', 'client_request')
        print(f"NFCリーダー再起動リクエスト: {reason}")
        
        # リーダーを再起動
        result = nfc_reader.restart_reader()
        
        # 再起動の結果をクライアントに通知
        return {'status': result['status'], 'message': 'NFCリーダーを再起動しました'}