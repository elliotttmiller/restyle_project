// File: frontend/src/components/Modal.js

import React from 'react';
import './Modal.css'; // We'll create this next

const Modal = ({ children, onClose }) => {
  // Stop click propagation to prevent modal from closing when clicking inside it
  const handleContentClick = (e) => {
    e.stopPropagation();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={handleContentClick}>
        {children}
      </div>
    </div>
  );
};

export default Modal;