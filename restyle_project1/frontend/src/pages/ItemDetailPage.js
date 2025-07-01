// File: frontend/src/pages/ItemDetailPage.js

import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import Modal from '../components/Modal'; // Import Modal
import AddListingForm from '../components/AddListingForm'; // Import AddListingForm

const ItemDetailPage = () => {
  const { itemId } = useParams();
  const [item, setItem] = useState(null);
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false); // State for our new modal

  useEffect(() => {
    const fetchItemAndListings = async () => {
      setLoading(true);
      setError('');
      try {
        // Fetch both the item and its listings in parallel for efficiency
        const itemPromise = api.get(`/core/items/${itemId}/`);
        const listingsPromise = api.get(`/core/items/${itemId}/listings/`);
        
        const [itemResponse, listingsResponse] = await Promise.all([itemPromise, listingsPromise]);
        
        setItem(itemResponse.data);
        setListings(listingsResponse.data);

      } catch (err) {
        setError('Failed to fetch item details. It may not exist or you may not have permission to view it.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchItemAndListings();
  }, [itemId]);

  // Callback function to add the new listing to our state
  const handleAddListing = (newListing) => {
    setListings(prevListings => [newListing, ...prevListings]);
    setIsModalOpen(false); // Close modal on success
  };

  if (loading) return <div style={{padding: '2rem'}}>Loading item...</div>;
  if (error) return <div style={{padding: '2rem', color: 'var(--error-color)'}}>{error}</div>;
  if (!item) return <div style={{padding: '2rem'}}>Item not found.</div>

  return (
    <div>
      <Link to="/" style={{ marginBottom: '1.5rem', display: 'inline-block', color: 'var(--text-secondary)' }}> 
        ← Back to Dashboard
      </Link>
      <h1>{item.brand} {item.title}</h1>
      <p style={{ color: 'var(--text-secondary)', marginTop: '-0.5rem' }}>
        <strong>SKU:</strong> {item.sku || 'N/A'} | <strong>Condition:</strong> {item.condition}
      </p>
      <p>{item.description || "No description provided."}</p>
      
      <hr style={{ margin: '2rem 0', borderColor: 'var(--border-color)'}}/>

      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <h2>Manage Listings</h2>
        <button onClick={() => setIsModalOpen(true)}>+ Add New Listing</button>
      </div>

      {listings.length > 0 ? (
        <ul style={{listStyle: 'none', padding: 0, marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem'}}>
          {listings.map(listing => (
            <li key={listing.id} className="item-card"> {/* Reusing our card style */}
              <div className="item-info">
                <p style={{fontWeight: 600, color: 'var(--text-primary)'}}>
                  {listing.platform} - ${parseFloat(listing.list_price).toFixed(2)}
                </p>
                <a href={listing.listing_url || '#'} target="_blank" rel="noopener noreferrer">
                  View on Platform (Mock)
                </a>
              </div>
              {/* Future actions like 'De-list' or 'Edit' would go here */}
            </li>
          ))}
        </ul>
      ) : (
        <div style={{
          padding: '2rem',
          border: '1px dashed var(--border-color)',
          borderRadius: '8px',
          backgroundColor: '#fafafa',
          textAlign: 'center',
          color: 'var(--text-secondary)',
          marginTop: '1rem'
        }}>
          <p>This item is not yet listed on any platform. Click "Add New Listing" to start.</p>
        </div>
      )}

      {/* Our modal for adding a new listing */}
      {isModalOpen && (
        <Modal onClose={() => setIsModalOpen(false)}>
          <AddListingForm 
            item={item}
            onAddListing={handleAddListing}
            onCancel={() => setIsModalOpen(false)}
          />
        </Modal>
      )}
    </div>
  );
};

export default ItemDetailPage;