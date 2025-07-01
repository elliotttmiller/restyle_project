// File: frontend/src/components/ListingCard.js
import React from 'react';
import './Card.css'; // We can reuse the same card styles

const ListingCard = ({ listing }) => {
  // A helper to get a friendly display name for the platform
  const getPlatformDisplayName = (platform) => {
    const names = {
      EBAY: 'eBay',
      ETSY: 'Etsy',
      POSH: 'Poshmark',
      DEPOP: 'Depop',
    };
    return names[platform] || platform;
  };

  return (
    <li className="item-card">
      <div className="item-info">
        <p style={{ fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
          {getPlatformDisplayName(listing.platform)}
        </p>
        <p style={{ margin: '0.25rem 0 0', fontSize: '1.25rem' }}>
          ${parseFloat(listing.list_price).toFixed(2)}
        </p>
      </div>
      <div className="item-actions">
        {listing.listing_url ? (
          <a href={listing.listing_url} target="_blank" rel="noopener noreferrer">
            <button style={{ backgroundColor: '#6b7280' }}>View Listing</button>
          </a>
        ) : (
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            (No URL)
          </span>
        )}
        {/* Future buttons like "De-list" or "Edit" can go here */}
      </div>
    </li>
  );
};

export default ListingCard;