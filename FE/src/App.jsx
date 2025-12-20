import React from 'react';
import { AuthProvider } from './contexts/AuthContext';
import { useAuth } from './hooks/useAuth';
import { AuthForm } from './components/Auth/AuthForm';
import { ChatInterface } from './components/Chat/ChatInterface';

// Helper component that handles conditional rendering based on authentication state
const AppContent = () => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    // JSX needs to be wrapped in an element, like a <div>
    return (
      <div>Loading...</div>
    );
  }

  // Ternary operator needs content for both true and false outcomes.
  // It renders ChatInterface if isAuthenticated is true, otherwise it renders AuthForm.
  return isAuthenticated ? <ChatInterface /> : <AuthForm />;
};

// Main App component that wraps the content in the AuthProvider
function App() {
  return (
    // All JSX must have a single root element.
    // The missing content was the AuthProvider wrapping AppContent.
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;