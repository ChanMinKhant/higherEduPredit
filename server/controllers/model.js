import asyncHandler from "express-async-handler";
import CustomError from "../middlewares/CustomError.js";
import ModelConfig from "../modals/modelConfig.js";

/**
 * @desc    Get all model configs
 * @route   GET /api/model-config
 * @access  Admin
 */
export const getModelConfigs = asyncHandler(async (req, res) => {
  // find latest config
  const config = await ModelConfig.findOne().sort({ createdAt: -1 });
  res.status(200).json({
    success: true,
    config,
  });
});

/**
 * @desc    Get single model config
 * @route   GET /api/model-config/:id
 * @access  Admin
 */
export const getModelConfig = asyncHandler(async (req, res) => {
  const config = await ModelConfig.findById(req.params.id);
  if (!config) {
    throw new CustomError("Model config not found", 404);
  }
  res.status(200).json({
    success: true,
    config,
  });
});

/**
 * @desc    Create new model config
 * @route   POST /api/model-config
 * @access  Admin
 */
export const createModelConfig = asyncHandler(async (req, res) => {
  const {
    n_estimators,
    max_depth,
    min_samples_split,
    min_samples_leaf,
    difficulty,
    basedScore,
  } = req.body;

  const config = await ModelConfig.create({
    n_estimators,
    max_depth,
    min_samples_split,
    min_samples_leaf,
    difficulty,
    basedScore,
  });

  res.status(201).json({
    success: true,
    config,
  });
});

/**
 * @desc    Update model config
 * @route   PUT /api/model-config/:id
 * @access  Admin
 */
export const updateModelConfig = asyncHandler(async (req, res) => {
  const config = await ModelConfig.findById(req.params.id);
  if (!config) {
    throw new CustomError("Model config not found", 404);
  }

  Object.assign(config, req.body); // update only provided fields
  await config.save();

  res.status(200).json({
    success: true,
    config,
  });
});

/**
 * @desc    Delete model config
 * @route   DELETE /api/model-config/:id
 * @access  Admin
 */
export const deleteModelConfig = asyncHandler(async (req, res) => {
  const config = await ModelConfig.findById(req.params.id);
  if (!config) {
    throw new CustomError("Model config not found", 404);
  }

  await config.deleteOne();

  res.status(200).json({
    success: true,
    message: "Model config deleted successfully",
  });
});
