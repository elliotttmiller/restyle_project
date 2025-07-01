// File: frontend/src/components/AddListingForm.js

import React, { useState } from 'react';
import api from '../services/api';
import './Form.css';

const AddListingForm = ({ item, onAddListing, onCancel }) => {
  const [formData, setFormData] = useState({
    platform: 'EBAY',
    list_price: '',
    listing_type: 'FIXED',
    duration: 'GTC',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await api.post(`/core/items/${item.id}/listings/`, formData);
      onAddListing(response.data);
    } catch (err) {
      // --- THIS IS THE CORRECTED ERROR HANDLING BLOCK ---
      const errorData = err.response?.data;
      if (errorData) {
        // If the error is a single string (like from our custom validation)
        if (typeof errorData === 'string') {
          setError(errorData);
        } else if (errorData.detail) {
          setError(errorData.detail);
        }
        else {
          // If the error is an object of field errors (like from DRF defaults)
          const errorMessages = Object.entries(errorData)
            .map(([key, value]) => {
              // Ensure value is an array before trying to join it
              const messages = Array.isArray(value) ? value.join(', ') : value;
              return `${key}: ${messages}`;
            })
            .join('; ');
          setError(errorMessages);
        }
      } else {
        setError('Failed to create listing. An unknown error occurred.');
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container" style={{paddingTop: 0}}>
      <form onSubmit={handleSubmit} className="form-card">
        <h2>List "{item.title}" on eBay</h2>
        
        <div className="form-group">
          <label htmlFor="listing_type">Listing Type</label>
          <select name="listing_type" value={formData.listing_type} onChange={handleChange} required disabled={loading}>
            <option value="FIXED">Fixed Price</option>
            <option value="AUCTION">Auction</option>
          </select>
        </div>
        
        <div className="form-group">
          <label htmlFor="list_price">Starting Price ($)</label>
          <input name="list_price" type="number" step="0.01" value={formData.list_price} onChange={handleChange} required disabled={loading} />
        </div>
        
        <div className="form-group">
          <label htmlFor="duration">Duration</label>
          <select name="duration" value={formData.duration} onChange={handleChange} required disabled={loading}>
            <option value="Days_3">3 Days</option>
            <option value="Days_5">5 Days</option>
            <option value="Days_7">7 Days</option>
            <option value="Days_10">10 Days</option>
            <option value="GTC">Good 'Til Canceled</option>
          </select>
        </div>

        {error && <p className="form-error">{error}</p>}
        
        <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
          <button type="button" onClick={onCancel} disabled={loading} style={{ backgroundColor: 'var(--text-secondary)'}}>Cancel</button>
          <button type="submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create Listing'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AddListingForm;