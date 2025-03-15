def register_websocket_handlers(socketio, nfc_reader):
    """WebSocketハンドラーを登録する"""
    
    @socketio.on('connect')
    def handle_connect():
        """クライアント接続時のハンドラー"""
        print('クライアント接続')
        
        # 現在の状態をクライアントに送信
        socketio.emit('nfc_status', {
            'active': nfc_reader.is_active(),
            'processing': nfc_reader.is_processing(),
            'last_tag_read': nfc_reader.get_last_tag_read()
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """クライアント切断時のハンドラー"""
        print('クライアント切断')
    
    @socketio.on('request_status')
    def handle_request_status():
        """ステータス要求時のハンドラー"""
        socketio.emit('nfc_status', {
            'active': nfc_reader.is_active(),
            'processing': nfc_reader.is_processing(),
            'last_tag_read': nfc_reader.get_last_tag_read()
        })