import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Umbrella, Home } from 'lucide-react';
import { useStudent } from '../context/StudentContext';

const ActionPage = ({ action }) => {
    // ページ遷移のためのフック
    const navigate = useNavigate();
    // グローバルな学生ID状態を使用
    const { setStudentId } = useStudent();
    // カウントダウンの状態管理（10秒）
    const [countdown, setCountdown] = useState(10);

    // ホームに戻る処理
    const handleHome = () => {
        setStudentId(null);
        navigate('/');
    };

    // カウントダウンタイマーの設定
    useEffect(() => {
        // 1秒ごとにカウントダウンを更新
        const timer = setInterval(() => {
            setCountdown((prev) => {
                // カウントが0になったらホームに戻る
                if (prev <= 1) {
                    handleHome();
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        // コンポーネントのクリーンアップ時にタイマーを解除
        return () => clearInterval(timer);
    }, [handleHome]);



    return (
        <div className="min-h-screen w-screen bg-gray-100 flex items-center justify-center">
            <div className="w-full lg:w-[567px] mx-4">
                <div className="bg-white rounded-2xl shadow-lg lg:h-[264px] p-6">
                    <div className="flex flex-col items-center justify-between h-full">
                        <div className="text-center flex-1 flex flex-col items-center justify-center">
                            <h2 className="text-2xl font-bold text-gray-800 mb-4">
                                {action === 'borrow' ? '傘を1つお取りください' : '傘を返してください'}
                            </h2>
                            <Umbrella size={48} className="text-blue-500 mb-4" />
                            <p className="text-gray-600">
                                {countdown}秒後にホームに戻ります
                            </p>
                        </div>

                        <div className="w-full max-w-xs">
                            <button
                                onClick={handleHome}
                                className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center justify-center gap-2"
                            >
                                <Home size={20} />
                                <span>ホーム</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};


export default ActionPage;