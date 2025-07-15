// File: frontend/src/components/ItemList.js

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import Modal from './Modal'; // Import the Modal
import AddItemForm from './AddItemForm'; // Import the Form
import './Card.css';

const ItemList = ({ refreshTrigger }) => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false); // State to control the modal
  const [selectedItems, setSelectedItems] = useState([]); // Track selected item IDs
  const [deleting, setDeleting] = useState(false); // Track delete state

  const fetchItems = () => {
    api.get('/core/items/')
      .then(response => {
        setItems(response.data);
      })
      .catch(err => {
        console.error("Failed to fetch items", err);
        if (err.response?.status === 401) {
          // Handle unauthorized - redirect to login
          window.location.href = '/login';
        } else {
          setError('Could not load your inventory. Please try again later.');
        }
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchItems(); // Initial fetch
  }, []);

  // Refresh items when refreshTrigger changes (when items are added from search)
  useEffect(() => {
    if (refreshTrigger) {
      fetchItems();
    }
  }, [refreshTrigger]);

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

  // Handle checkbox toggle
  const handleCheckboxChange = (itemId) => {
    setSelectedItems(prev =>
      prev.includes(itemId)
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  // Handle delete selected items
  const handleDeleteSelected = async () => {
    if (selectedItems.length === 0) return;
    setDeleting(true);
    setMessage('Deleting selected items...');
    try {
      // Use Promise.all to send all DELETE requests
      await Promise.all(selectedItems.map(id =>
        api.delete(`/core/items/${id}/`).catch(err => {
          // Optionally handle individual errors
          console.error(`Failed to delete item ${id}`, err);
        })
      ));
      setMessage('Selected items deleted successfully.');
      setSelectedItems([]);
      fetchItems();
    } catch (err) {
      setMessage('Error deleting selected items.');
    } finally {
      setDeleting(false);
    }
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
      {items.length > 0 && (
        <div style={{ marginBottom: '1em' }}>
          <button
            onClick={handleDeleteSelected}
            disabled={selectedItems.length === 0 || deleting}
            style={{
              backgroundColor:
                selectedItems.length === 0 || deleting
                  ? '#d1d5db' // Tailwind gray-300
                  : '#dc2626', // Tailwind red-600
              color: selectedItems.length === 0 || deleting ? '#6b7280' : 'white',
              marginRight: 8,
              cursor: selectedItems.length === 0 || deleting ? 'not-allowed' : 'pointer',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '4px',
              fontWeight: 600,
              transition: 'background 0.2s',
            }}
          >
            {deleting ? 'Deleting...' : `Delete Selected (${selectedItems.length})`}
          </button>
        </div>
      )}
      {items.length > 0 ? (
        <ul className="item-list">
          {items.map(item => (
            <li key={item.id} className="item-card">
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <input
                  type="checkbox"
                  checked={selectedItems.includes(item.id)}
                  onChange={() => handleCheckboxChange(item.id)}
                  style={{ marginRight: 12 }}
                />
                <div className="item-info">
                  <Link to={`/item/${item.id}`}>
                    {item.brand} {item.title}
                  </Link>
                  <p>Size: {item.size} | Color: {item.color} | Condition: {item.condition}</p>
                </div>
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