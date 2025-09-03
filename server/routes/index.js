import authRoutes from './auth.js';
import predictRoutes from './predit.js';
import modelConfigRoutes from './model.js';

import express from 'express';
const router = express.Router();

router.use('/auth', authRoutes);
router.use('/ml', predictRoutes);
router.use('/config', modelConfigRoutes );

export default router;
