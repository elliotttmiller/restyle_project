// File: frontend/src/components/Navbar.js

import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import useAuthStore from '../store/authStore';

const Navbar = () => {
  const { isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  // Modern glassmorphism navbar
  const navStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1.25rem 3rem',
    background: 'var(--surface-glass)',
    backdropFilter: 'blur(20px)',
    borderBottom: '1px solid var(--glass-border)',
    boxShadow: 'var(--shadow-lg)',
    position: 'sticky',
    top: 0,
    zIndex: 1000,
  };

  const logoContainerStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
  };

  const logoStyle = {
    textDecoration: 'none',
    fontSize: '1.75rem',
    fontWeight: '800',
    letterSpacing: '-0.02em',
    background: 'var(--primary-gradient)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    transition: 'transform var(--transition-base)',
  };

  const betaBadgeStyle = {
    fontSize: '0.625rem',
    fontWeight: '700',
    padding: '0.25rem 0.5rem',
    borderRadius: 'var(--radius-full)',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  };

  const navLinksStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  };

  const linkStyle = (active) => ({
    textDecoration: 'none',
    color: active ? 'var(--text-primary)' : 'var(--text-secondary)',
    fontWeight: '600',
    fontSize: '0.9375rem',
    padding: '0.625rem 1rem',
    borderRadius: 'var(--radius-lg)',
    transition: 'all var(--transition-base)',
    position: 'relative',
    background: active ? 'rgba(102, 126, 234, 0.15)' : 'transparent',
    border: active ? '1px solid rgba(102, 126, 234, 0.3)' : '1px solid transparent',
  });

  const buttonStyle = {
    background: 'var(--primary-gradient)',
    color: 'var(--text-primary)',
    border: 'none',
    padding: '0.625rem 1.25rem',
    borderRadius: 'var(--radius-lg)',
    fontWeight: '700',
    fontSize: '0.9375rem',
    cursor: 'pointer',
    transition: 'all var(--transition-base)',
    boxShadow: 'var(--shadow-md)',
    position: 'relative',
    overflow: 'hidden',
  };

  return (
    <nav style={navStyle}>
      <div style={logoContainerStyle}>
        <Link 
          to="/" 
          style={logoStyle}
          onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
          onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
        >
          <span>✨</span>
          Restyle.ai
        </Link>
        <span style={betaBadgeStyle}>Beta</span>
      </div>
      
      <div style={navLinksStyle}>
        {isAuthenticated ? (
          <>
            <Link 
              to="/" 
              style={linkStyle(isActive('/'))}
              onMouseEnter={(e) => {
                if (!isActive('/')) {
                  e.currentTarget.style.background = 'var(--surface-hover)';
                  e.currentTarget.style.color = 'var(--text-primary)';
                }
              }} 
              onMouseLeave={(e) => {
                if (!isActive('/')) {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.color = 'var(--text-secondary)';
                }
              }}
            >
              Dashboard
            </Link>
            <Link 
              to="/inventory" 
              style={linkStyle(isActive('/inventory'))}
              onMouseEnter={(e) => {
                if (!isActive('/inventory')) {
                  e.currentTarget.style.background = 'var(--surface-hover)';
                  e.currentTarget.style.color = 'var(--text-primary)';
                }
              }} 
              onMouseLeave={(e) => {
                if (!isActive('/inventory')) {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.color = 'var(--text-secondary)';
                }
              }}
            >
              Inventory
            </Link>
            <Link 
              to="/listings" 
              style={linkStyle(isActive('/listings'))}
              onMouseEnter={(e) => {
                if (!isActive('/listings')) {
                  e.currentTarget.style.background = 'var(--surface-hover)';
                  e.currentTarget.style.color = 'var(--text-primary)';
                }
              }} 
              onMouseLeave={(e) => {
                if (!isActive('/listings')) {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.color = 'var(--text-secondary)';
                }
              }}
            >
              Listings
            </Link>
            <button 
              onClick={handleLogout}
              style={buttonStyle}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = 'var(--shadow-primary)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'var(--shadow-md)';
              }}
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link 
              to="/login" 
              style={linkStyle(isActive('/login'))}
              onMouseEnter={(e) => {
                if (!isActive('/login')) {
                  e.currentTarget.style.background = 'var(--surface-hover)';
                  e.currentTarget.style.color = 'var(--text-primary)';
                }
              }} 
              onMouseLeave={(e) => {
                if (!isActive('/login')) {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.color = 'var(--text-secondary)';
                }
              }}
            >
              Login
            </Link>
            <Link 
              to="/register" 
              style={{...linkStyle(isActive('/register')), ...buttonStyle, display: 'inline-block'}}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = 'var(--shadow-primary)';
              }} 
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'var(--shadow-md)';
              }}
            >
              Sign Up
            </Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;