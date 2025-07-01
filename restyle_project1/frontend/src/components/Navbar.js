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

  // Inline styles for the component
  const navStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem 2rem',
    backgroundColor: 'var(--surface-color)',
    borderBottom: '1px solid var(--border-color)',
    boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
  };

  const navLinksStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '1.5rem',
  };

  const logoStyle = {
    textDecoration: 'none',
    color: 'var(--text-primary)',
    fontSize: '1.5rem',
    fontWeight: '700',
  };

  const linkStyle = {
    textDecoration: 'none',
    color: 'var(--text-secondary)',
    fontWeight: '500',
    padding: '8px 12px',
    borderRadius: '6px',
    transition: 'background-color 0.2s, color 0.2s',
  };
  
  const activeLinkStyle = {
    ...linkStyle,
    color: 'var(--primary-color)',
  };


  return (
    <nav style={navStyle}>
      <Link to="/" style={logoStyle}>
        Re-Style
      </Link>
      <div style={navLinksStyle}>
        {isAuthenticated ? (
          <>
            <Link to="/" style={linkStyle} onMouseOver={e => e.currentTarget.style.backgroundColor = '#f3f4f6'} onMouseOut={e => e.currentTarget.style.backgroundColor = 'transparent'}>
              Dashboard
            </Link>
            <button onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <>
            <Link to="/login" style={linkStyle} onMouseOver={e => e.currentTarget.style.backgroundColor = '#f3f4f6'} onMouseOut={e => e.currentTarget.style.backgroundColor = 'transparent'}>
              Login
            </Link>
            <Link to="/register" style={linkStyle} onMouseOver={e => e.currentTarget.style.backgroundColor = '#f3f4f6'} onMouseOut={e => e.currentTarget.style.backgroundColor = 'transparent'}>
              Sign Up
            </Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;