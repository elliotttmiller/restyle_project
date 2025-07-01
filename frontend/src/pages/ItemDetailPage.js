// File: frontend/src/pages/ItemDetailPage.js

// ... (imports remain the same) ...
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import Modal from '../components/Modal';
import AddListingForm from '../components/AddListingForm';
import ListingCard from '../components/ListingCard';

const ItemDetailPage = () => {
  // ... (all the state and useEffect hooks remain the same) ...
  const { itemId } = useParams();
  const [item, setItem] = useState(null);
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    const fetchItemAndListings = async () => {
        setLoading(true);
        setError('');
        try {
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

  const handleAddListing = (newListing) => {
    setListings(prevListings => [newListing, ...prevListings]);
    setIsModalOpen(false);
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
      
      {/* This section for displaying listings remains the same */}
      <div style={{marginTop: '1rem'}}>
        {listings.length > 0 ? (
          <ul style={{listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '1rem'}}>
            {listings.map(listing => (
              <ListingCard key={listing.id} listing={listing} />
            ))}
          </ul>
        ) : (
          <div style={{
            padding: '2rem', border: '1px dashed var(--border-color)',
            borderRadius: '8px', backgroundColor: '#fafafa',
            textAlign: 'center', color: 'var(--text-secondary)'
          }}>
            <p>This item is not yet listed on any platform. Click "Add New Listing" to start.</p>
          </div>
        )}
      </div>

      {/* This modal logic also remains the same */}
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