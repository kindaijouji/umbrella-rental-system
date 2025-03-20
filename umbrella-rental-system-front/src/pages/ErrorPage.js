import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { AlertCircle, Home } from 'lucide-react';
import { useStudent } from '../context/StudentContext';

const ErrorPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { setStudentId } = useStudent();
  
  // ロケーションのstateからエラーメッセージを取得
  const errorMessage = location.state?.message || '処理できませんでした';
  
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
  }, []);

  return (
    <div className="min-h-screen w-full bg-gray-100 flex items-center justify-center">
      <div className="w-full lg:w-[567px] mx-4">
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <div className="flex flex-col items-center justify-between h-full">
            <div className="text-center flex-1 flex flex-col items-center justify-center mb-6">
              <div className="text-red-500 mb-4">
                <AlertCircle size={48} />
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-4">
                エラー
              </h2>
              <p className="text-red-600 mb-4">
                {errorMessage}
              </p>
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

export default ErrorPage;