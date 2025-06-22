// frontend/src/api.js

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export async function getPredictionFromForm(patientData) {
  console.log('Sending prediction request to:', `${API_BASE_URL}/predict/`);
  console.log('Patient data:', patientData);
  
  try {
    const response = await fetch(`${API_BASE_URL}/predict/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(patientData),
    });

    console.log('Response status:', response.status);
    console.log('Response headers:', response.headers);

    // Check if the response is ok
    if (!response.ok) {
      // Try to get error details from the response
      let errorData;
      try {
        errorData = await response.json();
      } catch (jsonError) {
        // If we can't parse JSON, use the status text
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      // Create an error object with the details
      const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
      error.detail = errorData.detail || errorData.message || 'Unknown error occurred';
      throw error;
    }

    const data = await response.json();
    console.log('Prediction response:', data);
    return data;

  } catch (error) {
    console.error('API call failed:', error);
    
    // Handle different types of errors
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      // Network connectivity issues
      const networkError = new Error('Unable to connect to the server. Please check if the backend is running.');
      networkError.detail = 'Network connectivity issue - ensure your FastAPI server is running on the correct port.';
      throw networkError;
    }
    
    // Re-throw other errors as-is
    throw error;
  }
}

// Health check function to test backend connectivity
export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }
    
    const data = await response.json();
    return { status: 'healthy', data };
  } catch (error) {
    console.error('Backend health check failed:', error);
    return { status: 'unhealthy', error: error.message };
  }
}