import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './AdminPanel.css';

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
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);
  const [datasetStats, setDatasetStats] = useState<DatasetStats | null>(null);
  const [retrainParams, setRetrainParams] = useState<RetrainParams>({
    n_estimators: 100,
    max_depth: 10,
    min_samples_split: 5,
    min_samples_leaf: 2,
    difficulty: 0.5,
    basedScore: 20,
  });
  const [retraining, setRetraining] = useState(false);
  const [message, setMessage] = useState<string>('');
  const [messageType, setMessageType] = useState<'success' | 'error' | ''>('');

  const API_BASE = 'http://localhost:5000/api';

  useEffect(() => {
    fetchModelInfo();
    fetchDatasetStats();
  }, []);

  const fetchModelInfo = async () => {
    try {
      const response = await axios.get(`${API_BASE}/model/info`);
      setModelInfo(response.data);
    } catch (error) {
      console.error('Error fetching model info:', error);
      showMessage('Failed to load model information', 'error');
    }
  };

  const fetchDatasetStats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/admin/dataset/stats`);
      setDatasetStats(response.data);
    } catch (error) {
      console.error('Error fetching dataset stats:', error);
      showMessage('Failed to load dataset statistics', 'error');
    }
  };

  const showMessage = (msg: string, type: 'success' | 'error') => {
    setMessage(msg);
    setMessageType(type);
    setTimeout(() => {
      setMessage('');
      setMessageType('');
    }, 5000);
  };

  const handleRetrainModels = async () => {
    setRetraining(true);
    try {
      const response = await axios.post(`${API_BASE}/admin/retrain`, retrainParams);
      showMessage(
        `Models retrained successfully! Regression R²: ${response.data.performance.regression_r2}, Classification Accuracy: ${response.data.performance.classification_accuracy}`,
        'success'
      );
      // Refresh model info after retraining
      await fetchModelInfo();
    } catch (error: any) {
      showMessage(error.response?.data?.error || 'Failed to retrain models', 'error');
    } finally {
      setRetraining(false);
    }
  };

  const handleParamChange = (param: keyof RetrainParams, value: number) => {
    setRetrainParams(prev => ({
      ...prev,
      [param]: value
    }));
  };

  return (
    <div className="admin-panel">
      <h1>Admin Panel</h1>
      
      {message && (
        <div className={`message ${messageType}`}>
          {message}
        </div>
      )}

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
                <div className="stat-value">{datasetStats.total_features}</div>
              </div>
              <div className="stat-card">
                <h3>Mean Grade</h3>
                <div className="stat-value">{datasetStats.target_stats.mean_grade}</div>
              </div>
              <div className="stat-card">
                <h3>Pass Rate</h3>
                <div className="stat-value">{datasetStats.target_stats.pass_rate}%</div>
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
                  onChange={(e) => handleParamChange('n_estimators', Number(e.target.value))}
                />
                <span className="param-value">{retrainParams.n_estimators}</span>
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
                  onChange={(e) => handleParamChange('max_depth', Number(e.target.value))}
                />
                <span className="param-value">{retrainParams.max_depth}</span>
                <small>Controls how deep each tree can grow (overfitting prevention)</small>
              </div>

              <div className="param-group">
                <label>Min Samples Split (min_samples_split)</label>
                <input
                  type="range"
                  min="2"
                  max="20"
                  step="1"
                  value={retrainParams.min_samples_split}
                  onChange={(e) => handleParamChange('min_samples_split', Number(e.target.value))}
                />
                <span className="param-value">{retrainParams.min_samples_split}</span>
                <small>Minimum samples required to split a node</small>
              </div>

              <div className="param-group">
                <label>Min Samples Leaf (min_samples_leaf)</label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  step="1"
                  value={retrainParams.min_samples_leaf}
                  onChange={(e) => handleParamChange('min_samples_leaf', Number(e.target.value))}
                />
                <span className="param-value">{retrainParams.min_samples_leaf}</span>
                <small>Minimum samples required at each leaf node</small>
              </div>

              {/* difficulty 0.1 to 0.9 default 0.5 */}
              <div className="param-group">
                <label>Difficulty</label>
                <input
                  type="range"
                  min="0.1"
                  max="0.9"
                  step="0.1"
                  value={retrainParams.difficulty}
                  onChange={(e) => handleParamChange('difficulty', Number(e.target.value))}
                />
                <span className="param-value">{retrainParams.difficulty}</span>
                <small>Controls the difficulty of the training data</small>
              </div>

              {/* basedScore 1 to 100, default 20 */}
              <div className="param-group">
                <label>Based Score</label>
                <input
                  type="range"
                  min="1"
                  max="100"
                  step="1"
                  value={retrainParams.basedScore}
                  onChange={(e) => handleParamChange('basedScore', Number(e.target.value))}
                />
                <span className="param-value">{retrainParams.basedScore}</span>
                <small>Controls the based score of the training data</small>
              </div>

            </div>

            <button
              className="retrain-button"
              onClick={handleRetrainModels}
              disabled={retraining}
            >
              {retraining ? 'Retraining Models...' : 'Retrain Models'}
            </button>
          </div>
        </div>

        {/* Current Model Info */}
        <div className="admin-section">
          <h2>Current Model Information</h2>
          {modelInfo ? (
            <div className="model-info">
              <div className="model-details">
                <h3>Regression Model</h3>
                <p><strong>Type:</strong> {modelInfo.regression_model.type}</p>
                <p><strong>Trees:</strong> {modelInfo.regression_model.n_estimators}</p>
                <p><strong>Max Depth:</strong> {modelInfo.regression_model.max_depth}</p>
                <div className="feature-importance">
                  <h4>Top Features (Regression)</h4>
                  <div className="importance-list">
                    {modelInfo.regression_model.feature_importance.slice(0, 5).map(([feature, importance]) => (
                      <div key={feature} className="importance-item">
                        <span className="feature-name">{feature}</span>
                        <div className="importance-bar">
                          <div 
                            className="importance-fill"
                            style={{ width: `${importance * 100}%` }}
                          />
                        </div>
                        <span className="importance-value">{(importance * 100).toFixed(1)}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="model-details">
                <h3>Classification Model</h3>
                <p><strong>Type:</strong> {modelInfo.classification_model.type}</p>
                <p><strong>Trees:</strong> {modelInfo.classification_model.n_estimators}</p>
                <p><strong>Max Depth:</strong> {modelInfo.classification_model.max_depth}</p>
                <div className="feature-importance">
                  <h4>Top Features (Classification)</h4>
                  <div className="importance-list">
                    {modelInfo.classification_model.feature_importance.slice(0, 5).map(([feature, importance]) => (
                      <div key={feature} className="importance-item">
                        <span className="feature-name">{feature}</span>
                        <div className="importance-bar">
                          <div 
                            className="importance-fill"
                            style={{ width: `${importance * 100}%` }}
                          />
                        </div>
                        <span className="importance-value">{(importance * 100).toFixed(1)}%</span>
                      </div>
                    ))}
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