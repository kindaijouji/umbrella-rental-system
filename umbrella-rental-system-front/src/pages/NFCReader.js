import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { CreditCard } from 'lucide-react';
import { useStudent } from '../context/StudentContext';
import io from 'socket.io-client';

// バックエンドのWebSocket URL
const SOCKET_URL = 'http://localhost:5050';
// WebSocket接続
const socket = io(SOCKET_URL);

const NFCReader = () => {
    const navigate = useNavigate();
    const { action } = useParams();
    const {
        studentId,
        setStudentId,
        lastAction,
        setLastAction
    } = useStudent();

    // 状態管理
    const [error, setError] = useState(null);
    const [waitTime, setWaitTime] = useState(0);
    const [isReading, setIsReading] = useState(false);
    const [readerStatus, setReaderStatus] = useState('待機中');
    const [readProgress, setReadProgress] = useState(0);
    const [verificationStatus, setVerificationStatus] = useState('');

    // アクションをNFCリーダーに送信
    const sendActionToReader = useCallback(async () => {
        try {
            const response = await fetch(`http://localhost:5000/api/nfc/set-action`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ action }),
            });
            const data = await response.json();
            console.log('アクション設定結果:', data);
        } catch (err) {
            console.error('アクション設定エラー:', err);
        }
    }, [action]);

    // 成功時の処理
    const handleSuccess = useCallback((result) => {
        // resultからステータスに基づいて異なる処理を行う
        if (action === 'borrow') {
            if (result && result.status === 'already_borrowed') {
                setError('既に傘を借りています。');
                return false;
            }
            navigate('/borrow');
            return true;
        } else if (action === 'return') {
            if (result && result.status === 'not_borrowed') {
                setError('借りている傘がありません。');
                return false;
            }
            navigate('/return');
            return true;
        }
        return false;
    }, [action, navigate]);

    // WebSocket イベントリスナーの設定
    useEffect(() => {
        // NFCステータス更新
        socket.on('nfc_status', (data) => {
            console.log('NFCステータス更新:', data);
            setIsReading(data.active);
            
            if (data.last_tag_read) {
                // タグ読み取り後の処理
                handleTagRead(data.last_tag_read);
            }
        });

        socket.on('nfc_status_update', (data) => {
            console.log('NFCステータス通知:', data);
            setReaderStatus(data.message);
        });

        socket.on('nfc_tag_read', (tagData) => {
            console.log('NFCタグ読み取り:', tagData);
            // タグ読み取り時の処理
            handleTagRead(tagData);
        });

        socket.on('nfc_error', (errorData) => {
            console.error('NFCエラー:', errorData);
            setError(errorData.error || 'カードの読み取りに失敗しました');
            setIsReading(false);
        });

        socket.on('processing_update', (updateData) => {
            console.log('処理更新:', updateData);
            
            // 進捗状況を更新
            setReadProgress(updateData.progress || 0);
            setReaderStatus(updateData.message || '処理中...');
            
            if (updateData.status === 'in_progress') {
                setVerificationStatus('学生情報を確認中...');
            } else if (updateData.status === 'completed') {
                if (updateData.result && updateData.result.student_id) {
                    // 処理成功時の処理
                    const success = handleSuccess(updateData.result);
                    if (!success) {
                        setIsReading(false);
                    }
                }
            } else if (updateData.status === 'error') {
                setError(updateData.message || 'エラーが発生しました');
                setIsReading(false);
            }
        });

        // クリーンアップ関数
        return () => {
            socket.off('nfc_status');
            socket.off('nfc_status_update');
            socket.off('nfc_tag_read');
            socket.off('nfc_error');
            socket.off('processing_update');
        };
    }, [handleSuccess, handleTagRead]);

    // タグ読み取り時の処理
    const handleTagRead = useCallback((tagData) => {
        if (tagData.student_id && tagData.student_id !== "unknown") {
            const now = Date.now();
            const timePassed = !lastAction?.timestamp ||
                (now - lastAction.timestamp) > 3000;

            if (timePassed) {
                setStudentId(tagData.student_id);
                setLastAction({
                    id: tagData.student_id,
                    action: action,
                    timestamp: now
                });
                
                // 処理成功を待機（WebSocketの processing_update イベントを待つ）
                setVerificationStatus('学生情報を確認中...');
            } else {
                setError('同じカードは連続して読み取れません。しばらくお待ちください。');
            }
        } else {
            setError('学籍番号の読み取りに失敗しました。もう一度お試しください。');
        }
    }, [action, lastAction, setLastAction, setStudentId]);

    // カード読み取りの開始
    const startReading = useCallback(async () => {
        if (isReading) return; // 既に読み取り中の場合は新しいリクエストを送らない
        
        try {
            setIsReading(true);
            setError(null);
            setReaderStatus('カードの読み取り準備中...');
            setReadProgress(0);
    
            // アクションを設定
            await sendActionToReader();
    
            // リーダー起動APIを呼び出し
            const response = await fetch('http://localhost:5000/api/nfc/start', {
                method: 'POST',
            });
            const data = await response.json();
    
            if (data.status === 'started' || data.status === 'already_running') {
                setReaderStatus('カードをリーダーにかざしてください');
            } else {
                setError('リーダーの起動に失敗しました');
                setIsReading(false);
            }
        } catch (err) {
            console.error('API error:', err);
            setError('サーバーとの通信に失敗しました');
            setIsReading(false);
        }
    }, [isReading, sendActionToReader]);

    // コンポーネントマウント時に読み取りを開始
    useEffect(() => {
        startReading();
        
        // コンポーネントがアンマウントされる時にリーダーを停止
        return () => {
            fetch('http://localhost:5000/api/nfc/stop', {
                method: 'POST',
            }).catch(err => console.error('リーダー停止エラー:', err));
        };
    }, []); // コンポーネントのマウント時のみ実行

    const handleHome = useCallback(() => {
        setStudentId(null);
        navigate('/');
    }, [navigate, setStudentId]);

    const handleRetry = useCallback(() => {
        if (!isReading) {
            startReading();
        }
    }, [isReading, startReading]);

    // 待機時間の更新
    useEffect(() => {
        if (lastAction?.timestamp) {
            const interval = setInterval(() => {
                const remaining = 3 - Math.floor((Date.now() - lastAction.timestamp) / 1000);
                setWaitTime(remaining > 0 ? remaining : 0);
            }, 100);
            return () => clearInterval(interval);
        }
    }, [lastAction?.timestamp]);

    // 通知音の再生
    useEffect(() => {
        if (studentId) {
            try {
                const audio = new Audio('/sounds/success.mp3');
                audio.play().catch(e => console.log('音声再生エラー:', e));
            } catch (e) {
                console.error('通知音再生エラー:', e);
            }
        }
    }, [studentId]);

    return (
        <div className="min-h-screen w-screen bg-gray-100 flex items-center justify-center">
            <div className="w-full lg:w-[567px] mx-4">
                <div className="bg-white rounded-2xl shadow-lg lg:h-[264px] p-6">
                    <div className="text-center mb-6">
                        <h2 className="text-2xl font-bold text-gray-800">
                            {action === 'borrow' ? '借りる' : '返す'}
                        </h2>
                        <p className="text-gray-600 mt-2">学生証をリーダーにかざしてください</p>
                        <p className="text-sm text-gray-500 mt-1">
                            {isReading ? (
                                <>
                                    {readerStatus}
                                    {readProgress > 0 && readProgress < 100 && (
                                        <span className="ml-2">
                                            ({readProgress}% 完了)
                                        </span>
                                    )}
                                </>
                            ) : (
                                readerStatus
                            )}
                        </p>
                        {verificationStatus && (
                            <p className="text-sm text-blue-500 mt-1">
                                {verificationStatus}
                            </p>
                        )}
                    </div>

                    <div className="flex flex-col items-center justify-center">
                        <div className={`${isReading ? 'animate-pulse' : ''} mb-4 relative`}>
                            <CreditCard size={64} className="text-gray-600" />
                            {readProgress > 0 && readProgress < 100 && (
                                <div className="absolute -bottom-2 left-0 w-full h-1 bg-gray-200 rounded-full">
                                    <div
                                        className="h-full bg-blue-500 rounded-full transition-all duration-300"
                                        style={{ width: `${readProgress}%` }}
                                    />
                                </div>
                            )}
                        </div>

                        {error && (
                            <div className="text-red-500 text-sm mb-4">
                                {error}
                                <button
                                    onClick={handleRetry}
                                    disabled={isReading}
                                    className="ml-2 text-blue-500 hover:text-blue-600 disabled:text-gray-400"
                                >
                                    再試行
                                </button>
                            </div>
                        )}

                        {studentId && (
                            <div className="text-xl font-bold text-gray-900 mb-4">
                                学籍番号: {studentId}
                            </div>
                        )}

                        {waitTime > 0 && (
                            <p className="text-gray-600 mt-2">
                                次の操作まで {waitTime} 秒お待ちください
                            </p>
                        )}

                        <div className="flex gap-4 mt-4">
                            <button
                                onClick={handleHome}
                                className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                            >
                                ホーム
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default NFCReader;