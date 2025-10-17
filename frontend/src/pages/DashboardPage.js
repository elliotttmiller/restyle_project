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
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  if (!isAuthenticated) {
    return null; 
  }

  const handleSearchResults = (results, isNewSearch = true, query = '') => {
    if (isNewSearch) {
      setSearchResults(results);
      setShowSearchResults(true);
      setHasMoreResults(results.length === 20);
      setCurrentQuery(query);
    } else {
      setSearchResults(prev => [...prev, ...results]);
      setHasMoreResults(results.length === 20);
    }
  };

  const handleShowMore = async () => {
    if (!currentQuery.trim()) return;
    
    try {
      const nextOffset = searchResults.length;
      const response = await api.get('/core/ebay-search/', {
        params: {
          q: currentQuery.trim(),
          limit: 20,
          offset: nextOffset
        }
      });
      
      setSearchResults(prev => [...prev, ...response.data]);
      setHasMoreResults(response.data.length === 20);
    } catch (error) {
      console.error('Failed to load more results:', error);
    }
  };

  const handleAddToInventory = (newItem) => {
    setShowSearchResults(false);
    setSearchResults([]);
  };

  const pageStyle = {
    maxWidth: '1400px',
    margin: '0 auto',
    padding: '3rem 2rem',
    minHeight: 'calc(100vh - 80px)',
  };

  const heroStyle = {
    textAlign: 'center',
    marginBottom: '4rem',
    padding: '3rem 0',
    animation: 'fadeIn 0.8s ease-out',
  };

  const titleStyle = {
    fontSize: 'clamp(2.5rem, 5vw, 4rem)',
    fontWeight: '900',
    marginBottom: '1rem',
    background: 'var(--primary-gradient)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    letterSpacing: '-0.03em',
    lineHeight: '1.1',
  };

  const subtitleStyle = {
    fontSize: 'clamp(1.1rem, 2vw, 1.35rem)',
    color: 'var(--text-secondary)',
    marginBottom: '2.5rem',
    maxWidth: '700px',
    margin: '0 auto 2.5rem',
    lineHeight: '1.7',
    fontWeight: '400',
  };

  const statsContainerStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '1.5rem',
    marginBottom: '3rem',
  };

  const statCardStyle = {
    background: 'var(--surface-glass)',
    backdropFilter: 'blur(20px)',
    border: '1px solid var(--glass-border)',
    borderRadius: 'var(--radius-xl)',
    padding: '2rem',
    textAlign: 'center',
    transition: 'all var(--transition-base)',
    cursor: 'pointer',
  };

  const statNumberStyle = {
    fontSize: '2.5rem',
    fontWeight: '800',
    background: 'var(--primary-gradient)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    marginBottom: '0.5rem',
  };

  const statLabelStyle = {
    fontSize: '0.9rem',
    color: 'var(--text-muted)',
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  };

  const searchSectionStyle = {
    background: 'var(--surface-glass)',
    backdropFilter: 'blur(20px)',
    border: '1px solid var(--glass-border)',
    borderRadius: 'var(--radius-2xl)',
    padding: '3rem',
    marginBottom: '3rem',
    boxShadow: 'var(--shadow-xl)',
  };

  const searchTitleStyle = {
    fontSize: '1.75rem',
    fontWeight: '700',
    color: 'var(--text-primary)',
    marginBottom: '1.5rem',
    textAlign: 'center',
  };

  const quickActionsStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '1.5rem',
    marginTop: '3rem',
  };

  const actionCardStyle = {
    background: 'var(--surface-glass)',
    backdropFilter: 'blur(20px)',
    border: '1px solid var(--glass-border)',
    borderRadius: 'var(--radius-xl)',
    padding: '2rem',
    textAlign: 'center',
    transition: 'all var(--transition-base)',
    cursor: 'pointer',
    textDecoration: 'none',
    display: 'block',
  };

  const actionIconStyle = {
    fontSize: '3rem',
    marginBottom: '1rem',
    filter: 'drop-shadow(0 4px 12px rgba(102, 126, 234, 0.3))',
  };

  const actionTitleStyle = {
    fontSize: '1.25rem',
    fontWeight: '700',
    color: 'var(--text-primary)',
    marginBottom: '0.5rem',
  };

  const actionDescStyle = {
    fontSize: '0.9rem',
    color: 'var(--text-muted)',
    lineHeight: '1.6',
  };

  return (
    <div style={pageStyle}>
      <div style={heroStyle}>
        <h1 style={titleStyle}>
          Welcome to Restyle.ai
        </h1>
        <p style={subtitleStyle}>
          Your AI-powered fashion marketplace assistant. Search, analyze, and discover the best deals on eBay with cutting-edge AI technology.
        </p>
        
        <div style={statsContainerStyle}>
          <div 
            style={statCardStyle}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)';
              e.currentTarget.style.boxShadow = 'var(--shadow-primary)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <div style={statNumberStyle}>0</div>
            <div style={statLabelStyle}>Items Analyzed</div>
          </div>
          <div 
            style={statCardStyle}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)';
              e.currentTarget.style.boxShadow = 'var(--shadow-primary)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <div style={statNumberStyle}>0</div>
            <div style={statLabelStyle}>Searches</div>
          </div>
          <div 
            style={statCardStyle}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)';
              e.currentTarget.style.boxShadow = 'var(--shadow-primary)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <div style={statNumberStyle}>0</div>
            <div style={statLabelStyle}>In Inventory</div>
          </div>
        </div>
      </div>
      
      {/* eBay Search Section */}
      <section style={searchSectionStyle}>
        <h2 style={searchTitleStyle}>🔍 Search eBay Marketplace</h2>
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
      
      {/* Quick Actions */}
      <div style={quickActionsStyle}>
        <Link 
          to="/inventory" 
          style={actionCardStyle}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-6px) scale(1.02)';
            e.currentTarget.style.boxShadow = 'var(--shadow-primary)';
            e.currentTarget.style.borderColor = 'var(--primary-color)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0) scale(1)';
            e.currentTarget.style.boxShadow = 'none';
            e.currentTarget.style.borderColor = 'var(--glass-border)';
          }}
        >
          <div style={actionIconStyle}>📦</div>
          <div style={actionTitleStyle}>Manage Inventory</div>
          <div style={actionDescStyle}>
            View and manage all your items in one place
          </div>
        </Link>
        
        <Link 
          to="/listings" 
          style={actionCardStyle}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-6px) scale(1.02)';
            e.currentTarget.style.boxShadow = 'var(--shadow-primary)';
            e.currentTarget.style.borderColor = 'var(--primary-color)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0) scale(1)';
            e.currentTarget.style.boxShadow = 'none';
            e.currentTarget.style.borderColor = 'var(--glass-border)';
          }}
        >
          <div style={actionIconStyle}>📊</div>
          <div style={actionTitleStyle}>View Listings</div>
          <div style={actionDescStyle}>
            Browse all your active marketplace listings
          </div>
        </Link>
        
        <div 
          style={actionCardStyle}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-6px) scale(1.02)';
            e.currentTarget.style.boxShadow = 'var(--shadow-primary)';
            e.currentTarget.style.borderColor = 'var(--primary-color)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0) scale(1)';
            e.currentTarget.style.boxShadow = 'none';
            e.currentTarget.style.borderColor = 'var(--glass-border)';
          }}
        >
          <div style={actionIconStyle}>🤖</div>
          <div style={actionTitleStyle}>AI Analysis</div>
          <div style={actionDescStyle}>
            Get instant AI-powered price recommendations
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;