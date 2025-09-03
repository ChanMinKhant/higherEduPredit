import mongoose from "mongoose";

// {
//     n_estimators: 100,
//     max_depth: 10,
//     min_samples_split: 5,
//     min_samples_leaf: 2,
//     difficulty: 0.5,
//     basedScore: 20,
//   }
const modelConfigSchema = new mongoose.Schema(
    {
      n_estimators: {
      type: Number,
      required: true,
      default: 100,
    },
    max_depth: {
      type: Number,
      required: true,
      default: 10,
    },
    min_samples_split: {
      type: Number,
      required: true,
      default: 5,
    },
    min_samples_leaf: {
      type: Number,
      required: true,
      default: 2,
    },
    difficulty: {
      type: Number,
      required: true,
      default: 0.5,
      min: 0,
      max: 1,
    },
    basedScore: {
      type: Number,
      required: true,
      default: 20,
    },
  },
  { timestamps: true }
);

const ModelConfig = mongoose.model("ModelConfig", modelConfigSchema);

export default ModelConfig;
