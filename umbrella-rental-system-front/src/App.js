import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home';
import NFCReader from './pages/NFCReader';
import BorrowPage from './pages/BorrowPage';
import ReturnPage from './pages/ReturnPage';
import { StudentProvider } from './context/StudentContext';

const App = () => {
  return (
    <StudentProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/reader/:action" element={<NFCReader />} />
          <Route path="/borrow" element={<BorrowPage />} />
          <Route path="/return" element={<ReturnPage />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Router>
    </StudentProvider>
  );
};

export default App;