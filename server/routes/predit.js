import express from 'express';
import { getPrediction } from '../controllers/predit.js';
import { verifyJWT } from '../middlewares/verifyJWT.js';
const router = express.Router();


router.post('/predict', verifyJWT, getPrediction);


export default router;
