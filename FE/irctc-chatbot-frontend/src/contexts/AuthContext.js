import React, { createContext, useState, useEffect } from 'react';
import { authAPI } from '../api/auth';
import { storage } from '../utils/storage';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = storage.getAccessToken();
    const savedUser = storage.getUser();

    if (token && savedUser) {
      setIsAuthenticated(true);
      setUser(savedUser);
    }

    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const data = await authAPI.login(email, password);
    setIsAuthenticated(true);
    setUser({ email });
    return data;
  };

  const signup = async (email, password) => {
    const data = await authAPI.signup(email, password);
    setIsAuthenticated(true);
    setUser({ email });
    return data;
  };

  const logout = () => {
    authAPI.logout();
    setIsAuthenticated(false);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        user,
        loading,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
