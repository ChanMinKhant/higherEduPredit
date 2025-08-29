import express from 'express';
const router = express.Router();
import { login, register, getProfile } from '../controllers/user.js';


router.post('/login', login);
router.post('/register', register);
router.get('/profile', getProfile);


export default router;
