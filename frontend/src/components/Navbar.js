// File: frontend/src/components/Navbar.js

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';

const Navbar = () => {
  const { isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Inline styles for the component with dark theme
  const navStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem 2rem',
    backgroundColor: 'var(--surface-color)',
    borderBottom: '1px solid var(--border-color)',
    boxShadow: 'var(--shadow-md)',
    backdropFilter: 'blur(10px)',
    position: 'sticky',
    top: 0,
    zIndex: 1000,
  };

  const navLinksStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '1.5rem',
  };

  const logoStyle = {
    textDecoration: 'none',
    color: 'var(--primary-color)',
    fontSize: '1.75rem',
    fontWeight: '800',
    letterSpacing: '-0.025em',
    textShadow: '0 0 20px rgba(139, 92, 246, 0.3)',
  };

  const linkStyle = {
    textDecoration: 'none',
    color: 'var(--text-secondary)',
    fontWeight: '500',
    padding: '10px 16px',
    borderRadius: '8px',
    transition: 'all 0.2s ease-in-out',
    position: 'relative',
  };
  
  const activeLinkStyle = {
    ...linkStyle,
    color: 'var(--primary-color)',
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
  };

  const buttonStyle = {
    backgroundColor: 'var(--primary-color)',
    color: 'var(--text-primary)',
    border: 'none',
    padding: '10px 20px',
    borderRadius: '8px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.2s ease-in-out',
    boxShadow: 'var(--shadow-sm)',
  };

  return (
    <nav style={navStyle}>
      <Link to="/" style={logoStyle}>
        Restyle
      </Link>
      <div style={navLinksStyle}>
        {isAuthenticated ? (
          <>
            <Link 
              to="/" 
              style={linkStyle} 
              onMouseOver={e => {
                e.currentTarget.style.backgroundColor = 'var(--surface-hover)';
                e.currentTarget.style.color = 'var(--text-primary)';
              }} 
              onMouseOut={e => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = 'var(--text-secondary)';
              }}
            >
              Dashboard
            </Link>
            <button 
              onClick={handleLogout}
              style={buttonStyle}
              onMouseOver={e => {
                e.currentTarget.style.backgroundColor = 'var(--primary-hover)';
                e.currentTarget.style.transform = 'translateY(-1px)';
                e.currentTarget.style.boxShadow = 'var(--shadow-md)';
              }}
              onMouseOut={e => {
                e.currentTarget.style.backgroundColor = 'var(--primary-color)';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
              }}
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link 
              to="/login" 
              style={linkStyle} 
              onMouseOver={e => {
                e.currentTarget.style.backgroundColor = 'var(--surface-hover)';
                e.currentTarget.style.color = 'var(--text-primary)';
              }} 
              onMouseOut={e => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = 'var(--text-secondary)';
              }}
            >
              Login
            </Link>
            <Link 
              to="/register" 
              style={linkStyle} 
              onMouseOver={e => {
                e.currentTarget.style.backgroundColor = 'var(--surface-hover)';
                e.currentTarget.style.color = 'var(--text-primary)';
              }} 
              onMouseOut={e => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = 'var(--text-secondary)';
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