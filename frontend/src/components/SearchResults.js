import React, { useState } from 'react';
import api from '../services/api';
import './SearchResults.css';

const SearchResults = ({ results, onAddToInventory, onLoading }) => {
  const [addingItems, setAddingItems] = useState(new Set());
  const [message, setMessage] = useState('');

  const handleAddToInventory = async (item) => {
    setAddingItems(prev => new Set(prev).add(item.itemId));
    onLoading && onLoading(true);

    try {
      // Extract relevant data from eBay item
      const itemData = {
        title: item.title,
        brand: extractBrand(item.title),
        size: extractSize(item.title) || 'Unknown',
        color: extractColor(item.title) || 'Unknown',
        condition: item.condition?.[0]?.conditionDisplayName || 'Used',
        ebay_item_id: item.itemId,
        image_url: item.image?.imageUrl || '',
        current_price: parseFloat(item.price?.value || '0'),
        currency: item.price?.currency || 'USD'
      };

      const response = await api.post('/core/items/', itemData);
      
      onAddToInventory && onAddToInventory(response.data);
      setMessage(`Successfully added "${itemData.title}" to your inventory!`);
      
      // Clear message after 3 seconds
      setTimeout(() => setMessage(''), 3000);
      
    } catch (err) {
      console.error('Failed to add item to inventory:', err);
      setMessage(err.response?.data?.error || 'Failed to add item to inventory. Please try again.');
    } finally {
      setAddingItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(item.itemId);
        return newSet;
      });
      onLoading && onLoading(false);
    }
  };

  const extractBrand = (title) => {
    const commonBrands = ['Nike', 'Adidas', 'Jordan', 'Apple', 'Samsung', 'Sony', 'Canon', 'Nikon', 'Levi\'s', 'Calvin Klein'];
    const titleLower = title.toLowerCase();
    
    for (const brand of commonBrands) {
      if (titleLower.includes(brand.toLowerCase())) {
        return brand;
      }
    }
    return 'Unknown';
  };

  const extractSize = (title) => {
    const sizePatterns = [
      /\b(XS|S|M|L|XL|XXL|XXXL)\b/i,
      /\b(\d{1,2})\s*(US|UK|EU|CM|INCH|")\b/i,
      /\b(\d{1,2}\.\d{1,2})\s*(US|UK|EU|CM|INCH|")\b/i
    ];
    
    for (const pattern of sizePatterns) {
      const match = title.match(pattern);
      if (match) {
        return match[0];
      }
    }
    return null;
  };

  const extractColor = (title) => {
    const colorPatterns = [
      /\b(Black|White|Red|Blue|Green|Yellow|Purple|Pink|Orange|Brown|Grey|Gray|Silver|Gold|Navy|Beige|Cream)\b/i
    ];
    
    for (const pattern of colorPatterns) {
      const match = title.match(pattern);
      if (match) {
        return match[1];
      }
    }
    return null;
  };

  const formatPrice = (price) => {
    if (!price || !price.value) return 'Price not available';
    return `$${parseFloat(price.value).toFixed(2)} ${price.currency || 'USD'}`;
  };

  if (!results || results.length === 0) {
    return (
      <div className="search-results">
        <div className="no-results">
          <h3>No Results Found</h3>
          <p>Try adjusting your search terms or browse different categories.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="search-results">
      {message && (
        <div className="search-message">
          {message}
        </div>
      )}
      
      <div className="search-results-header">
        <h3 className="search-results-title">eBay Search Results</h3>
        <span className="search-results-count">{results.length} items found</span>
      </div>
      
      <div className="search-results-grid">
        {results.map((item) => (
          <div key={item.itemId} className="search-result-card">
            <div className="result-image">
              {item.image?.imageUrl ? (
                <img 
                  src={item.image.imageUrl} 
                  alt={item.title}
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
              ) : null}
              <div className="no-image">No Image</div>
            </div>
            
            <div className="result-content">
              <h4 className="result-title">{item.title}</h4>
              
              <div className="result-details">
                <div className="result-price">
                  {formatPrice(item.price)}
                </div>
                
                {item.condition && (
                  <div className="result-condition">
                    Condition: {item.condition[0]?.conditionDisplayName || 'Unknown'}
                  </div>
                )}
                
                {item.shippingCost && (
                  <div className="result-shipping">
                    Shipping: {formatPrice(item.shippingCost)}
                  </div>
                )}
              </div>
              
              <div className="result-actions">
                <button
                  className="add-to-inventory-btn"
                  onClick={() => handleAddToInventory(item)}
                  disabled={addingItems.has(item.itemId)}
                >
                  {addingItems.has(item.itemId) ? 'Adding...' : 'Add to Inventory'}
                </button>
                
                <a 
                  href={item.itemWebUrl} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="view-on-ebay-btn"
                >
                  View on eBay
                </a>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SearchResults; 