// File: frontend/src/pages/AnalysisPage.js

import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import './AnalysisPage.css'; // Import our new stylesheet

const AnalysisPage = () => {
  const { itemId } = useParams();
  const [item, setItem] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchAnalysisData = async () => {
      setLoading(true);
      setError('');
      try {
        const itemResponse = await api.get(`/core/items/${itemId}/`);
        setItem(itemResponse.data);
        if (itemResponse.data && itemResponse.data.analysis) {
          setAnalysis(itemResponse.data.analysis);
        }
      } catch (err) {
        setError('Failed to fetch item or analysis data. The item may not exist.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysisData();
  }, [itemId]);

  const getStatusClass = (status) => {
    if (status === 'COMPLETE') return 'status-complete';
    if (status === 'PENDING' || status === 'RUNNING') return 'status-pending';
    return 'status-error';
  };

  if (loading) return <div className="analysis-container"><p>Loading analysis data...</p></div>;
  
  if (error) return (
    <div className="analysis-container">
      <p style={{ color: 'var(--error-color)' }}>{error}</p>
      <Link to="/"> ← Back to Dashboard</Link>
    </div>
  );

  return (
    <div className="analysis-container">
      <div className="analysis-header">
        <Link to="/"> ← Back to Dashboard</Link>
        <h1>{item?.brand} {item?.title}</h1>
        <p className="item-subtitle">
          Size: {item?.size} | Color: {item?.color} | Condition: {item?.condition}
        </p>
      </div>

      <div className="summary-card">
        <div className="summary-stats">
          <div className="stat">
            <div className="stat-label">Price Range</div>
            <div className="stat-value-small">
              {analysis?.price_range_low ? `$${parseFloat(analysis.price_range_low).toFixed(2)}` : 'N/A'} - {analysis?.price_range_high ? `$${parseFloat(analysis.price_range_high).toFixed(2)}` : 'N/A'}
            </div>
          </div>
          <div className="stat">
            <div className="stat-label">Suggested Price</div>
            <div className="stat-value">
              {analysis?.suggested_price ? `$${parseFloat(analysis.suggested_price).toFixed(2)}` : 'N/A'}
            </div>
          </div>
          <div className="stat">
            <div className="stat-label">Status</div>
            <div className="stat-value-small">
              <span className={`status-badge ${getStatusClass(analysis?.status)}`}>
                {analysis?.status || 'NOT STARTED'}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <h3>Comparable Listings ({analysis?.comps?.length || 0})</h3>
      {analysis && analysis.comps.length > 0 ? (
        <div className="comps-grid">
          {analysis.comps.map(comp => (
            <div key={comp.id} className="comp-card">
              <img src={comp.image_url} alt={comp.title} />
              <div className="comp-card-content">
                <p className="comp-card-title">{comp.title}</p>
                <p className="comp-card-price">${parseFloat(comp.sold_price).toFixed(2)}</p>
                <div className="comp-card-footer">
                  <span>{comp.platform}</span>
                  <a href={comp.source_url} target="_blank" rel="noopener noreferrer">View</a>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p>No comparable listings found or analysis has not completed.</p>
      )}
    </div>
  );
};

export default AnalysisPage;