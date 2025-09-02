import asyncHandler from 'express-async-handler';
import CustomError from '../middlewares/CustomError.js'; 
import axios from 'axios';
import Prediction from '../modals/prediction.js';
import User from '../modals/user.js'; 

// call api to python server 

const pythonBaseUrl = process.env.PYTHON_URL || 'http://localhost:5000';

export const makePrediction = asyncHandler(async (req, res, next) => {
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

export const getPredictionHistory = asyncHandler(async (req, res, next) => {
  try {
    if (req.role !== 'admin' && req.userId !== req.params.userId) {
      throw new CustomError('Not authorized to access this resource', 403);
    }
    const predictions = await Prediction.find({ userId: req.params.userId });
    res.status(200).json(predictions);

  } catch (error) {
    next(error);
  }
});

export const getAllPredictions = asyncHandler(async (req, res, next) => {
  try {
    const predictions = await Prediction.find();
    res.status(200).json(predictions);
  } catch (error) {
    next(error);
  }
});

export const deletePrediction = asyncHandler(async (req, res, next) => {
  try {
    const prediction = await Prediction.findById(req.params.id);
    if (!prediction) {
      throw new CustomError('Prediction not found', 404);
    }
    if (req.role !== 'admin' && req.userId !== prediction.userId) {
      throw new CustomError('Not authorized to delete this prediction', 403);
    }
    await prediction.remove();
    res.status(204).send();
  } catch (error) {
    next(error);
  }
});
