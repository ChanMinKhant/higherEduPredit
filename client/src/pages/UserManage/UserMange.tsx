import React, { useEffect, useState } from 'react';
import { getAllUsers, createUser, updateUser, deleteUser } from '../../services/auth';
import { useUser } from '../../hooks/useUser';
import './UserManage.css';
import { Link } from 'react-router-dom';

const UserManage: React.FC = () => {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    role: 'user',
    password: ''
  });
  const [editingUserId, setEditingUserId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { user: currentAdmin } = useUser();

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const data = await getAllUsers();
      setUsers(data.users || []);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const validateForm = () => {
    if (!formData.username.trim() || !formData.email.trim()) {
      return 'Username and email are required';
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      return 'Invalid email format';
    }
    if (!editingUserId && !formData.password.trim()) {
      return 'Password is required when creating a user';
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }
    setError(null);

    try {
      if (editingUserId) {
        // Do not send password when updating
        const { password, ...updateData } = formData;
        await updateUser(editingUserId, updateData);
      } else {
        await createUser(formData);
      }

      // Reset form
      setFormData({ username: '', email: '', role: 'user', password: '' });
      setEditingUserId(null);
      fetchUsers();
    } catch (error) {
      console.error('Error saving user:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (currentAdmin && currentAdmin._id === id) {
      alert("❌ You cannot delete your own account.");
      return;
    }

    if (!window.confirm('Are you sure you want to delete this user?')) return;

    try {
      await deleteUser(id);
      fetchUsers();
    } catch (error) {
      console.error('Error deleting user:', error);
    }
  };

  const handleEdit = (user: any) => {
    setEditingUserId(user._id);
    setFormData({
      username: user.username,
      email: user.email,
      role: user.role,
      password: '' // clear password for editing
    });
  };

  return (
    <div className="user-manage">
      <h2 className="title">User Management</h2>

      <form onSubmit={handleSubmit} className="user-form">
        {error && <p className="error">{error}</p>}
        <div className="form-grid">
          <input
            type="text"
            name="username"
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
            required
          />
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
          />
          <select name="role" value={formData.role} onChange={handleChange}>
            <option value="user">Student</option>
            <option value="admin">Admin</option>
          </select>
          {!editingUserId && (
            <input
              type="password"
              name="password"
              placeholder="Password"
              value={formData.password}
              onChange={handleChange}
              required
            />
          )}
        </div>
        <button type="submit" className="btn primary">
          {editingUserId ? "Update User" : "Create User"}
        </button>
      </form>

      {loading ? (
        <p className="loading">Loading users...</p>
      ) : users.length > 0 ? (
        <div className="user-list">
          {users.map((u: any) => (
            <div key={u._id} className="user-card">
              <div>
                <h3>{u.username}</h3>
                <p>{u.email}</p>
                <p className="role">Role: {u.role}</p>
              </div>
              <div className="actions">
                <Link to={`/predictions/${u._id}`} className="btn primary">
                  result
                </Link>
                <button onClick={() => handleEdit(u)} className="btn secondary">
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(u._id)}
                  className="btn danger"
                  disabled={currentAdmin && currentAdmin._id === u._id}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="empty">No users found.</p>
      )}
    </div>
  );
};

export default UserManage;
