import { ENDPOINTS } from '../utils/constants';
import { apiClient } from '../utils/api';
import { storage } from '../utils/storage';

export const authAPI = {
  async login(username, password) {
    const data = await apiClient.post(ENDPOINTS.AUTH.LOGIN, { username, password });
    
    storage.setAccessToken(data.access_token);
    storage.setRefreshToken(data.refresh_token);
    storage.setUser({ username });
    
    return data;
  },

  async signup(username, password) {
    const data = await apiClient.post(ENDPOINTS.AUTH.SIGNUP, { username, password });
    
    storage.setAccessToken(data.access_token);
    storage.setRefreshToken(data.refresh_token);
    storage.setUser({ username });
    
    return data;
  },

  async refreshToken() {
    const refreshToken = storage.getRefreshToken();
    const data = await apiClient.post(ENDPOINTS.AUTH.REFRESH, { token: refreshToken });
    
    storage.setAccessToken(data.access_token);
    
    return data;
  },

  logout() {
    storage.clear();
  },

  isAuthenticated() {
    return !!storage.getAccessToken();
  },
};