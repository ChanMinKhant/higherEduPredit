import express from "express";
import {
  getModelConfigs,
  getModelConfig,
  createModelConfig,
  updateModelConfig,
  deleteModelConfig,
} from "../controllers/model.js";
import { verifyJWT } from "../middlewares/verifyJWT.js";

const router = express.Router();

router.get("/model-config", getModelConfigs);
router.get("/model-config/:id", verifyJWT, getModelConfig);
router.post("/model-config", verifyJWT, createModelConfig);
router.put("/model-config/:id", verifyJWT, updateModelConfig);
router.delete("/model-config/:id", verifyJWT, deleteModelConfig);

export default router;
