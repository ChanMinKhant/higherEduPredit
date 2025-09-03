import express from 'express';
const router = express.Router();
import { login, register, getProfile, getAllUsers, createUser, updateUser, deleteUser } from '../controllers/user.js';
import { verifyJWT } from '../middlewares/verifyJWT.js';


router.post('/login', login);
router.post('/register', register);
router.get('/get-user', verifyJWT, getProfile);
router.get('/get-all-users', verifyJWT, getAllUsers)
// GET all users (admin only)
router.get('/users', verifyJWT, getAllUsers);

// CREATE a new user (admin only)
router.post('/users', verifyJWT, createUser);

// UPDATE a user by ID (admin only)
router.put('/users/:id', verifyJWT, updateUser);

// DELETE a user by ID (admin only)
router.delete('/users/:id', verifyJWT, deleteUser);

export default router;
