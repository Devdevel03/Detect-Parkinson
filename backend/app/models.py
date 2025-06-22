# backend/app/models.py

import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from xgboost import XGBClassifier # Imported for type hinting and instance checks

# --- 1. Model and Scaler Loading ---

# Get the base directory of the current file
# This makes the path independent of where the script is run from
BASE_DIR = Path(__file__).resolve(strict=True).parent

# Define paths to the pre-trained model and scaler
MODEL_PATH = BASE_DIR / "parkinsons_model.joblib"
SCALER_PATH = BASE_DIR / "parkinsons_scaler.joblib"

# Load the assets
# A comment on how to create these files is crucial, as the provided script doesn't save them.
# To create these files, add the following lines to the end of the training script:
#
# import joblib
# joblib.dump(model, 'parkinsons_model.joblib')
# joblib.dump(scaler, 'parkinsons_scaler.joblib')
#
# Then, place the generated .joblib files in the same directory as this models.py file.
try:
    model: XGBClassifier = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
except FileNotFoundError:
    # This provides a clear error message if the app is started without the necessary files.
    raise RuntimeError(
        f"Model file not found at {MODEL_PATH} or scaler not found at {SCALER_PATH}. "
        "Please run the training script and save the model/scaler using joblib."
    )

# --- 2. Feature Definition ---

# Define the feature columns based on the training script.
# The script uses all columns except 'status' (target) and 'name' (identifier).
# df.loc[:,df.columns!='status'].values[:,1:]
# Explicitly listing them ensures order and prevents errors if CSV columns change.
# This is our single source of truth for feature names
FEATURE_COLUMNS = [
    'MDVP:Fo(Hz)', 'MDVP:Fhi(Hz)', 'MDVP:Flo(Hz)', 'MDVP:Jitter(%)',
    'MDVP:Jitter(Abs)', 'MDVP:RAP', 'MDVP:PPQ', 'Jitter:DDP',
    'MDVP:Shimmer', 'MDVP:Shimmer(dB)', 'Shimmer:APQ3', 'Shimmer:APQ5',
    'MDVP:APQ', 'Shimmer:DDA', 'NHR', 'HNR', 'RPDE', 'DFA',
    'spread1', 'spread2', 'D2', 'PPE'
]

# --- 3. Preprocessing and Prediction Pipeline ---

def preprocess_data(data: pd.DataFrame) -> np.ndarray:
    """
    Validates and preprocesses the input data.
    
    Args:
        data (pd.DataFrame): The raw data from the uploaded CSV.
    
    Returns:
        np.ndarray: The scaled feature data ready for the model.
        
    Raises:
        ValueError: If required columns are missing.
    """
    # Check for the presence of all required feature columns
    missing_cols = set(FEATURE_COLUMNS) - set(data.columns)
    if missing_cols:
        raise ValueError(f"The following required columns are missing from the input data: {', '.join(missing_cols)}")

    # Ensure data is in the correct order and drop any extra columns
    features = data[FEATURE_COLUMNS]
    
    # Apply the pre-trained scaler
    scaled_features = scaler.transform(features)
    
    return scaled_features


def get_prediction(data: pd.DataFrame) -> list[dict]:
    """
    Takes a DataFrame of patient data, preprocesses it, and returns predictions.

    Args:
        data (pd.DataFrame): DataFrame containing one or more rows of patient data.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary contains the
                    prediction results ('prediction', 'probability_healthy', 
                    'probability_parkinsons') and original data for a single patient.
    """
    # Preprocess the data using the helper function
    scaled_features = preprocess_data(data)

    # Get class predictions (0 or 1)
    predictions = model.predict(scaled_features)
    
    # Get class probabilities [[P(0), P(1)], [P(0), P(1)], ...]
    probabilities = model.predict_proba(scaled_features)

    # Format the results into a list of dictionaries
    results = []
    # Combine original data with the predictions for a comprehensive output
    # `to_dict('records')` is a convenient way to iterate over DataFrame rows as dictionaries
    for i, record in enumerate(data.to_dict('records')):
        results.append({
            'prediction': int(predictions[i]),  # 0 for healthy, 1 for Parkinson's
            'probability_healthy': float(probabilities[i][0]),
            'probability_parkinsons': float(probabilities[i][1]),
            'original_data': record  # Include the original input data for context
        })
        
    return results