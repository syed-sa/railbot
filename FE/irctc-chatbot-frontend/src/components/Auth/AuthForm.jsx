import React, { useState } from 'react';
import { Train, Loader2 } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { Button } from '../common/Button';
import { Input } from '../common/Input';

export const AuthForm = () => {
  const [authMode, setAuthMode] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login, signup } = useAuth();

  const handleSubmit = async () => {
    // Prevent submitting if fields are empty
    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }

    setError('');
    setLoading(true);

    try {
      if (authMode === 'login') {
        await login(email, password);
      } else {
        await signup(email, password);
      }
    } catch (err) {
      // Assuming the error object has a 'message' property
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    // Check for 'Enter' key press and ensure fields are not empty before submitting
    if (e.key === 'Enter' && email && password) {
      handleSubmit();
    }
  };

  return (
    // 1. Root container (e.g., full screen center alignment)
    <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
      
      {/* 2. Card/Form container */}
      <div className="bg-white p-8 rounded-xl shadow-2xl w-full max-w-md">
        
        {/* Header/Branding Section */}
        <div className="flex flex-col items-center mb-6">
          
          {/* Icon */}
          <div className="p-3 bg-indigo-100 rounded-full mb-3">
            <Train className="w-8 h-8 text-indigo-600" />
          </div>
          
          {/* Title */}
          <h1 className="text-3xl font-bold text-gray-900 mb-1">
            IRCTC Chatbot
          </h1>
          
          {/* Subtitle */}
          <p className="text-gray-500 text-center">
            Your AI assistant for train information
          </p>
          
        </div>

        {/* Login/Sign Up Mode Toggle Buttons */}
        <div className="flex space-x-2 bg-gray-100 p-1 rounded-lg mb-6">
          <button
            onClick={() => setAuthMode('login')}
            className={`flex-1 py-2 rounded-lg font-medium transition-colors ${
              authMode === 'login'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-gray-600 hover:bg-white'
            }`}
          >
            Login
          </button>
          
          <button
            onClick={() => setAuthMode('signup')}
            className={`flex-1 py-2 rounded-lg font-medium transition-colors ${
              authMode === 'signup'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-gray-600 hover:bg-white'
            }`}
          >
            Sign Up
          </button>
        </div>

        {/* Form Fields Section */}
        <div className="space-y-6">
          
          <Input
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your email"
          />
          
          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your password"
          />

          {error && (
            <div className="text-red-600 text-sm font-medium p-2 bg-red-50 rounded-lg border border-red-200">
              {error}
            </div>
          )}

          <Button 
            onClick={handleSubmit} 
            disabled={loading || !email || !password} // Disable if loading or fields are empty
            className="w-full h-12 bg-indigo-600 text-white hover:bg-indigo-700"
          >
            {loading ? (
              <div className="flex items-center justify-center">
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                <span>Processing...</span>
              </div>
            ) : (
              authMode === 'login' ? 'Login' : 'Sign Up'
            )}
          </Button>
          
        </div>
      </div>
    </div>
  );
};