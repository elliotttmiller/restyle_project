// File: frontend/src/pages/DashboardPage.js

import React from 'react';
import { useEffect } from 'react';
import useAuthStore from '../store/authStore';
import { useNavigate } from 'react-router-dom';
import ItemList from '../components/ItemList';

const DashboardPage = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const navigate = useNavigate();

  useEffect(() => {
    // This is a protected route. If the user is not authenticated,
    // redirect them to the login page.
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  // If not authenticated, we render nothing to avoid a flash of content
  // before the redirect happens.
  if (!isAuthenticated) {
    return null; 
  }

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Welcome to your Re-Style dashboard. Here you can manage your inventory and analyze market prices.</p>
      <hr style={{ margin: '2rem 0', borderColor: 'var(--border-color)'}}/>
      <ItemList />
    </div>
  );
};

export default DashboardPage;