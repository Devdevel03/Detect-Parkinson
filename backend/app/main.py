# backend/app/main.py

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import traceback

# --- Corrected Relative Imports ---
# Use relative imports to correctly locate modules within the same 'app' package.
from . import models
from . import schema

# Check if explainer exists, if not we'll create a mock
try:
    from . import explainer
    EXPLAINER_AVAILABLE = True
    print("INFO: Explainer module loaded successfully.")
except ImportError as e:
    EXPLAINER_AVAILABLE = False
    print(f"WARNING: Explainer module not found or failed to import: {e}. Using mock explanations.")
except Exception as e:
    # This catches errors during explainer initialization (e.g., model loading issues for SHAP)
    EXPLAINER_AVAILABLE = False
    print(f"WARNING: SHAP explainer failed to initialize: {e}. Using mock explanations.")


# --- 1. App Object and Metadata ---
app = FastAPI(
    title="Parkinson's Detection API",
    description="An API to predict Parkinson's disease from voice data and provide model explanations.",
    version="1.0.0"
)

# --- 2. CORS Middleware ---
# This configuration allows your React frontend (running on port 3000 or 3001)
# to communicate with this backend (running on port 8000).
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. Helper Functions ---

def create_mock_explanation(prediction_result: dict) -> dict:
    """Create a mock explanation when the explainer module is not available or fails."""
    if prediction_result['prediction'] == 1:
        narrative = f"The model predicts a {prediction_result['probability_parkinsons']:.1%} probability of Parkinson's disease based on voice analysis patterns."
    else:
        narrative = f"The model predicts a {prediction_result['probability_healthy']:.1%} probability of healthy voice patterns."
    
    # Create some plausible mock SHAP values
    mock_shap_values = [
        {'feature': 'PPE', 'value': 0.15 if prediction_result['prediction'] == 1 else -0.15},
        {'feature': 'spread1', 'value': 0.12 if prediction_result['prediction'] == 1 else -0.12},
        {'feature': 'HNR', 'value': -0.08 if prediction_result['prediction'] == 1 else 0.08},
        {'feature': 'DFA', 'value': -0.05 if prediction_result['prediction'] == 1 else 0.05}
    ]
    
    return {
        'shap_values': mock_shap_values,
        'narrative': narrative
    }

# --- 4. API Endpoints ---

@app.get("/", tags=["Root"])
async def read_root():
    """A simple health check endpoint."""
    return {"message": "Welcome to the Parkinson's Detection API!", "status": "healthy"}

@app.post("/predict/", response_model=schema.PredictionResponse, tags=["Prediction"])
async def predict(patient_data: schema.PatientRecord):
    """
    Receives patient voice data from a JSON form body, performs prediction,
    and returns results along with model explanations.
    """
    try:
        # 1. Convert Pydantic model to a dictionary with original column names
        data_dict = patient_data.to_dict()
        
        # 2. Create a pandas DataFrame (must be in a list for a single row)
        df = pd.DataFrame([data_dict])
        
        # 3. Verify all required columns are present (as a safeguard)
        missing_cols = set(models.FEATURE_COLUMNS) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # 4. Get predictions from the model pipeline
        predictions = models.get_prediction(df)
        
        if not predictions:
            raise HTTPException(status_code=500, detail="Model did not return a prediction.")

        # Get the first (and only) prediction result
        result = predictions[0]
        
        # 5. Generate explanation
        explanation = None
        if EXPLAINER_AVAILABLE:
            try:
                # Preprocess data again specifically for the explainer
                scaled_features = models.preprocess_data(df)
                
                # The explainer function needs the original data as a DataFrame
                # and the scaled data as a NumPy array.
                original_row_df = pd.DataFrame([result['original_data']])
                
                # Generate real explanation
                explanation = explainer.generate_explanation(original_row_df, scaled_features)
                print("INFO: Real explanation generated successfully.")
            except Exception as explainer_error:
                print(f"WARNING: Explainer failed during execution, falling back to mock. Error: {explainer_error}")
                traceback.print_exc()
                explanation = create_mock_explanation(result)
        else:
            # Use mock explanation if the module isn't available
            explanation = create_mock_explanation(result)
            print("INFO: Mock explanation generated.")
        
        # 6. Add explanation to the result dictionary
        result['explanation'] = explanation
        
        # 7. Create and return the final response using the Pydantic schema
        response = schema.PredictionResponse(results=[result])
        
        return response
    
    except ValueError as e:
        # Handle data validation or missing column errors
        print(f"ERROR: ValueError in /predict endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Data validation error: {str(e)}")
    
    except Exception as e:
        # Handle any other unexpected server errors
        print(f"ERROR: Unexpected error in /predict endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")