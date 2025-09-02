import asyncHandler from 'express-async-handler';
import CustomError from '../middlewares/CustomError.js'; 
import axios from 'axios';
import Prediction from '../modals/prediction.js';

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
    console.log(response.data)
    // res.status(200).json(response.data)

    // save to database
    const prediction = new Prediction({
      userId: req.userId,
      ...req.body,
      result: response.data
    });
    await prediction.save();
    if (response.status < 200 || response.status >= 300) {
      throw new CustomError('Failed to get prediction from Python server', 500);
    }
    res.status(200).json(response.data);
  } catch (error) {
    next(error);
  }
});