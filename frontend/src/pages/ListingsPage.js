import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { useNavigate } from 'react-router-dom';
import ListingCard from '../components/ListingCard';
import Modal from '../components/Modal';
import AddListingForm from '../components/AddListingForm';
import api from '../services/api';

const ListingsPage = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const navigate = useNavigate();
  const [listings, setListings] = useState([]);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  useEffect(() => {
    // This is a protected route. If the user is not authenticated,
    // redirect them to the login page.
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchAllListings();
    }
  }, [refreshTrigger, isAuthenticated]);

  // If not authenticated, we render nothing to avoid a flash of content
  // before the redirect happens.
  if (!isAuthenticated) {
    return null; 
  }

  const fetchAllListings = async () => {
    setLoading(true);
    try {
      // First get all items
      const itemsResponse = await api.get('/core/items/');
      setItems(itemsResponse.data);
      
      // Then get all listings for each item
      const allListings = [];
      for (const item of itemsResponse.data) {
        try {
          const listingsResponse = await api.get(`/core/items/${item.id}/listings/`);
          const itemListings = listingsResponse.data.map(listing => ({
            ...listing,
            item_title: item.title,
            item_brand: item.brand,
            item_id: item.id
          }));
          allListings.push(...itemListings);
        } catch (err) {
          console.error(`Failed to fetch listings for item ${item.id}:`, err);
        }
      }
      setListings(allListings);
    } catch (err) {
      console.error("Failed to fetch listings", err);
      if (err.response?.status === 401) {
        window.location.href = '/login';
      } else {
        setError('Could not load your listings. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAddListing = (newListing) => {
    setListings(prevListings => [newListing, ...prevListings]);
    setIsModalOpen(false);
    setSelectedItem(null);
  };

  const handleOpenAddListing = (item) => {
    setSelectedItem(item);
    setIsModalOpen(true);
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

  const statsStyle = {
    display: 'flex',
    justifyContent: 'center',
    gap: '2rem',
    margin: '2rem 0',
    flexWrap: 'wrap',
  };

  const statCardStyle = {
    backgroundColor: 'var(--card-background)',
    padding: '1rem 1.5rem',
    borderRadius: '8px',
    border: '1px solid var(--border-color)',
    textAlign: 'center',
    minWidth: '120px',
  };

  const statNumberStyle = {
    fontSize: '1.5rem',
    fontWeight: '700',
    color: 'var(--primary-color)',
    margin: '0',
  };

  const statLabelStyle = {
    fontSize: '0.875rem',
    color: 'var(--text-secondary)',
    margin: '0.25rem 0 0 0',
  };

  const listingsContainerStyle = {
    marginTop: '2rem',
  };

  const noListingsStyle = {
    textAlign: 'center',
    padding: '3rem',
    backgroundColor: 'var(--card-background)',
    borderRadius: '8px',
    border: '1px solid var(--border-color)',
  };

  if (loading) return <div style={pageStyle}><p>Loading your listings...</p></div>;
  if (error) return <div style={pageStyle}><p style={{ color: 'var(--error-color)' }}>{error}</p></div>;

  const totalListings = listings.length;
  const activeListings = listings.filter(l => l.status === 'ACTIVE').length;
  const platforms = [...new Set(listings.map(l => l.platform))];

  return (
    <div style={pageStyle}>
      <header style={headerStyle}>
        <h1 style={titleStyle}>Manage Listings</h1>
        <p style={subtitleStyle}>
          View and manage all your listings across different platforms. Track performance and manage your sales.
        </p>
      </header>

      {/* Stats Section */}
      <div style={statsStyle}>
        <div style={statCardStyle}>
          <p style={statNumberStyle}>{totalListings}</p>
          <p style={statLabelStyle}>Total Listings</p>
        </div>
        <div style={statCardStyle}>
          <p style={statNumberStyle}>{activeListings}</p>
          <p style={statLabelStyle}>Active Listings</p>
        </div>
        <div style={statCardStyle}>
          <p style={statNumberStyle}>{platforms.length}</p>
          <p style={statLabelStyle}>Platforms</p>
        </div>
        <div style={statCardStyle}>
          <p style={statNumberStyle}>{items.length}</p>
          <p style={statLabelStyle}>Items</p>
        </div>
      </div>

      {/* Listings Section */}
      <div style={listingsContainerStyle}>
        {listings.length > 0 ? (
          <div>
            {listings.map(listing => (
              <div key={listing.id} style={{ marginBottom: '1rem' }}>
                <ListingCard listing={listing} />
                <div style={{ marginLeft: '1rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                  Item: <Link to={`/item/${listing.item_id}`}>{listing.item_brand} {listing.item_title}</Link>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={noListingsStyle}>
            <h3>No Listings Found</h3>
            <p>You haven't created any listings yet. Add items to your inventory first, then create listings for them.</p>
            <Link to="/inventory" style={{ color: 'var(--primary-color)', textDecoration: 'none' }}>
              Go to Inventory
            </Link>
          </div>
        )}
      </div>

      {/* Modal for adding new listings */}
      {isModalOpen && selectedItem && (
        <Modal onClose={() => setIsModalOpen(false)}>
          <AddListingForm
            item={selectedItem}
            onAddListing={handleAddListing}
            onCancel={() => setIsModalOpen(false)}
          />
        </Modal>
      )}
    </div>
  );
};

export default ListingsPage; 