import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css'; // We'll create a basic CSS file next
import App from './App';

// Find the root element from our HTML file
const container = document.getElementById('root');

// Create a root for the React application
const root = createRoot(container);

// Render the main App component
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);