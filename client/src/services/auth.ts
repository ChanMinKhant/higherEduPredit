import apiService from './nodeApi';

const authBaseUrl = 'auth';

export const register = async (userData: any) => {
  try {
    const response = await apiService.post(`${authBaseUrl}/register`, userData);
    return response.data;
  } catch (error: any) {
    throw error.response;
  }
};

export const login = async (userData: any) => {
  try {
    const response = await apiService.post(`${authBaseUrl}/login`, userData);
    return response.data;
  } catch (error: any) {
    throw error.response;
  }
};

//submit otp
export const submitOtp = async (email: String, otp: String) => {
  try {
    const response = await apiService.post(`${authBaseUrl}/submit-otp`, {
      email,
      otp,
    });
    return response.data;
  } catch (error: any) {
    throw error.response;
  }
};

export const resendOtp = async (email: String) => {
  try {
    const response = await apiService.post(`${authBaseUrl}/resend-otp`, {
      email,
    });
    return response.data;
  } catch (error: any) {
    throw error.response;
  }
};

export const getUser = async () => {
  try {
    const response = await apiService.get(`${authBaseUrl}/get-user`);
    return response.data;
  } catch (error: any) {
    throw error.response;
  }
};

export const getAllUsers = async () => {
   try {
    const response = await apiService.get(`${authBaseUrl}/users`);
    return response.data;
  } catch (error: any) {
    throw error.response;
  }
};


// ✅ Create a new user
export const createUser = async (userData: {
  username: string;
  email: string;
  password: string;
  role: string;
}) => {
  try {
    const response = await apiService.post(`${authBaseUrl}/users`, userData);
    return response.data;
  } catch (error: any) {
    throw error.response;
  }
};

// ✅ Update an existing user
export const updateUser = async (id: string, userData: {
  username: string;
  email: string;
  password: string;
  role: string;
}) => {
  try {
    const response = await apiService.put(`${authBaseUrl}/users/${id}`, userData);
    return response.data;
  } catch (error: any) {
    throw error.response;
  }
};

// ✅ Delete a user
export const deleteUser = async (id: string) => {
  try {
    const response = await apiService.delete(`${authBaseUrl}/users/${id}`);
    return response.data;
  } catch (error: any) {
    throw error.response;
  }
};

export const logout = async () => {
  try {
    const response = await apiService.post(`${authBaseUrl}/logout`);
    return response.data;
  } catch (error: any) {
    throw error.response;
  }
};
