// File: frontend/src/pages/DashboardPage.js

import React, { useState } from 'react';
import { useEffect } from 'react';
import useAuthStore from '../store/authStore';
import { useNavigate } from 'react-router-dom';
import ItemList from '../components/ItemList';
import SearchBar from '../components/SearchBar';
import SearchResults from '../components/SearchResults';

const DashboardPage = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const navigate = useNavigate();
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

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

  const handleSearchResults = (results) => {
    setSearchResults(results);
    setShowSearchResults(true);
  };

  const handleAddToInventory = (newItem) => {
    // Trigger refresh of the item list
    setRefreshTrigger(prev => prev + 1);
    setShowSearchResults(false);
    setSearchResults([]);
  };

  const pageStyle = {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '2rem',
  };

  const headerStyle = {
    marginBottom: '2rem',
    textAlign: 'center',
  };

  const titleStyle = {
    fontSize: '2.5rem',
    fontWeight: '800',
    color: 'var(--text-primary)',
    margin: '0 0 1rem 0',
    background: 'linear-gradient(135deg, var(--primary-color), var(--primary-light))',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    letterSpacing: '-0.025em',
  };

  const subtitleStyle = {
    fontSize: '1.1rem',
    color: 'var(--text-secondary)',
    margin: '0',
    lineHeight: '1.6',
    maxWidth: '600px',
    margin: '0 auto',
  };

  const dividerStyle = {
    margin: '3rem 0',
    border: 'none',
    height: '1px',
    background: 'linear-gradient(90deg, transparent, var(--border-color), transparent)',
  };

  const searchSectionStyle = {
    marginBottom: '3rem',
  };

  const searchTitleStyle = {
    fontSize: '1.5rem',
    fontWeight: '600',
    color: 'var(--text-primary)',
    marginBottom: '1rem',
    textAlign: 'center',
  };

  return (
    <div style={pageStyle}>
      <header style={headerStyle}>
        <h1 style={titleStyle}>Dashboard</h1>
        <p style={subtitleStyle}>
          Welcome to your Re-Style dashboard. Search eBay for items to add to your inventory and analyze market prices with our advanced AI-powered insights.
        </p>
      </header>
      
      <hr style={dividerStyle}/>
      
      {/* eBay Search Section */}
      <section style={searchSectionStyle}>
        <h2 style={searchTitleStyle}>Search eBay for Items</h2>
        <SearchBar 
          onSearchResults={handleSearchResults}
          onLoading={setIsSearching}
        />
        
        {showSearchResults && searchResults.length > 0 && (
          <SearchResults 
            results={searchResults}
            onAddToInventory={handleAddToInventory}
            onLoading={setIsSearching}
          />
        )}
      </section>
      
      <hr style={dividerStyle}/>
      
      {/* Inventory Section */}
      <ItemList refreshTrigger={refreshTrigger} />
    </div>
  );
};

export default DashboardPage;