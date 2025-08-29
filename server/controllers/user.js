import User from '../modals/user.js'; // Adjust the path as necessary
import asyncHandler from 'express-async-handler';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import CustomError from '../middlewares/CustomError.js';  

export const register = asyncHandler(async (req, res, next) => {
    console.log(process.env.JWT_SECRET);
    const { username, email, password } = req.body;

    // Simple validation
    if (!username || !email || !password) {
        res.status(400);
        throw new CustomError('Please provide email and password', 400);
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
    });

    // Generate JWT
    const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET || '12345', {
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
    console.log(email, password);
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
    const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET || '12345', {
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
    const user = await User.findById(req.user.id).select('-password');
    if (!user) {
        res.status(404);
        throw new CustomError('User not found', 404);
    }
    res.status(200).json({
        success: true,
        user: {
            id: user._id,
            email: user.email,
        },
    });
});

export const getUsers = asyncHandler(async (req, res, next) => {
    const users = await User.find().select('-password').lean();
    res.status(200).json({
        success: true,
        users,
    });
});