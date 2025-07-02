// File: frontend/src/components/AddItemForm.js

import React, { useState } from 'react';
import api from '../services/api';
import './Form.css'; // We can reuse our existing form styles

const CONDITION_CHOICES = [
  { value: 'NWT', label: 'New with tags' },
  { value: 'NWOT', label: 'New without tags' },
  { value: 'EUC', label: 'Excellent used condition' },
  { value: 'GUC', label: 'Good used condition' },
  { value: 'Fair', label: 'Fair condition' },
];

const generateSku = () => {
  // Simple random SKU generator (8 hex chars)
  return 'SKU-' + Math.random().toString(16).slice(2, 10).toUpperCase();
};

const AddItemForm = ({ onAddItem, onCancel }) => {
  // We use an object to hold all form data
  const [formData, setFormData] = useState({
    title: '',
    brand: '',
    category: '',
    size: '',
    color: '',
    condition: 'GUC', // Default to 'Good Used Condition'
    cost_of_goods: '',
    sku: ''
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

    // Ensure required fields are present and valid
    let dataToSubmit = {
      ...formData,
      cost_of_goods: formData.cost_of_goods || null,
      sku: formData.sku || generateSku(),
      category: formData.category || 'Misc',
    };
    // Validate condition value
    if (!CONDITION_CHOICES.some(opt => opt.value === dataToSubmit.condition)) {
      dataToSubmit.condition = 'GUC';
    }

    try {
      const response = await api.post('/core/items/', dataToSubmit);
      onAddItem(response.data); // Pass the new item back to the parent component
    } catch (err) {
      setError('Failed to create item. Please check the fields and try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <form onSubmit={handleSubmit} className="form-card">
        <h2>Add New Inventory Item</h2>
        
        <div className="form-group">
          <label htmlFor="title">Title</label>
          <input name="title" type="text" value={formData.title} onChange={handleChange} required disabled={loading} />
        </div>

        <div className="form-group">
          <label htmlFor="brand">Brand</label>
          <input name="brand" type="text" value={formData.brand} onChange={handleChange} required disabled={loading} />
        </div>

        <div className="form-group">
          <label htmlFor="category">Category</label>
          <input name="category" type="text" placeholder="e.g., Jeans, T-Shirt" value={formData.category} onChange={handleChange} required disabled={loading} />
        </div>

        <div className="form-group">
          <label htmlFor="size">Size</label>
          <input name="size" type="text" value={formData.size} onChange={handleChange} required disabled={loading} />
        </div>

        <div className="form-group">
          <label htmlFor="color">Color</label>
          <input name="color" type="text" value={formData.color} onChange={handleChange} required disabled={loading} />
        </div>

        <div className="form-group">
          <label htmlFor="condition">Condition</label>
          <select name="condition" value={formData.condition} onChange={handleChange} required disabled={loading}>
            {CONDITION_CHOICES.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
        
        <div className="form-group">
          <label htmlFor="cost_of_goods">Cost of Goods ($)</label>
          <input name="cost_of_goods" type="number" step="0.01" placeholder="0.00" value={formData.cost_of_goods} onChange={handleChange} disabled={loading} />
        </div>
        
        <div className="form-group">
          <label htmlFor="sku">SKU (Optional)</label>
          <input name="sku" type="text" value={formData.sku} onChange={handleChange} disabled={loading} />
        </div>

        {error && <p className="form-error">{error}</p>}
        
        <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
          <button type="button" onClick={onCancel} disabled={loading} style={{ backgroundColor: 'var(--text-secondary)'}}>Cancel</button>
          <button type="submit" disabled={loading}>
            {loading ? 'Saving...' : 'Add Item'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AddItemForm;