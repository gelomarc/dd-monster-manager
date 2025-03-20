import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const BASE_URL = 'http://your-api-url/api';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// API endpoints
export const authAPI = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },
  register: async (email: string, password: string, username: string) => {
    const response = await api.post('/auth/register', {
      email,
      password,
      username,
    });
    return response.data;
  },
  logout: async () => {
    await AsyncStorage.removeItem('authToken');
  },
};

export const campaignsAPI = {
  getAll: async () => {
    const response = await api.get('/campaigns');
    return response.data;
  },
  getById: async (id: number) => {
    const response = await api.get(`/campaigns/${id}`);
    return response.data;
  },
  create: async (data: { title: string; description: string }) => {
    const response = await api.post('/campaigns', data);
    return response.data;
  },
  update: async (id: number, data: { title: string; description: string }) => {
    const response = await api.put(`/campaigns/${id}`, data);
    return response.data;
  },
  delete: async (id: number) => {
    await api.delete(`/campaigns/${id}`);
  },
};

export const encountersAPI = {
  getAll: async (campaignId: number) => {
    const response = await api.get(`/campaigns/${campaignId}/encounters`);
    return response.data;
  },
  getById: async (campaignId: number, id: number) => {
    const response = await api.get(`/campaigns/${campaignId}/encounters/${id}`);
    return response.data;
  },
  create: async (
    campaignId: number,
    data: { title: string; description: string; difficulty: string }
  ) => {
    const response = await api.post(`/campaigns/${campaignId}/encounters`, data);
    return response.data;
  },
};

export const npcsAPI = {
  getAll: async (campaignId: number) => {
    const response = await api.get(`/campaigns/${campaignId}/npcs`);
    return response.data;
  },
  getById: async (campaignId: number, id: number) => {
    const response = await api.get(`/campaigns/${campaignId}/npcs/${id}`);
    return response.data;
  },
  create: async (
    campaignId: number,
    data: {
      name: string;
      role: string;
      attitude: string;
      description: string;
    }
  ) => {
    const response = await api.post(`/campaigns/${campaignId}/npcs`, data);
    return response.data;
  },
};

export const lootAPI = {
  getAll: async (campaignId: number, encounterId: number) => {
    const response = await api.get(
      `/campaigns/${campaignId}/encounters/${encounterId}/loot`
    );
    return response.data;
  },
  create: async (
    campaignId: number,
    encounterId: number,
    data: {
      name: string;
      description: string;
      value: string;
      quantity: number;
    }
  ) => {
    const response = await api.post(
      `/campaigns/${campaignId}/encounters/${encounterId}/loot`,
      data
    );
    return response.data;
  },
};

export default api; 