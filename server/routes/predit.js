import express from 'express';
import { getPredictionHistory, makePrediction } from '../controllers/predit.js';
import { verifyJWT } from '../middlewares/verifyJWT.js';
const router = express.Router();


router.post('/predict', verifyJWT, makePrediction);
router.get('/predict/recent', verifyJWT, getPredictionHistory);


export default router;
