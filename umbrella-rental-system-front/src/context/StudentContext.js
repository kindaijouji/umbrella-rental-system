import React, { createContext, useState, useContext } from 'react';

const StudentContext = createContext();

export const StudentProvider = ({ children }) => {
    const [studentId, setStudentId] = useState(null);
    const [lastAction, setLastAction] = useState({
        id: null,
        action: null,
        timestamp: null
    });

    return (
        <StudentContext.Provider value={{
            studentId,
            setStudentId,
            lastAction,
            setLastAction
        }}>
            {children}
        </StudentContext.Provider>
    );
};

export const useStudent = () => useContext(StudentContext);