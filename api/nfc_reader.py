import threading
import time
import re
import nfc
import queue
import json

class NFCReader:
    """NFCリーダーを管理するクラス"""
    
    def __init__(self, socketio, umbrella_service):
        """初期化"""
        self.socketio = socketio
        self.umbrella_service = umbrella_service
        
        # 状態変数
        self.reader_active = False
        self.reader_thread = None
        self.last_tag_read = None
        self.latest_student_id = None
        
        # 処理関連
        self.processing_active = False
        self.processing_thread = None
        self.processing_queue = queue.Queue()
        self.action = None  # 'borrow' または 'return'
    
    def set_action(self, action):
        """アクション（借りる/返す）を設定"""
        if action in ['borrow', 'return']:
            self.action = action
            return True
        return False
    
    def is_active(self):
        """NFCリーダーがアクティブかどうか"""
        return self.reader_active
    
    def is_processing(self):
        """処理中かどうか"""
        return self.processing_active
    
    def get_last_tag_read(self):
        """最後に読み取ったタグ情報"""
        return self.last_tag_read
    
    def start_reader(self):
        """NFCリーダーを起動"""
        if not self.reader_active:
            self.reader_active = True
            self.reader_thread = threading.Thread(target=self._reader_thread_func)
            self.reader_thread.daemon = True
            self.reader_thread.start()
            return {'status': 'started'}
        return {'status': 'already_running'}
    
    def stop_reader(self):
        """NFCリーダーを停止"""
        if self.reader_active:
            self.reader_active = False
            return {'status': 'stopping'}
        return {'status': 'not_running'}
    
    def stop_processing(self):
        """処理を停止"""
        if self.processing_active:
            self.processing_active = False
            return {'status': 'stopping'}
        return {'status': 'not_running'}
    
    def _reader_thread_func(self):
        """NFCリーダースレッドの実行関数"""
        # 再試行の設定
        max_retries = 5
        retry_delay = 1  # 1秒
        retry_count = 0
        
        # NFCリーダー初期化（リトライループ）
        clf = None
        while retry_count < max_retries and self.reader_active:
            try:
                # 再試行中の場合はメッセージを表示
                if retry_count > 0:
                    self._emit_nfc_status_update(
                        'reader_retrying', 
                        f'NFCリーダーの初期化に失敗しました。再試行中 ({retry_count}/{max_retries})...'
                    )
                
                # NFCリーダーの初期化を試みる
                clf = nfc.ContactlessFrontend('usb')
                
                # 成功したらメッセージを表示して再試行ループを抜ける
                self._emit_nfc_status_update('reader_started', 'NFCリーダーを起動しました')
                break
                
            except Exception as e:
                # エラーをログに記録
                print(f"NFCリーダー初期化エラー (試行 {retry_count+1}/{max_retries}): {e}")
                
                # 最後の試行の場合はエラーをクライアントに通知
                if retry_count == max_retries - 1:
                    self._emit_nfc_error(f"NFCリーダーの初期化に失敗しました: {str(e)}")
                    self.reader_active = False
                    return
                
                # リトライ回数を増やしてディレイ
                retry_count += 1
                time.sleep(retry_delay)
        
        # リーダーが停止されたか最大再試行回数に達した場合
        if not clf:
            self.reader_active = False
            return
        
        while self.reader_active:
            try:
                # NFCタグの読み取り待機
                tag = clf.connect(rdwr={'on-connect': self._connected_callback})
                
                if tag and self.last_tag_read:
                    # WebSocketでクライアントにリアルタイム通知
                    self.socketio.emit('nfc_tag_read', self.last_tag_read)
                    
                    # タグ検出後、自動的にリーダーを停止し、処理キューに追加
                    self.reader_active = False
                    self.processing_queue.put(self.last_tag_read)
                    
                    # 学籍番号が取得できた場合としてない場合のメッセージを分ける
                    student_id = self.last_tag_read.get('student_id')
                    if student_id and student_id != "unknown":
                        message = f'学生証を検出しました。学籍番号: {student_id}。処理を開始します。'
                    else:
                        message = 'カードを検出しましたが学籍番号の読み取りに失敗しました。処理を続行します。'
                    
                    self._emit_nfc_status_update('tag_detected', message)
                    
                    # 処理スレッドが実行中でなければ開始
                    self._start_processing_thread()
                    break
                
            except Exception as e:
                print(f"NFCリーダーエラー: {e}")
                self._emit_nfc_error(str(e))
                time.sleep(2)  # エラー時の再試行間隔
        
        # スレッド終了時にリーダーを閉じる
        clf.close()
        self._emit_nfc_status_update('reader_stopped', 'NFCリーダーを停止しました')
    
    def _connected_callback(self, tag):
        """NFCタグが接続された時のコールバック"""
        try:
            tag_id = str(tag.identifier.hex())
            student_id = self._extract_student_id_from_tag(tag)
            
            # タグ情報を保存
            self.last_tag_read = {
                'id': tag_id,
                'timestamp': time.time(),
                'student_id': student_id
            }
            
            return True
        except Exception as e:
            print(f"タグ読み取りエラー: {e}")
            return False
    
    def _extract_student_id_from_tag(self, tag):
        """タグから学籍番号を抽出"""
        try:
            # カードの内容をダンプ（読み取り）します
            dumps = tag.dump()
            
            # System FE00セクションを見つけるためのフラグを初期化します
            fe00_section = False
            
            # ダンプした各行を処理します
            for line in dumps:
                # System FE00セクションの開始を見つけたらフラグを立てます
                if "System FE00" in line:
                    fe00_section = True
                # FE00セクション内で'0000:'で始まる行を見つけたら学籍番号を抽出します
                elif fe00_section and '0000:' in line:
                    numbers = self._extract_12_digit_numbers(line)
                    if numbers:
                        student_id = numbers[0]
                        print("Found student ID:", student_id)
                        return student_id
                # 次のSystemセクションが始まったら処理を終了します
                elif fe00_section and line.startswith("System"):
                    break
            
            return "unknown"
        except Exception as e:
            print(f"学籍番号抽出エラー: {e}")
            return "unknown"
    
    def _extract_12_digit_numbers(self, text):
        """テキストから12桁の数字を抽出"""
        # テキストを'|'で分割し、右側の部分を取り出してスペースを削除します
        # '|'がない場合は元のテキストをそのまま使用します
        ascii_text = text.split('|')[1].strip() if '|' in text else text
        
        # 正規表現を使って12桁の数字を探します
        matches = re.findall(r'\d{12}', ascii_text)
        
        # 見つかった12桁の数字の3桁目以降を返します（最初の2桁を除外）
        return [match[2:] for match in matches]
    
    def _start_processing_thread(self):
        """処理スレッドを開始"""
        if not self.processing_active:
            self.processing_active = True
            self.processing_thread = threading.Thread(target=self._processing_thread_func)
            self.processing_thread.daemon = True
            self.processing_thread.start()
    
    def _processing_thread_func(self):
        """バックエンド処理スレッド関数"""
        self.processing_active = True
        
        while not self.processing_queue.empty() and self.processing_active:
            tag_data = self.processing_queue.get()
            
            try:
                # 処理開始を通知
                self._emit_processing_update('started', 0, '処理を開始しました')
                
                # 学籍番号の有無でメッセージを変える
                student_id = tag_data.get('student_id', 'unknown')
                
                if student_id and student_id != "unknown":
                    # 処理ステップ1 - 学籍番号確認
                    time.sleep(0.5)
                    self._emit_processing_update('in_progress', 25, f'学籍番号 {student_id} の情報を確認中...')
                    
                    # 傘の貸出状態を確認
                    status = self.umbrella_service.check_student_status(student_id)
                    
                    # 処理ステップ2 - 貸出/返却処理
                    time.sleep(0.5)
                    
                    result = None
                    if self.action == 'borrow':
                        # 借りる処理
                        self._emit_processing_update('in_progress', 50, f'傘の貸出処理中...')
                        result = self.umbrella_service.borrow_umbrella(student_id)
                    elif self.action == 'return':
                        # 返す処理
                        self._emit_processing_update('in_progress', 50, f'傘の返却処理中...')
                        result = self.umbrella_service.return_umbrella(student_id)
                    else:
                        # アクションが設定されていない場合
                        self._emit_processing_update('error', 0, 'アクション（借りる/返す）が設定されていません')
                        continue
                    
                    # 処理ステップ3 - 結果確認
                    time.sleep(0.5)
                    self._emit_processing_update('in_progress', 75, '処理結果を確認中...')
                    
                    # 処理完了
                    time.sleep(0.5)
                    
                    if result['success']:
                        # 成功の場合
                        process_result = {
                            'student_id': student_id,
                            'action': self.action,
                            'status': result['status'],
                            'processed_at': time.time(),
                            'result': 'success',
                            'details': result['message']
                        }
                        
                        self._emit_processing_update('completed', 100, result['message'], process_result)
                    else:
                        # 失敗の場合
                        process_result = {
                            'student_id': student_id,
                            'action': self.action,
                            'status': result.get('status', 'error'),
                            'processed_at': time.time(),
                            'result': 'warning',
                            'details': result['message']
                        }
                        
                        self._emit_processing_update('completed', 100, result['message'], process_result)
                else:
                    # 学籍番号が取得できなかった場合の処理
                    time.sleep(1)
                    self._emit_processing_update('error', 0, '学籍番号を読み取れませんでした。もう一度お試しください。')
            
            except Exception as e:
                print(f"処理エラー: {e}")
                self._emit_processing_update('error', 0, f'処理中にエラーが発生しました: {str(e)}')
            
            self.processing_queue.task_done()
        
        self.processing_active = False
    
    # WebSocketイベントヘルパー関数
    
    def _emit_nfc_status_update(self, status, message):
        """NFCリーダーの状態更新を送信"""
        self.socketio.emit('nfc_status_update', {
            'status': status,
            'message': message
        })
    
    def _emit_nfc_error(self, error):
        """NFCエラーイベントを送信"""
        self.socketio.emit('nfc_error', {'error': str(error)})
    
    def _emit_processing_update(self, status, progress, message, result=None):
        """処理更新イベントを送信"""
        data = {
            'status': status,
            'progress': progress,
            'message': message
        }
        if result:
            data['result'] = result
        self.socketio.emit('processing_update', data)