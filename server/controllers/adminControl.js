import asyncHandler from 'express-async-handler';
import CustomError from '../middlewares/CustomError.js'; 
import { PassThrough } from 'nodemailer/lib/xoauth2/index.js';

export const basedScore = asyncHandler(async (req, res, next) => {
    try {
        res.status(200).json({message: "success"})
    } catch (error) {
        next(error);
    }
});

// 0.5 is normal, 1 is impossible to pass, 0 is impossible to fail

export const difficultyAdjust = asyncHandler(async (req, res, next) => {
    try {
        res.status(200).json({message: "success"})
    } catch (error) {
        next(error);
    }
});
