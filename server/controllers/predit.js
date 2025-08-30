import asyncHandler from 'express-async-handler';
import CustomError from '../middlewares/CustomError.js'; 
import axios from 'axios';

// call api to python server 

const pythonBaseUrl = process.env.PYTHON_URL || 'http://localhost:5000';

export const getPrediction = asyncHandler(async (req, res, next) => {
    // filter later
  try {
    const response = await axios.post(
      `${pythonBaseUrl}/api/predict`,
      req.body,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new CustomError('Failed to get prediction from Python server', 500);
    }

    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    next(error);
  }
});