import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';
import { useUser } from '../hooks/useUser';

const Navbar: React.FC = () => {
  const location = useLocation();
  const { user, loading } = useUser();

  return (
    <nav className="navbar">
      <div className="nav-container">
        <h1 className="nav-title">Higher Education Access Prediction System</h1>
        <div className="nav-links">
          <Link 
            to="/" 
            className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
          >
            Prediction
          </Link>
          <Link 
            to="/admin" 
            className={`nav-link ${location.pathname === '/admin' ? 'active' : ''}`}
          >
            Admin Panel
          </Link>
          <Link 
            to="/predictions" 
            className={`nav-link ${location.pathname === '/predictions' ? 'active' : ''}`}
          >
            Recent Predictions
          </Link>
          <Link 
            to="/users" 
            className={`nav-link ${location.pathname === '/users' ? 'active' : ''}`}
          >
            User Management
          </Link>


          {!loading && (
            user ? (
              <span className="nav-user">Welcome, {user.name}</span>
            ) : (
              <Link 
                to="/login" 
                className={`nav-link ${location.pathname === '/login' ? 'active' : ''}`}
              >
                Login
              </Link>
            )
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
