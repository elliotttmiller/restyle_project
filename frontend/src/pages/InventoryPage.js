import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { useNavigate } from 'react-router-dom';
import ItemList from '../components/ItemList';
import Modal from '../components/Modal';
import AddItemForm from '../components/AddItemForm';
import api from '../services/api';

const InventoryPage = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

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

  const handleAddItem = (newItem) => {
    // Trigger refresh of the item list
    setRefreshTrigger(prev => prev + 1);
    setIsModalOpen(false);
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

  const actionButtonStyle = {
    backgroundColor: 'var(--primary-color)',
    color: 'white',
    border: 'none',
    padding: '12px 24px',
    borderRadius: '8px',
    fontSize: '1rem',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    marginTop: '1rem',
  };

  return (
    <div style={pageStyle}>
      <header style={headerStyle}>
        <h1 style={titleStyle}>Inventory Management</h1>
        <p style={subtitleStyle}>
          Manage your inventory items. Add new items, view details, run price analysis, and track your collection.
        </p>
        <button 
          style={actionButtonStyle}
          onClick={() => setIsModalOpen(true)}
        >
          + Add New Item
        </button>
      </header>
      
      {/* Inventory Section */}
      <ItemList refreshTrigger={refreshTrigger} />
      
      {/* Modal for adding new items */}
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

export default InventoryPage; 