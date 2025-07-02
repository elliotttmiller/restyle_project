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
      <div style={{ 
        minHeight: '100vh', 
        backgroundColor: 'var(--background-color)',
        color: 'var(--text-primary)'
      }}>
        <Navbar />
        <main>
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
      </div>
    </Router>
  );
}

export default App;