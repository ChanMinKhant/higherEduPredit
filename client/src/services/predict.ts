import apiService from './pythonApi';
import api from './nodeApi';
// Health check
export const health = async () => {
  try {
    const response = await apiService.get('/health');
    return response.data;
  } catch (error: any) {
    throw error.response || error;
  }
};

// Predict student performance
export const predict = async (studentData: any) => {
  try {
    const response = await api.post('/ml/predict', studentData);
    return response.data;
  } catch (error: any) {
    console.log(error.response);
    throw error.response || error;
  }
};

export const getRecentPredictions = async (userId: string) => {
  try {
    const response = await api.get(`/ml/predict/recent?userId=${userId}`);
    return response.data;
  } catch (error: any) {
    throw error.response || error;
  }
};

// Get model info
export const getModelInfo = async () => {
  try {
    const response = await apiService.get('/model/info');
    return response.data;
  } catch (error: any) {
    throw error.response || error;
  }
};

// Retrain models (admin)
export const retrainModels = async (params: any) => {
  try {
    const response = await apiService.post('/admin/retrain', params);
    return response.data;
  } catch (error: any) {
    throw error.response || error;
  }
};

// Get dataset stats (admin)
export const getDatasetStats = async () => {
  try {
    const response = await apiService.get('/admin/dataset/stats');
    return response.data;
  } catch (error: any) {
    throw error.response || error;
  }
};

// Get form structure
export const getFormStructure = async () => {
  try {
    const response = await apiService.get('/form/structure');
    return response.data;
  } catch (error: any) {
    throw error.response || error;
  }
};