import React, { useState } from 'react';
import api from '../services/api';
import './SearchResults.css';
import Modal from './Modal';
import '../pages/AnalysisPage.css';

const SearchResults = ({ results, onAddToInventory, onLoading }) => {
  const [addingItems, setAddingItems] = useState(new Set());
  const [message, setMessage] = useState('');
  const [analysisModalOpen, setAnalysisModalOpen] = useState(false);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState('');
  const [analysisData, setAnalysisData] = useState(null);
  const [analysisItem, setAnalysisItem] = useState(null);

  const CONDITION_CHOICES = [
    { value: 'NWT', label: 'New with tags' },
    { value: 'NWOT', label: 'New without tags' },
    { value: 'EUC', label: 'Excellent used condition' },
    { value: 'GUC', label: 'Good used condition' },
    { value: 'Fair', label: 'Fair condition' },
  ];

  const mapEbayConditionToBackend = (ebayCondition) => {
    if (!ebayCondition) return 'GUC';
    const cond = ebayCondition.toLowerCase();
    if (cond.includes('new with tags')) return 'NWT';
    if (cond.includes('new without tags')) return 'NWOT';
    if (cond.includes('excellent')) return 'EUC';
    if (cond.includes('good')) return 'GUC';
    if (cond.includes('fair')) return 'Fair';
    return 'GUC';
  };

  const generateSku = () => {
    return 'SKU-' + Math.random().toString(16).slice(2, 10).toUpperCase();
  };

  const handleAddToInventory = async (item) => {
    setAddingItems(prev => new Set(prev).add(item.itemId));
    onLoading && onLoading(true);

    try {
      // Extract relevant data from eBay item
      const itemData = {
        title: item.title || 'Untitled',
        brand: extractBrand(item.title) || 'Unknown',
        category: item.categoryPath || 'Misc',
        size: extractSize(item.title) || 'Unknown',
        color: extractColor(item.title) || 'Unknown',
        condition: mapEbayConditionToBackend(item.condition?.[0]?.conditionDisplayName),
        sku: generateSku(),
        cost_of_goods: null,
        ebay_category_id: item.categoryId || '',
      };

      const response = await api.post('/core/items/', itemData);
      onAddToInventory && onAddToInventory(response.data);
      setMessage(`Successfully added "${itemData.title}" to your inventory!`);
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

  const handlePriceAnalysis = async (item) => {
    setAnalysisModalOpen(true);
    setAnalysisLoading(true);
    setAnalysisError('');
    setAnalysisData(null);
    setAnalysisItem(item);
    try {
      const payload = {
        title: item.title || '',
        brand: extractBrand(item.title) || '',
        category: item.categoryPath || '',
        size: extractSize(item.title) || '',
        color: extractColor(item.title) || '',
        condition: mapEbayConditionToBackend(item.condition?.[0]?.conditionDisplayName),
      };
      const response = await api.post('/core/price-analysis/', payload);
      setAnalysisData(response.data);
    } catch (err) {
      setAnalysisError('Failed to fetch price analysis.');
    } finally {
      setAnalysisLoading(false);
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
              
              <div className="result-actions" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <button
                  className="add-to-inventory-btn"
                  onClick={() => handleAddToInventory(item)}
                  disabled={addingItems.has(item.itemId)}
                >
                  {addingItems.has(item.itemId) ? 'Adding...' : 'Add to Inventory'}
                </button>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <a 
                  href={item.itemWebUrl} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="view-on-ebay-btn"
                >
                  View on eBay
                </a>
                  <button
                    className="price-analysis-btn add-to-inventory-btn"
                    onClick={() => handlePriceAnalysis(item)}
                  >
                    Price Analysis
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      {/* Price Analysis Modal */}
      {analysisModalOpen && (
        <Modal onClose={() => setAnalysisModalOpen(false)}>
          <div className="analysis-container" style={{ minWidth: 320, maxWidth: 700, height: 800, padding: '2rem', display: 'flex', flexDirection: 'column' }}>
            {/* Title and subtitle */}
            <div style={{ marginBottom: '1.5rem' }}>
              <h1 style={{ fontSize: '1.5rem', margin: 0, textAlign: 'left', fontWeight: 700, lineHeight: 1.2 }}>{analysisItem?.brand || 'Unknown'} {analysisItem?.title}</h1>
              <p className="item-subtitle" style={{ textAlign: 'left', margin: '0.5rem 0 0 0', color: '#666' }}>
                Size: {extractSize(analysisItem?.title) || 'Unknown'} | Color: {extractColor(analysisItem?.title) || 'Unknown'} | Condition: {mapEbayConditionToBackend(analysisItem?.condition?.[0]?.conditionDisplayName)}
              </p>
            </div>
            {/* Stat card */}
            <div className="summary-card" style={{ display: 'flex', justifyContent: 'center', alignItems: 'stretch', gap: '2rem', marginBottom: '2rem', padding: '1.5rem 1rem' }}>
              <div className="stat" style={{ flex: 1, textAlign: 'center' }}>
                <div className="stat-label">Price Range</div>
                <div className="stat-value-small">
                  {analysisData ? `$${analysisData.price_range_low.toFixed(2)} - $${analysisData.price_range_high.toFixed(2)}` : 'N/A'}
                </div>
                  </div>
              <div className="stat" style={{ flex: 1, textAlign: 'center' }}>
                <div className="stat-label">Suggested Price</div>
                <div className="stat-value">
                  {analysisData ? `$${analysisData.suggested_price.toFixed(2)}` : 'N/A'}
                </div>
              </div>
              <div className="stat" style={{ flex: 1, textAlign: 'center' }}>
                <div className="stat-label">Status</div>
                <div className="stat-value-small">
                  <span className={`status-badge ${analysisData?.status === 'COMPLETE' ? 'status-complete' : (analysisData?.status === 'PENDING' || analysisData?.status === 'RUNNING' ? 'status-pending' : 'status-error')}`}>
                    {analysisData?.status || 'NOT STARTED'}
                  </span>
                </div>
              </div>
            </div>
            {/* Comparable Listings */}
            <div style={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column', overflowY: 'auto' }}>
              <h3 style={{ margin: '0 0 1rem 0', fontWeight: 600 }}>Comparable Listings ({analysisData?.comps?.length || 0})</h3>
              {analysisLoading && <p>Loading analysis...</p>}
              {analysisError && <p style={{ color: 'red' }}>{analysisError}</p>}
              {analysisData && analysisData.comps.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    {analysisData.comps.map(comp => (
                    <div key={comp.id} className="comp-card" style={{ display: 'flex', flexDirection: 'row', background: 'var(--surface-color)', border: '1px solid var(--border-color)', borderRadius: 8, overflow: 'hidden', boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.05)', padding: '1rem', minHeight: 180 }}>
                      {/* Image */}
                        {comp.image_url ? (
                        <img src={comp.image_url} alt={comp.title} style={{ width: 140, height: 140, objectFit: 'cover', borderRadius: 8, marginRight: 24 }} />
                      ) : (
                        <div style={{ width: 140, height: 140, background: '#eee', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#888', borderRadius: 8, marginRight: 24 }}>No Image</div>
                      )}
                      {/* Info */}
                      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
                        <div style={{ fontWeight: 600, fontSize: '1.1rem', marginBottom: 4 }}>{comp.title}</div>
                        <div style={{ fontSize: '1rem', color: 'var(--primary-color)', fontWeight: 700, marginBottom: 4 }}>{`$${comp.sold_price.toFixed(2)}`}</div>
                        <div style={{ fontSize: '0.95rem', color: '#555', marginBottom: 4 }}><b>Platform:</b> {comp.platform}</div>
                        {comp.condition && <div style={{ fontSize: '0.95rem', color: '#555', marginBottom: 4 }}><b>Condition:</b> {comp.condition}</div>}
                        {comp.seller && <div style={{ fontSize: '0.95rem', color: '#555', marginBottom: 4 }}><b>Seller:</b> {comp.seller}</div>}
                        {comp.location && <div style={{ fontSize: '0.95rem', color: '#555', marginBottom: 4 }}><b>Location:</b> {comp.location}</div>}
                        {comp.shipping && <div style={{ fontSize: '0.95rem', color: '#555', marginBottom: 4 }}><b>Shipping:</b> {comp.shipping}</div>}
                        <div style={{ marginTop: 'auto', display: 'flex', justifyContent: 'flex-end' }}>
                          <a href={comp.source_url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary-color)', textDecoration: 'underline', fontWeight: 600 }}>View Listing</a>
                        </div>
                      </div>
                      </div>
                    ))}
                  </div>
                ) : (
                <p>No comparable listings found or analysis has not completed.</p>
                )}
              </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default SearchResults; 