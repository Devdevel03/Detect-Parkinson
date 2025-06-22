import React, { useState } from 'react';
import './PredictionForm.css';

// We need the feature names to generate the form
const FEATURE_COLUMNS = [
    'MDVP:Fo(Hz)', 'MDVP:Fhi(Hz)', 'MDVP:Flo(Hz)', 'MDVP:Jitter(%)',
    'MDVP:Jitter(Abs)', 'MDVP:RAP', 'MDVP:PPQ', 'Jitter:DDP',
    'MDVP:Shimmer', 'MDVP:Shimmer(dB)', 'Shimmer:APQ3', 'Shimmer:APQ5',
    'MDVP:APQ', 'Shimmer:DDA', 'NHR', 'HNR', 'RPDE', 'DFA',
    'spread1', 'spread2', 'D2', 'PPE'
];

// Let's create some sensible default values for the form from our sample data
const defaultFormData = {
    'MDVP:Fo(Hz)': 135.32, 'MDVP:Fhi(Hz)': 152.45, 'MDVP:Flo(Hz)': 105.88,
    'MDVP:Jitter(%)': 0.0075, 'MDVP:Jitter(Abs)': 0.00006, 'MDVP:RAP': 0.0039,
    'MDVP:PPQ': 0.0045, 'Jitter:DDP': 0.0117, 'MDVP:Shimmer': 0.0413,
    'MDVP:Shimmer(dB)': 0.382, 'Shimmer:APQ3': 0.0216, 'Shimmer:APQ5': 0.0259,
    'MDVP:APQ': 0.0331, 'Shimmer:DDA': 0.0648, 'NHR': 0.0182, 'HNR': 20.61,
    'RPDE': 0.536, 'DFA': 0.765, 'spread1': -5.12, 'spread2': 0.245, 'D2': 2.45, 'PPE': 0.258
};

function PredictionForm({ onPredict, disabled }) {
  const [formData, setFormData] = useState(defaultFormData);

  const handleChange = (e) => {
    const { name, value } = e.target;
    // Convert to number, but allow empty string for typing
    const numericValue = value === '' ? '' : Number(value);
    setFormData(prevData => ({
      ...prevData,
      [name]: numericValue,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onPredict(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="prediction-form">
      <h3>Enter Patient Voice Measurements</h3>
      <div className="form-grid">
        {FEATURE_COLUMNS.map(feature => (
          <div key={feature} className="form-group">
            <label htmlFor={feature}>{feature}</label>
            <input
              type="number"
              id={feature}
              name={feature}
              value={formData[feature]}
              onChange={handleChange}
              step="any" // Allow floating point numbers
              required
              disabled={disabled}
            />
          </div>
        ))}
      </div>
      <button type="submit" disabled={disabled}>
        {disabled ? 'Analyzing...' : 'Get Prediction'}
      </button>
    </form>
  );
}

export default PredictionForm;