import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));

// The missing JSX (App component wrapped in StrictMode)
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);