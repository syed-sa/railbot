import React from 'react';
import { Train, LogOut } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';

export const ChatHeader = () => {
  const { logout } = useAuth();

  return (
    // 1. Root container for the header (flex layout, padding, background)
    <header className="chat-header-container flex justify-between items-center p-4 border-b border-gray-200 bg-white">
      
      {/* 2. Left section: Icon and Title/Subtitle */}
      <div className="flex items-center space-x-3">
        
        {/* Train Icon (assuming Train is imported from lucide-react) */}
        <Train className="w-8 h-8 text-blue-600" />
        
        {/* Title and Subtitle container */}
        <div className="flex flex-col">
          {/* Main Title */}
          <h1 className="text-xl font-semibold text-gray-800">
            IRCTC Assistant
          </h1>
          {/* Subtitle/Tagline */}
          <p className="text-sm text-gray-500">
            Always here to help
          </p>
        </div>
        
      </div>
      
      {/* 3. Right section: Logout Button */}
      <button 
        onClick={logout} 
        className="flex items-center space-x-1 p-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition duration-150"
        title="Logout"
      >
        <LogOut className="w-5 h-5" />
        <span>Logout</span>
      </button>
      
    </header>
  );
};