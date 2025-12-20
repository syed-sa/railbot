
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/v1/user/login',
    SIGNUP: '/api/v1/user/signup',
    REFRESH: '/api/v1/user/refresh-token',
  },
  CHAT: '/api/v1/chat/',
};

export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER: 'user',
};

export const WELCOME_MESSAGE = `👋 Hello! I'm your IRCTC assistant. I can help you with:

• PNR Status
• Live Train Status
• Train Schedule
• Seat Availability
• Trains between stations
• Search trains & stations
• Fare information

How can I assist you today?`;
