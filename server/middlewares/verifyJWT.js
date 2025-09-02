import jwt from 'jsonwebtoken';
import CustomError from './CustomError.js';
import asyncHandler from 'express-async-handler';

export const verifyJWT = asyncHandler(async (req, res, next) => {
  const token = req?.cookies?.jwt; // cookies.jwt // iam not sure cookie or authrization
  if (!token) {
    const err = new CustomError('Authentication failed', 401);
    return next(err);
  }
  jwt.verify(token, process.env.JWT_SECRET, (err, decodedToken) => {
    // req.userId = decodedToken.id;
    // next();
    if (err) {
      const error = new CustomError('Authentication failed', 401);
      console.log('error', err);
      return next(error);
    }
    req.userId = decodedToken.id;
    next();
  });
});
