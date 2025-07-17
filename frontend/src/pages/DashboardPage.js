// File: frontend/src/pages/DashboardPage.js

import React, { useState } from 'react';
import { useEffect } from 'react';
import useAuthStore from '../store/authStore';
import { useNavigate, Link } from 'react-router-dom';
import SearchBar from '../components/SearchBar';
import SearchResults from '../components/SearchResults';
import api from '../services/api';

const DashboardPage = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const navigate = useNavigate();
  const [searchResults, setSearchResults] = useState([]);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [hasMoreResults, setHasMoreResults] = useState(false);
  const [currentQuery, setCurrentQuery] = useState('');

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

  const handleSearchResults = (results, isNewSearch = true, query = '') => {
    if (isNewSearch) {
      setSearchResults(results);
      setShowSearchResults(true);
      setHasMoreResults(results.length === 20); // If we got 20 results, there might be more
      setCurrentQuery(query); // Store the current search query
    } else {
      // Append new results to existing ones
      setSearchResults(prev => [...prev, ...results]);
      setHasMoreResults(results.length === 20); // If we got 20 results, there might be more
    }
  };

  const handleShowMore = async () => {
    if (!currentQuery.trim()) return;
    
    try {
      // Calculate the next offset based on current results
      const nextOffset = searchResults.length;
      const response = await api.get('/core/ebay-search/', {
        params: {
          q: currentQuery.trim(),
          limit: 20,
          offset: nextOffset
        }
      });
      
      setSearchResults(prev => [...prev, ...response.data]);
      setHasMoreResults(response.data.length === 20); // If we got 20 results, there might be more
    } catch (error) {
      console.error('Failed to load more results:', error);
    } finally {
    }
  };

  const handleAddToInventory = (newItem) => {
    // Show success message and clear search results
    setShowSearchResults(false);
    setSearchResults([]);
    // You could add a toast notification here
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
        />
        
        {showSearchResults && searchResults.length > 0 && (
          <SearchResults 
            results={searchResults}
            onAddToInventory={handleAddToInventory}
            onShowMore={handleShowMore}
            hasMoreResults={hasMoreResults}
          />
        )}
      </section>
      
      <hr style={dividerStyle}/>
      
      {/* Quick Actions Section */}
      <section style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h2 style={searchTitleStyle}>Quick Actions</h2>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link to="/inventory" style={{ textDecoration: 'none' }}>
            <button style={{
              backgroundColor: 'var(--primary-color)',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '8px',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}>
              Manage Inventory
            </button>
          </Link>
          <Link to="/listings" style={{ textDecoration: 'none' }}>
            <button style={{
              backgroundColor: 'var(--surface-color)',
              color: 'var(--text-primary)',
              border: '1px solid var(--border-color)',
              padding: '12px 24px',
              borderRadius: '8px',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}>
              View Listings
            </button>
          </Link>
        </div>
      </section>
    </div>
  );
};

export default DashboardPage;