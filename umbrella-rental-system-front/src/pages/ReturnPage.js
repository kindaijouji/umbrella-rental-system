import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { CheckCircle, Umbrella, Home as HomeIcon } from 'lucide-react';
import { useStudent } from '../context/StudentContext';

const ReturnPage = () => {
  const { studentId, setStudentId } = useStudent();
  const navigate = useNavigate();
  // カウントダウンの状態
  const [countdown, setCountdown] = useState(5);
  
  // 学籍番号がない場合はホームにリダイレクト
  useEffect(() => {
    if (!studentId) {
      navigate('/');
    }
  }, [studentId, navigate]);

  // ホームに戻る関数
  const goHome = () => {
    setStudentId(null);
    navigate('/');
  };

  // 5秒カウントダウン後に自動的にホームに戻る
  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prevCount) => {
        if (prevCount <= 1) {
          clearInterval(timer);
          goHome();
          return 0;
        }
        return prevCount - 1;
      });
    }, 1000);

    // クリーンアップ
    return () => clearInterval(timer);
  }, [navigate]);

  return (
    <div className="min-h-screen w-full bg-gray-100 flex items-center justify-center">
      <div className="w-full lg:w-[567px] mx-4">
        <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
          <div className="flex justify-center mb-4 text-green-500">
            <CheckCircle size={64} />
          </div>
          
          <h1 className="text-2xl font-bold text-gray-800 mb-4">
            返却完了
          </h1>
          
          {studentId && (
            <div className="mb-6">
              <p className="text-gray-600">学籍番号</p>
              <p className="text-xl font-semibold">{studentId}</p>
            </div>
          )}
          
          <div className="p-4 bg-green-50 rounded-lg mb-6">
            <div className="flex items-center justify-center text-green-600 mb-2">
              <Umbrella className="mr-2" />
              <span className="font-medium">返却完了</span>
            </div>
            <p className="text-sm text-gray-600">
              傘の返却が完了しました。<br />
              ご利用ありがとうございました。
            </p>
          </div>
          
          <p className="text-gray-500 mb-4">
            {countdown}秒後にホーム画面に戻ります
          </p>
          
          <div className="flex justify-center">
            <button 
              onClick={goHome}
              className="px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors flex items-center gap-2"
            >
              <HomeIcon size={18} />
              <span>ホームに戻る</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReturnPage;