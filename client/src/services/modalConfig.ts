import apiService from './nodeApi';

// Get all configs (public)
export const getConfigs = async () => {
  try {
    const response = await apiService.get(`/config/model-config`);
    return response.data;
  } catch (error: any) {
    throw error.response;
  }
};

// Get single config (requires auth)
export const getConfigById = async (id: string) => {
  try {
    const response = await apiService.get(`/config/model-config/${id}`);
    return response.data;
  } catch (error: any) {
    throw error.response;
  }
};

// Create config (requires auth)
export const createConfig = async (configData: any) => {
  try {
    const response = await apiService.post(`/config/model-config`, configData);
    return response.data;
  } catch (error: any) {
    throw error.response;
  }
};

// Update config (requires auth)
export const updateConfig = async (id: string, configData: any) => {
  try {
    const response = await apiService.put(`/config/model-config/${id}`, configData);
    return response.data;
  } catch (error: any) {
    throw error.response;
  }
};

// Delete config (requires auth)
export const deleteConfig = async (id: string) => {
  try {
    const response = await apiService.delete(`/config/model-config/${id}`);
    return response.data;
  } catch (error: any) {
    throw error.response;
  }
};
