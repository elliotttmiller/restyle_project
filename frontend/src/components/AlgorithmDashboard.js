import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './AlgorithmDashboard.css';

const AlgorithmDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshInterval, setRefreshInterval] = useState(30000); // 30 seconds

  useEffect(() => {
    fetchDashboardData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await api.get('/core/algorithm-dashboard/');
      
      if (response.data.status === 'success') {
        setDashboardData(response.data.data);
        setError(null);
      } else {
        setError('Failed to fetch dashboard data');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const formatNumber = (value) => {
    return value.toLocaleString();
  };

  const getConfidenceColor = (score) => {
    if (score >= 0.8) return '#10B981'; // Green
    if (score >= 0.6) return '#F59E0B'; // Yellow
    if (score >= 0.4) return '#F97316'; // Orange
    return '#EF4444'; // Red
  };

  const getSuccessRateColor = (rate) => {
    if (rate >= 90) return '#10B981';
    if (rate >= 75) return '#F59E0B';
    if (rate >= 60) return '#F97316';
    return '#EF4444';
  };

  if (loading && !dashboardData) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading algorithm performance data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <h3>Error Loading Dashboard</h3>
        <p>{error}</p>
        <button onClick={fetchDashboardData} className="retry-btn">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="algorithm-dashboard">
      <div className="dashboard-header">
        <h1>Algorithm Performance Dashboard</h1>
        <p>Real-time insights into your pricing algorithm's performance</p>
        <button onClick={fetchDashboardData} className="refresh-btn">
          🔄 Refresh
        </button>
      </div>

      {dashboardData && (
        <div className="dashboard-grid">
          {/* Key Metrics */}
          <div className="metrics-section">
            <h2>Key Performance Metrics</h2>
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-icon">📊</div>
                <div className="metric-content">
                  <h3>Average Confidence</h3>
                  <div 
                    className="metric-value"
                    style={{ color: getConfidenceColor(dashboardData.avg_confidence || 0) }}
                  >
                    {formatPercentage(dashboardData.avg_confidence || 0)}
                  </div>
                  <p className="metric-description">
                    Average confidence score across all analyses
                  </p>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-icon">🎯</div>
                <div className="metric-content">
                  <h3>Success Rate</h3>
                  <div 
                    className="metric-value"
                    style={{ color: getSuccessRateColor(dashboardData.success_rate || 0) }}
                  >
                    {formatNumber(dashboardData.success_rate || 0)}%
                  </div>
                  <p className="metric-description">
                    Percentage of successful analyses
                  </p>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-icon">📈</div>
                <div className="metric-content">
                  <h3>Total Analyses</h3>
                  <div className="metric-value">
                    {formatNumber(dashboardData.total_analyses || 0)}
                  </div>
                  <p className="metric-description">
                    Total analyses performed (last 30 days)
                  </p>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-icon">⚡</div>
                <div className="metric-content">
                  <h3>Avg Outlier Ratio</h3>
                  <div className="metric-value">
                    {formatPercentage(dashboardData.avg_outlier_ratio || 0)}
                  </div>
                  <p className="metric-description">
                    Average percentage of outliers detected
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Market Insights */}
          <div className="insights-section">
            <h2>Market Insights</h2>
            <div className="insights-grid">
              <div className="insight-card">
                <h3>Market Volatility</h3>
                <div className="volatility-meter">
                  <div 
                    className="volatility-bar"
                    style={{ 
                      width: `${(dashboardData.avg_volatility || 0) * 100}%`,
                      backgroundColor: dashboardData.avg_volatility > 0.3 ? '#EF4444' : 
                                   dashboardData.avg_volatility > 0.15 ? '#F59E0B' : '#10B981'
                    }}
                  ></div>
                </div>
                <p>{formatPercentage(dashboardData.avg_volatility || 0)} volatility</p>
              </div>

              <div className="insight-card">
                <h3>Confidence Stability</h3>
                <div className="stability-meter">
                  <div 
                    className="stability-bar"
                    style={{ 
                      width: `${(1 - (dashboardData.confidence_std || 0)) * 100}%`,
                      backgroundColor: dashboardData.confidence_std < 0.1 ? '#10B981' : 
                                   dashboardData.confidence_std < 0.2 ? '#F59E0B' : '#EF4444'
                    }}
                  ></div>
                </div>
                <p>{(1 - (dashboardData.confidence_std || 0)) * 100}% stable</p>
              </div>
            </div>
          </div>

          {/* Popular Categories */}
          {dashboardData.popular_categories && dashboardData.popular_categories.length > 0 && (
            <div className="categories-section">
              <h2>Most Analyzed Categories</h2>
              <div className="categories-list">
                {dashboardData.popular_categories.slice(0, 5).map((category, index) => (
                  <div key={index} className="category-item">
                    <span className="category-name">{category.category || 'Unknown'}</span>
                    <span className="category-count">{category.count} analyses</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Platform Distribution */}
          {dashboardData.platform_distribution && dashboardData.platform_distribution.length > 0 && (
            <div className="platforms-section">
              <h2>Platform Distribution</h2>
              <div className="platforms-list">
                {dashboardData.platform_distribution.slice(0, 5).map((platform, index) => (
                  <div key={index} className="platform-item">
                    <span className="platform-name">{platform.platform}</span>
                    <span className="platform-count">{platform.count} listings</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Performance Trends */}
          <div className="trends-section">
            <h2>Performance Trends</h2>
            <div className="trends-grid">
              <div className="trend-card">
                <h3>Algorithm Health</h3>
                <div className="health-indicator">
                  {dashboardData.avg_confidence >= 0.7 ? '🟢 Excellent' :
                   dashboardData.avg_confidence >= 0.5 ? '🟡 Good' :
                   dashboardData.avg_confidence >= 0.3 ? '🟠 Fair' : '🔴 Poor'}
                </div>
                <p>Based on confidence scores and success rates</p>
              </div>

              <div className="trend-card">
                <h3>Data Quality</h3>
                <div className="quality-indicator">
                  {dashboardData.avg_outlier_ratio <= 0.1 ? '🟢 High' :
                   dashboardData.avg_outlier_ratio <= 0.2 ? '🟡 Medium' :
                   dashboardData.avg_outlier_ratio <= 0.3 ? '🟠 Low' : '🔴 Poor'}
                </div>
                <p>Based on outlier detection rates</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AlgorithmDashboard; 