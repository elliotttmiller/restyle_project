// File: frontend/src/App.js

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import AnalysisPage from './pages/AnalysisPage';
import ItemDetailPage from './pages/ItemDetailPage'; // <-- New page is imported
import Navbar from './components/Navbar';

function App() {
  return (
    <Router>
      <Navbar />
      <main style={{ padding: '2rem' }}>
        <Routes>
          {/* Authentication Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          {/* Core Application Routes */}
          <Route path="/item/:itemId/analysis" element={<AnalysisPage />} />
          <Route path="/item/:itemId" element={<ItemDetailPage />} /> {/* <-- New route is added */}
          <Route path="/" element={<DashboardPage />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;