import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { CreditCard } from 'lucide-react';
import { useStudent } from '../context/StudentContext';

const NFCReader = () => {
    const navigate = useNavigate();
    const { action } = useParams();
    const {
        studentId,
        setStudentId,
        lastAction,
        setLastAction
    } = useStudent();
    const [error, setError] = useState(null);
    const [waitTime, setWaitTime] = useState(0);

    // handleSuccessの定義を上部に移動
    const handleSuccess = useCallback(() => {
        if (action === 'borrow') {
            navigate('/borrow');
        } else if (action === 'return') {
            navigate('/return');
        }
    }, [action, navigate]);

    // handleHomeの定義
    const handleHome = useCallback(() => {
        setStudentId(null);
        navigate('/');
    }, [navigate, setStudentId]);

    useEffect(() => {
        const fetchLatestId = async () => {
            try {
                const response = await fetch('http://localhost:5000/latest-id');
                const data = await response.json();
                const newId = data.student_id;

                if (newId) {
                    const now = Date.now();
                    const timePassed = !lastAction?.timestamp ||
                        (now - lastAction.timestamp) > 3000;

                    if (timePassed) {
                        setStudentId(newId);
                        setLastAction({
                            id: newId,
                            action: action,
                            timestamp: now
                        });
                        handleSuccess();
                    }
                }
            } catch (err) {
                setError('サーバーに接続できません');
            }
        };

        const interval = setInterval(fetchLatestId, 1000);
        return () => clearInterval(interval);
    }, [studentId, handleSuccess, setStudentId, lastAction, action, setLastAction]);

    useEffect(() => {
        if (lastAction?.timestamp) {
            const interval = setInterval(() => {
                const remaining = 3 - Math.floor((Date.now() - lastAction.timestamp) / 1000);
                setWaitTime(remaining > 0 ? remaining : 0);
            }, 100);
            return () => clearInterval(interval);
        }
    }, [lastAction?.timestamp]);

    return (
        <div className="min-h-screen w-screen bg-gray-100 flex items-center justify-center">
            <div className="w-full lg:w-[567px] mx-4">
                <div className="bg-white rounded-2xl shadow-lg lg:h-[264px] p-6">
                    <div className="text-center mb-6">
                        <h2 className="text-2xl font-bold text-gray-800">
                            {action === 'borrow' ? '借りる' : '返す'}
                        </h2>
                        <p className="text-gray-600 mt-2">学生証をリーダーにかざしてください</p>
                    </div>

                    <div className="flex flex-col items-center justify-center">
                        <div className="animate-pulse mb-4">
                            <CreditCard size={64} className="text-gray-600" />
                        </div>

                        {error && (
                            <div className="text-red-500 text-sm mb-4">
                                {error}
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