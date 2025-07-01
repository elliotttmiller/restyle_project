// File: frontend/src/components/AddListingForm.js

import React, { useState } from 'react';
import api from '../services/api';
import './Form.css'; // We can reuse our existing form styles

const AddListingForm = ({ item, onAddListing, onCancel }) => {
  const [formData, setFormData] = useState({
    platform: 'EBAY', // Default to eBay
    list_price: '',
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
      // In a real sprint, this would call the API. For now, it's mocked.
      console.log(`MOCK: Creating listing for item ${item.id} with data:`, formData);
      
      // This is the real API call we would make in the future:
      // const response = await api.post(`/core/items/${item.id}/listings/`, formData);
      
      // We will simulate the response for the UI to update
      const mockResponseData = {
          id: Math.floor(Math.random() * 10000), // Fake ID
          ...formData,
          item: item.id,
          is_active: true, // Assume it's active on creation
      };
      
      onAddListing(mockResponseData); // Pass the new mock listing back to the parent
    } catch (err) {
      setError('Failed to create listing.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container" style={{paddingTop: 0}}>
      <form onSubmit={handleSubmit} className="form-card">
        <h2>List "{item.title}" on a Platform</h2>
        
        <div className="form-group">
          <label htmlFor="platform">Platform</label>
          <select name="platform" value={formData.platform} onChange={handleChange} required disabled={loading}>
            <option value="EBAY">eBay</option>
            <option value="ETSY">Etsy</option>
            <option value="POSH">Poshmark</option>
            <option value="DEPOP">Depop</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="list_price">List Price ($)</label>
          <input 
            id="list_price"
            name="list_price" 
            type="number" 
            step="0.01" 
            placeholder="0.00" 
            value={formData.list_price} 
            onChange={handleChange} 
            required 
            disabled={loading} 
          />
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