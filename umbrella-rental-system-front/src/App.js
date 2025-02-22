import Home from "./pages/Home";
import { HashRouter as Router, Routes, Route } from "react-router-dom";
import NFCReader from "./pages/NFCReader";
import BorrowPage from "./pages/BorrowPage";
import ReturnPage from "./pages/ReturnPage";
import { StudentProvider } from "./context/StudentContext";

function App() {
  return (
    <StudentProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/nfc/:action" element={<NFCReader />} />
          <Route path="/borrow" element={<BorrowPage />} />
          <Route path="/return" element={<ReturnPage />} />
        </Routes>
      </Router>
    </StudentProvider>
  );
}

export default App;