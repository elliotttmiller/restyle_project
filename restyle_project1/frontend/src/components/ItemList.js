// File: frontend/src/components/ItemList.js

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import Modal from './Modal'; // Import the Modal
import AddItemForm from './AddItemForm'; // Import the Form
import './Card.css';

const ItemList = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false); // State to control the modal

  const fetchItems = () => {
    api.get('/core/items/')
      .then(response => {
        setItems(response.data);
      })
      .catch(err => {
        console.error("Failed to fetch items", err);
        setError('Could not load your inventory. Please try again later.');
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchItems(); // Initial fetch
  }, []);

  const handleAnalyze = (itemId) => {
    // ... (this function remains the same)
    setMessage(`Analyzing item ${itemId}...`);
    api.post(`/core/items/${itemId}/analyze/`)
      .then(() => {
        setMessage(`Analysis started for item ${itemId}! You can view the results in a moment.`);
      })
      .catch(err => {
        console.error("Failed to start analysis", err);
        setMessage(`Error starting analysis for item ${itemId}.`);
      });
  };

  // Function to handle adding a new item and refreshing the list
  const handleAddItem = (newItem) => {
    setItems(prevItems => [newItem, ...prevItems]); // Add new item to the top of the list
    setIsModalOpen(false); // Close the modal
    setMessage(`Successfully added "${newItem.title}" to your inventory!`);
  };

  if (loading) return <p>Loading your inventory...</p>;
  if (error) return <p style={{ color: 'var(--error-color)' }}>{error}</p>;

  return (
    <div className="item-list-container">
      <div className="item-list-header">
        <h2>Your Inventory</h2>
        {/* This button now opens the modal */}
        <button onClick={() => setIsModalOpen(true)}>+ Add New Item</button>
      </div>
      {message && <p style={{ color: 'var(--primary-color)' }}>{message}</p>}
      
      {items.length > 0 ? (
        <ul className="item-list">
          {items.map(item => (
            <li key={item.id} className="item-card">
              <div className="item-info">
                <Link to={`/item/${item.id}`}>
                  {item.brand} {item.title}
                </Link>
                <p>Size: {item.size} | Color: {item.color} | Condition: {item.condition}</p>
              </div>
              <div className="item-actions">
                <Link to={`/item/${item.id}/analysis`} style={{textDecoration: 'none'}}>
                  <button style={{backgroundColor: '#6b7280'}}>View Analysis</button>
                </Link>
                <button onClick={() => handleAnalyze(item.id)}>Run Analysis</button>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <div className="item-card">
          <p>You haven't added any items to your inventory yet. Click "Add New Item" to get started!</p>
        </div>
      )}

      {/* Conditional rendering for the modal */}
      {isModalOpen && (
        <Modal onClose={() => setIsModalOpen(false)}>
          <AddItemForm 
            onAddItem={handleAddItem}
            onCancel={() => setIsModalOpen(false)} 
          />
        </Modal>
      )}
    </div>
  );
};

export default ItemList;