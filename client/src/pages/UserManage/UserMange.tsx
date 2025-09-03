import React, { useEffect, useState } from 'react';
import { getAllUsers, createUser, updateUser, deleteUser } from '../../services/auth';
import { useUser } from '../../hooks/useUser';

const UserManage: React.FC = () => {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    role: 'user',
  });
  const [editingUserId, setEditingUserId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { user: currentAdmin } = useUser(); // ✅ logged-in admin

  // ✅ Fetch all users
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

  // ✅ Handle input changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // ✅ Validate form
  const validateForm = () => {
    if (!formData.username.trim() || !formData.email.trim()) {
      return 'Username and email are required';
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      return 'Invalid email format';
    }
    if (!editingUserId && !formData.password) {
      return 'Password is required when creating a new user';
    }
    return null;
  };

  // ✅ Handle form submit (create or update)
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
      setFormData({ username: '', email: '', password: '', role: 'student' });
      setEditingUserId(null);
      fetchUsers();
    } catch (error) {
      console.error('Error saving user:', error);
    }
  };

  // ✅ Handle delete with confirmation
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

  // ✅ Handle edit
  const handleEdit = (user: any) => {
    setEditingUserId(user._id);
    setFormData({
      username: user.username,
      email: user.email,
      password: '', // leave empty (new password required on update)
      role: user.role,
    });
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">User Management</h2>

      {/* User Form */}
      <form onSubmit={handleSubmit} className="mb-8 bg-white shadow-md rounded-xl p-6">
        {error && <p className="text-red-600 mb-3">{error}</p>}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <input
            type="text"
            name="username"
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
            className="border rounded-lg px-3 py-2 w-full"
            required
          />
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            className="border rounded-lg px-3 py-2 w-full"
            required
          />
          <input
            type="password"
            name="password"
            placeholder={editingUserId ? "New Password (leave blank to keep)" : "Password"}
            value={formData.password}
            onChange={handleChange}
            className="border rounded-lg px-3 py-2 w-full"
            required={!editingUserId} // password required only when creating
          />
          <select
            name="role"
            value={formData.role}
            onChange={handleChange}
            className="border rounded-lg px-3 py-2 w-full"
          >
            <option value="user">Student</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          {editingUserId ? 'Update User' : 'Create User'}
        </button>
      </form>

      {/* User List */}
      {loading ? (
        <p className="text-gray-500">Loading users...</p>
      ) : users.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {users.map((u: any) => (
            <div
              key={u._id}
              className="bg-white shadow-md rounded-xl p-5 flex flex-col justify-between"
            >
              <div>
                <h3 className="text-lg font-semibold">{u.username}</h3>
                <p className="text-gray-600">{u.email}</p>
                <p className="text-sm text-gray-500">Role: {u.role}</p>
              </div>
              <div className="mt-4 flex gap-3">
                <button
                  onClick={() => handleEdit(u)}
                  className="bg-yellow-500 text-white px-3 py-1 rounded-lg hover:bg-yellow-600 transition"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(u._id)}
                  className={`px-3 py-1 rounded-lg transition ${
                    currentAdmin && currentAdmin._id === u._id
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-red-600 text-white hover:bg-red-700'
                  }`}
                  disabled={currentAdmin && currentAdmin._id === u._id}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-500">No users found.</p>
      )}
    </div>
  );
};

export default UserManage;
