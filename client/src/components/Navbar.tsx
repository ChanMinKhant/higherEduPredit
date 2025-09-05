import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';
import { useUser } from '../hooks/useUser';
import { logout } from '../services/auth';

const Navbar: React.FC = () => {
  const location = useLocation();
  const { user, loading } = useUser();
  console.log(user)

  const handleLogout = async () => {
    try {
      await logout();
      window.location.href = '/login'; // Redirect to login page after logout
    } catch (error) {
      console.error('Logout failed:', error);
    }
  }
  if (loading) {
    return <div>Loading...</div>;
  }
  return (
    <nav className="navbar">
      <div className="nav-container">
        <h1 className="nav-title">Higher Education Access Prediction System</h1>
        <div className="nav-links">
          { user && <Link 
            to="/predict" 
            className={`nav-link ${location.pathname === '/predict' ? 'active' : ''}`}
          >
            Prediction
          </Link>}
          { user?.role === 'admin' && (
            <Link 
              to="/admin" 
              className={`nav-link ${location.pathname === '/admin' ? 'active' : ''}`}
            >
              Admin Panel
            </Link>
          )}
         { user && <Link 
            to="/predictions" 
            className={`nav-link ${location.pathname === '/predictions' ? 'active' : ''}`}
          >
            Recent Predictions
          </Link>}
          { user?.role === 'admin' && (
            <Link 
              to="/users" 
              className={`nav-link ${location.pathname === '/users' ? 'active' : ''}`}
            >
              User Management
            </Link>
          )}


          {!loading && (
            user ? (
              <button
                onClick={handleLogout}
                className={`nav-link ${location.pathname === '/logout' ? 'active' : ''}`}
              >
                Logout
              </button>
            ) : (
              <>
              <Link 
                to="/register" 
                className={`nav-link ${location.pathname === '/register' ? 'active' : ''}`}
              >
                register
              </Link>
              <Link 
                to="/login" 
                className={`nav-link ${location.pathname === '/login' ? 'active' : ''}`}
              >
                Login
              </Link></>
            )
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
