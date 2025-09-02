import express from 'express';
import { makePrediction } from '../controllers/predit.js';
import { verifyJWT } from '../middlewares/verifyJWT.js';
const router = express.Router();


router.post('/predict', verifyJWT, makePrediction);


export default router;
