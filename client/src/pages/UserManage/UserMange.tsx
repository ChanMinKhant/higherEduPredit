import React, { useEffect, useState } from 'react';
import { getAllUsers, createUser, updateUser, deleteUser } from '../../services/auth';
import { useUser } from '../../hooks/useUser';
import './UserManage.css'

const UserManage: React.FC = () => {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    role: 'user',
  });
  const [editingUserId, setEditingUserId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { user: currentAdmin } = useUser(); // logged-in admin

  // Fetch all users
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

  // Handle input changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Validate form
  const validateForm = () => {
    if (!formData.username.trim() || !formData.email.trim()) {
      return 'Username and email are required';
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      return 'Invalid email format';
    }
    return null;
  };

  // Handle form submit (create or update)
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
        await updateUser(editingUserId, formData);
      } else {
        await createUser(formData);
      }
      setFormData({ username: '', email: '', role: 'user' });
      setEditingUserId(null);
      fetchUsers();
    } catch (error) {
      console.error('Error saving user:', error);
    }
  };

  // Handle delete with confirmation
  const handleDelete = async (id: string) => {
    if (currentAdmin && currentAdmin._id === id) {
      alert("❌ You cannot delete your own account.");
      return;
    }

    const confirmDelete = window.confirm('Are you sure you want to delete this user?');
    if (!confirmDelete) return;

    try {
      await deleteUser(id);
      fetchUsers();
    } catch (error) {
      console.error('Error deleting user:', error);
    }
  };

  // Handle edit
  const handleEdit = (user: any) => {
    setEditingUserId(user._id);
    setFormData({
      username: user.username,
      email: user.email,
      role: user.role,
    });
  };

  return (
    <div className="user-manage">
      <h2 className="title">User Management</h2>

      {/* User Form */}
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
        </div>
        <button type="submit" className="btn primary">
          {editingUserId ? "Update User" : "Create User"}
        </button>
      </form>

      {/* User List */}
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
