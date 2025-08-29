import authRoutes from './auth.js';

import express from 'express';
const router = express.Router();

router.use('/auth', authRoutes);

export default router;
