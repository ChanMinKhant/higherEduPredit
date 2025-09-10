import User from '../modals/user.js'; // Adjust the path as necessary
import asyncHandler from 'express-async-handler';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import CustomError from '../middlewares/CustomError.js';  

export const register = asyncHandler(async (req, res, next) => {
    const { username, email, password } = req.body;
    // Simple validation
    if (!username || !email || !password) {
        res.status(400);
        throw new CustomError('Please provide username, email and password', 400);
    }

    // Check if user already exists (replace with your User model)
    const existingUser = await User.findOne({ email });
    if (existingUser) {
        res.status(400);
        throw new Error('User already exists');
    }

    // Hash password (using bcrypt)
    const hashedPassword = await bcrypt.hash(password, 10);
   // Check if any users exist
    const isFirstUser = !(await User.exists({}));

    // Create the user
    const user = await User.create({
    username,
    email,
    password: hashedPassword,
    role: isFirstUser ? "admin" : "user", // Assign role based on existence
    });
    
    // Generate JWT
    const token = jwt.sign({ id: user._id, role: user.role }, process.env.JWT_SECRET || '12345', {
        expiresIn: '7d',
    });

    // Set cookie
    res.cookie('jwt', token, {
    maxAge: 365 * 24 * 60 * 60 * 1000, // 1 year
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'none',
    path: '/',
    });

    res.status(201).json({
        success: true,
        user: {
            id: user._id,
            email: user.email,
        },
        token,
    });
});

export const login = asyncHandler(async (req, res, next) => {
    const { email, password } = req.body;
    // Simple validation
    if (!email || !password) {
        res.status(400);
        throw new CustomError('Please provide email and password', 400);
    }

    // Find user by email
    const user = await User.findOne({ email }).select('+password');
    if (!user) {
        res.status(401);
        throw new CustomError('Invalid credentials', 401);
    }
    
    // Compare password
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
        res.status(401);
        throw new CustomError('Invalid credentials', 401);
    }

    // Generate JWT
    const token = jwt.sign({ id: user._id, role: user.role }, process.env.JWT_SECRET || '12345', {
        expiresIn: '7d',
    });

    // Set cookie
    res.cookie('jwt', token, {
        maxAge: 365 * 24 * 60 * 60 * 1000, // 1 year
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'none',
        path: '/',
    });

    res.status(200).json({
        success: true,
        user: {
            id: user._id,
            email: user.email,
        },
        token,
    });
});

export const getProfile = asyncHandler(async (req, res, next) => {
    const user = await User.findById(req.userId).select('-password');
    if (!user) {
        res.status(404);
        throw new CustomError('User not found', 404);
    }
    res.status(200).json({
        success: true,
        user
    });
});

export const getAllUsers = asyncHandler(async (req, res, next) => {
    const user = await User.findById(req.userId)
    if (!user) {
        res.status(404);
        throw new CustomError('User not found', 404);
    }
    if (user?.role !== 'admin') {
        throw new CustomError('Not authorized to access this resource', 403);
    }
    const users = await User.find().select('-password').lean();
    res.status(200).json({
        success: true,
        users,
    });
});

export const createUser = asyncHandler(async (req, res, next) => {
    const currentUser = await User.findById(req.userId);
    if (!currentUser) {
        res.status(404);
        throw new CustomError('User not found', 404);
    }
    if (currentUser?.role !== 'admin') {
        throw new CustomError('Not authorized to access this resource', 403);
    }
    
    const { username, email, password, role } = req.body;
    // Simple validation
    if (!username || !email || !password || !role) {
        res.status(400);
        throw new CustomError('Please provide username, email, password and role', 400);
    }
    // Check if user already exists (replace with your User model)
    const existingUser = await User.findOne({ email });
    if (existingUser) {
        res.status(400);
        throw new Error('User already exists');
    }
    // Hash password (using bcrypt)
    const hashedPassword = await bcrypt.hash(password, 10);
    // Create user (replace with your User model)
    const user = await User.create({
        username,
        email,
        password: hashedPassword,
        role,
    });
    res.status(201).json({
        success: true,
        user
    });
});

export const deleteUser = asyncHandler(async (req, res, next) => {
    const currentUser = await User.findById(req.userId);
    if (!currentUser || currentUser?.role !== 'admin') {
        throw new CustomError('Not authorized to access this resource', 403);
    }
    const user = await User.findById(req.params.id);
    if (!user) {
        res.status(404);
        throw new CustomError('User not found', 404);
    }

    await user.deleteOne();
    res.status(204).json({
        success: true,
        message: 'User deleted successfully'
    });
});

export const updateUser = asyncHandler(async (req, res, next) => {
    
    const user = await User.findById(req.userId);
    if (!user) {
        res.status(404);
        throw new CustomError('User not found', 404);
    }
    if (user?.role !== 'admin') {
        throw new CustomError('Not authorized to access this resource', 403);
    }
    const { username, email, role } = req.body;
    // Simple validation
    if (!username || !email || !role) {
        res.status(400);
        throw new CustomError('Please provide username, email and role', 400);
    }

    const updateUser = await User.findById(req.params.id);
    // Hash password (using bcrypt)
    // Update user (replace with your User model)
    updateUser.username = username;
    updateUser.email = email;
    updateUser.role = role;
    await updateUser.save();
    res.status(200).json({
        success: true,
        user
    });
});

export const logout = asyncHandler(async (req, res, next) => {
    res.cookie('jwt', '', {
        maxAge: 1,
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'none',
    });

    res.status(200).json({
        success: true,
        message: 'Logged out successfully',
    });
});