import React, { useState } from 'react';

// --- Step 1: Import the new components and API functions ---
// We now import PredictionForm instead of UploadForm.
import PredictionForm from './components/PredictionForm';
// We import getPredictionFromForm instead of uploadAndPredict.
import { getPredictionFromForm } from './api';

// These components for displaying results remain the same.
import Gauge from './components/Gauge';
import ShapBar from './components/ShapBar';

// Import the stylesheet.
import './App.css';

function App() {
  // --- Step 2: State management remains the same ---
  // This state is perfect for our workflow, regardless of the input method.
  const [predictionData, setPredictionData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // --- Step 3: Update the prediction handler function ---
  // It now receives a 'patientData' object from the form, not a 'formData' object.
  const handlePrediction = async (patientData) => {
    setIsLoading(true);
    setError('');
    setPredictionData(null);
    try {
      const data = await getPredictionFromForm(patientData);
      setPredictionData(data.results[0]); 

    } catch (err) {
      // **THE FIX**: Make the error handling more robust.
      let errorMessage = 'An unexpected error occurred. Please check the values and try again.';
      
      // Check if this is a detailed validation error from FastAPI
      if (err.detail && Array.isArray(err.detail)) {
        // Grab the message from the first validation error
        errorMessage = err.detail[0].msg || 'A validation error occurred.';
      } else if (err.detail) {
        // Handle cases where err.detail is a simple string
        errorMessage = err.detail;
      }
      
      setError(errorMessage);

    } finally {
      setIsLoading(false);
    }
  };

  // --- Step 4: Update the rendered JSX ---
  return (
    <div className="App">
      <header className="App-header">
        <h1>Parkinson's Disease Detection Dashboard</h1>
      </header>
      <main>
        {/*
          Replace the old <UploadForm /> with our new <PredictionForm />.
          The props we pass ('onPredict' and 'disabled') are the same.
        */}
        <PredictionForm onPredict={handlePrediction} disabled={isLoading} />
        
        {/* 
          The rest of the component for displaying loading, error, and results
          is completely unchanged, which shows the power of good component design.
        */}
        {isLoading && <div className="loading">Analyzing...</div>}
        
        {error && <div className="error-message">Error: {error}</div>}
        
        {predictionData && (
          <div className="results-container">
            <h2>Prediction Result</h2>
            <div className="results-grid">
              <div className="gauge-card">
                <h3>Prediction Probability</h3>
                <Gauge probability={predictionData.probability_parkinsons} />
              </div>
              <div className="narrative-card">
                 <h3>AI Explanation</h3>
                 <p>{predictionData.explanation.narrative}</p>
              </div>
            </div>
            
            <div className="shap-card">
              <h3>Feature Influence Analysis (SHAP)</h3>
              <p>This chart shows which voice features had the biggest impact on the prediction. Red bars indicate features pushing the prediction towards "Parkinson's," and blue bars indicate features pushing it towards "Healthy."</p>
              <ShapBar shapValues={predictionData.explanation.shap_values} />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;