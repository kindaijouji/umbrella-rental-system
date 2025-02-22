import React from 'react';
import { Umbrella, ArrowLeftRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useStudent } from '../context/StudentContext';
import { useEffect } from 'react';

const Home = () => {
    const navigate = useNavigate();
    const { setStudentId } = useStudent();
    useEffect(() => {
        setStudentId(null);
    }, [setStudentId]);
    return (

        <div className="min-h-screen w-screen bg-gray-100 flex items-center justify-center">
            <div className="w-full lg:w-[567px] mx-4">

                <div className="bg-white rounded-2xl shadow-lg lg:h-[264px] p-6">
                    <div className="text-center mb-6">
                        <h1 className="text-2xl font-bold text-gray-800">傘貸し出し</h1>
                        <p className="text-gray-600 mt-2">学生証をタッチしといてください</p>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <button onClick={() => navigate('/nfc/borrow')} className="
              bg-gradient-to-br from-blue-500 to-blue-600 
              text-white rounded-xl p-4 
              hover:from-blue-600 hover:to-blue-700 
              transition-all duration-200 
              shadow-md hover:shadow-lg
            ">
                            <div className="flex flex-col items-center">
                                <Umbrella size={32} className="mb-2" />
                                <span className="text-lg font-medium">借りる</span>
                            </div>
                        </button>

                        <button onClick={() => navigate('/nfc/return')} className="
              bg-gradient-to-br from-green-500 to-green-600 
              text-white rounded-xl p-4 
              hover:from-green-600 hover:to-green-700 
              transition-all duration-200 
              shadow-md hover:shadow-lg
            ">
                            <div className="flex flex-col items-center">
                                <ArrowLeftRight size={32} className="mb-2" />
                                <span className="text-lg font-medium">返す</span>
                            </div>
                        </button>
                    </div>
                    <div className="mt-4 text-center text-sm text-gray-500">
                        近畿大学情報学部自治会
                    </div>

                </div>
            </div>
        </div>
    );
};

export default Home;