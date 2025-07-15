import React, { useState } from 'react';
import api from '../services/api';
import './SearchBar.css';

const SearchBar = ({ onSearchResults, onLoading }) => {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState('');
  const [currentOffset, setCurrentOffset] = useState(0);

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a search term');
      return;
    }

    setIsSearching(true);
    setError('');
    setCurrentOffset(0); // Reset offset for new search
    onLoading && onLoading(true);

    try {
      const response = await api.get('/core/ebay-search/', {
        params: { 
          q: query.trim(),
          limit: 20,
          offset: 0
        }
      });
      
      setCurrentOffset(0); // Reset offset for new search
      onSearchResults && onSearchResults(response.data, true, query.trim()); // true = new search, pass query
    } catch (err) {
      console.error('Search failed:', err);
      setError(err.response?.data?.error || 'Search failed. Please try again.');
    } finally {
      setIsSearching(false);
      onLoading && onLoading(false);
    }
  };



  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch(e);
    }
  };

  return (
    <div className="search-container">
      <form onSubmit={handleSearch} className="search-form">
        <div className="search-input-group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Search eBay for items (e.g., 'Nike Air Jordan', 'iPhone 13')"
            className="search-input"
            disabled={isSearching}
          />
          <button 
            type="submit" 
            className="search-button"
            disabled={isSearching}
          >
            {isSearching ? (
              <span className="search-spinner">🔍</span>
            ) : (
              'Search'
            )}
          </button>
        </div>
      </form>
      
      {error && (
        <div className="search-error">
          {error}
        </div>
      )}
      
      {isSearching && (
        <div className="search-loading">
          Searching eBay...
        </div>
      )}
      
      {/* Show More button moved to SearchResults component */}
    </div>
  );
};

export default SearchBar; 