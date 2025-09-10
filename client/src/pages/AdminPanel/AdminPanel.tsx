import React, { useState, useEffect } from "react";
import axios from "axios";
import "./AdminPanel.css";
import { createConfig, getConfigs } from "../../services/modalConfig";
import { useUser } from "../../hooks/useUser.js";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

interface ModelInfo {
  regression_model: {
    type: string;
    n_estimators: number;
    max_depth: number;
    feature_importance: Array<[string, number]>;
  };
  classification_model: {
    type: string;
    n_estimators: number;
    max_depth: number;
    feature_importance: Array<[string, number]>;
  };
  feature_columns: string[];
}

interface DatasetStats {
  total_samples: number;
  total_features: number;
  target_stats: {
    mean_grade: number;
    std_grade: number;
    min_grade: number;
    max_grade: number;
    pass_rate: number;
  };
  feature_stats: {
    numerical_features: number;
    categorical_features: number;
  };
}

interface RetrainParams {
  n_estimators: number;
  max_depth: number;
  min_samples_split: number;
  min_samples_leaf: number;
  difficulty?: number;
  basedScore?: number;
}

const AdminPanel: React.FC = () => {
  // ✅ All hooks first
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);
  const [datasetStats, setDatasetStats] = useState<DatasetStats | null>(null);
  const [originalDatasetStats, setOriginalDatasetStats] =
    useState<DatasetStats | null>(null);
  const [retrainParams, setRetrainParams] = useState<RetrainParams>({
    n_estimators: 100,
    max_depth: 10,
    min_samples_split: 5,
    min_samples_leaf: 2,
    difficulty: 0.5,
    basedScore: 20,
  });
  const [retraining, setRetraining] = useState(false);
  const [message, setMessage] = useState<string>("");
  const [messageType, setMessageType] = useState<"success" | "error" | "">("");
  const navigate = useNavigate();

  // Assuming getUser is a hook or function that returns user and loading
  const { user, loading } = useUser();
  console.log(user)
  useEffect(() => {
    if (!loading && user?.role !== 'admin') {
      // If user already logged in / exists → redirect
      navigate("/");
    }
  }, [user, loading, navigate]);

  const API_BASE = "http://localhost:5000/api";

  // fetch on mount
  useEffect(() => {
    fetchRetrainParams();
    fetchModelInfo();
    fetchDatasetStats();
  }, []);



  const fetchRetrainParams = async () => {
    try {
      const response = await getConfigs();
      if (response?.config) {
        setRetrainParams(response.config);
      }
    } catch (error) {
      console.error("Error fetching retrain params:", error);
      showMessage("Failed to load retrain parameters", "error");
    }
  };

  const fetchModelInfo = async () => {
    try {
      const response = await axios.get(`${API_BASE}/model/info`);
      setModelInfo(response.data);
      console.log(response.data)
    } catch (error) {
      console.error("Error fetching model info:", error);
      showMessage("Failed to load model information", "error");
    }
  };

  const fetchDatasetStats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/admin/dataset/stats`);
      setDatasetStats(response.data);
      setOriginalDatasetStats(response.data);
    } catch (error) {
      console.error("Error fetching dataset stats:", error);
      showMessage("Failed to load dataset statistics", "error");
    }
  };

  const showMessage = (msg: string, type: "success" | "error") => {
    setMessage(msg);
    setMessageType(type);
    setTimeout(() => {
      setMessage("");
      setMessageType("");
    }, 5000);
  };

  const handleRetrainModels = async () => {
    setRetraining(true);
    const id = toast.loading('Retarining...')
    try {
      const response = await axios.post(
        `${API_BASE}/admin/retrain`,
        retrainParams
      );
      console.log(response.data)
      showMessage(
        `Models retrained successfully! Classification Accuracy: ${response.data?.performance?.classification_accuracy} \n Classification Accuracy (higher): ${response.data?.performance?.higher_accuracy}`,
        "success"
      );
      toast.update(id, { render:  `Models retrained successfully! Classification Accuracy: ${response.data?.performance?.classification_accuracy} \n Classification Accuracy (higher): ${response.data?.performance?.higher_accuracy}`,
         type: "success", isLoading: false,  autoClose: 5000, });
      await createConfig(retrainParams);
      await fetchModelInfo();
      await fetchDatasetStats();
    } catch (error: any) {
      showMessage(
        error.response?.data?.error || "Failed to retrain models",
        "error"
      );
      toast.update(id, { render: "failed to retrain", type: "error", isLoading: false,  autoClose: 3000, });
    } finally {
      setRetraining(false);
    }
  };

  const handleParamChange = (param: keyof RetrainParams, value: number) => {
    setRetrainParams((prev) => ({
      ...prev,
      [param]: value,
    }));
  };

    // ✅ Safe to return conditionally here
  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="admin-panel">
      <div className="fixed inset-0 -z-20 bg-gradient-to-b from-blue-100 via-blue-200 to-blue-300 blur-sm"></div>

      <h1>Admin Panel</h1>

      {message && <div className={`message ${messageType}`}>{message}</div>}

      <div className="admin-sections">
        {/* Dataset Statistics */}
        <div className="admin-section">
          <h2>Dataset Statistics</h2>
          {datasetStats ? (
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Sample Count</h3>
                <div className="stat-value">{datasetStats.total_samples}</div>
              </div>
              <div className="stat-card">
                <h3>Features</h3>
                <div className="stat-value">{datasetStats.total_features - 10}</div>
              </div>
              <div className="stat-card">
                <h3>Mean Grade</h3>
                <div className="stat-value">
                  {datasetStats.target_stats.mean_grade}
                </div>
              </div>
              <div className="stat-card">
                <h3>Pass Rate</h3>
                <div className="stat-value">
                  {datasetStats.target_stats.pass_rate}%
                </div>
              </div>
            </div>
          ) : (
            <div className="loading">Loading dataset statistics...</div>
          )}
        </div>

        {/* Model Configuration */}
        <div className="admin-section">
          <h2>Model Configuration & Retraining</h2>
          <div className="retrain-form">
            <div className="param-controls">
              <div className="param-group">
                <label>Number of Trees (n_estimators)</label>
                <input
                  type="range"
                  min="10"
                  max="500"
                  step="10"
                  value={retrainParams.n_estimators}
                  onChange={(e) =>
                    handleParamChange("n_estimators", Number(e.target.value))
                  }
                />
                <span className="param-value">
                  {retrainParams.n_estimators}
                </span>
                <small>Higher values = more complex model, better accuracy but slower training</small>
              </div>

              <div className="param-group">
                <label>Maximum Depth (max_depth)</label>
                <input
                  type="range"
                  min="3"
                  max="50"
                  step="1"
                  value={retrainParams.max_depth}
                  onChange={(e) =>
                    handleParamChange("max_depth", Number(e.target.value))
                  }
                />
                <span className="param-value">{retrainParams.max_depth}</span>
                <small>Controls how deep each tree can grow (overfitting prevention)</small>
              </div>

              <div className="param-group">
                <label>Min Samples Split</label>
                <input
                  type="range"
                  min="2"
                  max="20"
                  step="1"
                  value={retrainParams.min_samples_split}
                  onChange={(e) =>
                    handleParamChange("min_samples_split", Number(e.target.value))
                  }
                />
                <span className="param-value">
                  {retrainParams.min_samples_split}
                </span>
                <small>Minimum samples required to split a node</small>
              </div>

              <div className="param-group">
                <label>Min Samples Leaf</label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  step="1"
                  value={retrainParams.min_samples_leaf}
                  onChange={(e) =>
                    handleParamChange("min_samples_leaf", Number(e.target.value))
                  }
                />
                <span className="param-value">
                  {retrainParams.min_samples_leaf}
                </span>
                <small>Minimum samples required at each leaf node</small>
              </div>

              <div className="param-group">
                <label>Difficulty</label>
                <input
                  type="range"
                  min="0.1"
                  max="0.9"
                  step="0.1"
                  value={retrainParams.difficulty}
                  onChange={(e) =>
                    handleParamChange("difficulty", Number(e.target.value))
                  }
                />
                <span className="param-value">{retrainParams.difficulty}</span>
                <small>Higher values correspond to lower pass rates</small>
              </div>

              <div className="param-group">
                <label>Based Score</label>
                <input
                  type="range"
                  min="1"
                  max="100"
                  step="1"
                  value={retrainParams.basedScore}
                  onChange={(e) =>
                    handleParamChange("basedScore", Number(e.target.value))
                  }
                />
                <span className="param-value">{retrainParams.basedScore}</span>
                <small>Maximum scored</small>
              </div>
            </div>

            <button
              className="retrain-button"
              onClick={handleRetrainModels}
              disabled={retraining}
            >
              {retraining ? "Retraining Models..." : "Retrain Models"}
            </button>
          </div>
        </div>

        {/* Current Model Info */}
        <div className="admin-section">
          <h2>Current Model Information</h2>
          {modelInfo ? (
            <div className="model-info">
              {/* <div className="model-details">
                <h3>Regression Model</h3>
                <p>
                  <strong>Type:</strong> {modelInfo.regression_model.type}
                </p>
                <p>
                  <strong>Trees:</strong> {modelInfo.regression_model.n_estimators}
                </p>
                <p>
                  <strong>Max Depth:</strong> {modelInfo.regression_model.max_depth}
                </p>
                <div className="feature-importance">
                  <h4>Top Features (Regression)</h4>
                  <div className="importance-list">
                    {modelInfo.regression_model.feature_importance.map(
                      ([feature, importance]) => (
                        <div key={feature} className="importance-item">
                          <span className="feature-name">{feature}</span>
                          <div className="importance-bar">
                            <div
                              className="importance-fill"
                              style={{ width: `${importance * 100}%` }}
                            />
                          </div>
                          <span className="importance-value">
                            {(importance * 100).toFixed(1)}%
                          </span>
                        </div>
                      )
                    )}
                  </div>
                </div>
              </div> */}
              {/*  */}
              <div className="model-details">
                <h3>Classification Model (higher)</h3>
                <p>
                  <strong>Type:</strong> {modelInfo.classification_model_higher.type}
                </p>
                <p>
                  <strong>Trees:</strong>{" "}
                  {modelInfo.classification_model_higher.n_estimators}
                </p>
                <p>
                  <strong>Max Depth:</strong>{" "}
                  {modelInfo.classification_model_higher.max_depth}
                </p>
                <div className="feature-importance">
                  <h4>Top Features (Classification)</h4>
                  <div className="importance-list">
                    {modelInfo.classification_model_higher.feature_importance.map(
                      ([feature, importance]) => (
                        <div key={feature} className="importance-item">
                          <span className="feature-name">{feature}</span>
                          <div className="importance-bar">
                            <div
                              className="importance-fill"
                              style={{ width: `${importance * 100}%` }}
                            />
                          </div>
                          <span className="importance-value">
                            {(importance * 100).toFixed(1)}%
                          </span>
                        </div>
                      )
                    )}
                  </div>
                </div>
              </div>
              {/*  */}
              <div className="model-details">
                <h3>Classification Model</h3>
                <p>
                  <strong>Type:</strong> {modelInfo.classification_model.type}
                </p>
                <p>
                  <strong>Trees:</strong>{" "}
                  {modelInfo.classification_model.n_estimators}
                </p>
                <p>
                  <strong>Max Depth:</strong>{" "}
                  {modelInfo.classification_model.max_depth}
                </p>
                <div className="feature-importance">
                  <h4>Top Features (Classification)</h4>
                  <div className="importance-list">
                    {modelInfo.classification_model.feature_importance.map(
                      ([feature, importance]) => (
                        <div key={feature} className="importance-item">
                          <span className="feature-name">{feature}</span>
                          <div className="importance-bar">
                            <div
                              className="importance-fill"
                              style={{ width: `${importance * 100}%` }}
                            />
                          </div>
                          <span className="importance-value">
                            {(importance * 100).toFixed(1)}%
                          </span>
                        </div>
                      )
                    )}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="loading">Loading model information...</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;
