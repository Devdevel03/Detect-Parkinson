# backend/app/explainer.py
import shap
import pandas as pd
import numpy as np
import requests # To communicate with the Ollama API
import json
from typing import Dict, List, Any

#we need the model to create the explainer

from .models import model, FEATURE_COLUMNS

#Initialize the SHAP explainer

try:
    explainer = shap.Explainer(model)
    print("SHAP explainer initialized successfully.")
except Exception as e:
    print(f"Error initializing SHAP explainer: {e}")
    explainer = None

OLLAMA_API_URL = "http://localhost:11434/api/generate"  # Adjust this URL as needed
OLLAMA_MODEL = "phi3:mini"

def generate_explanation(raw_data_df: pd.DataFrame, scaled_features: np.ndarray) -> Dict[str, Any]:
    """
    Generates both SHAP values and a narrative explanation for a prediction.

    Args:
        raw_data_df (pd.DataFrame): The original, unscaled input data (a single row).
        scaled_features (np.ndarray): The scaled features for the model (a single row).

    Returns:
        Dict[str, Any]: A dictionary containing structured SHAP values and a narrative text.
    """
    if explainer is None:
        return {
            "shap_values": [],
            "narrative": "Explanation module is not available."
        }

    # --- Generate SHAP values ---
    # shap_values will be a list of arrays if the model has multiple outputs.
    # For binary classification, we are interested in the values for the "Parkinson's" class (class 1).
    shap_values = explainer.shap_values(scaled_features)
    
    # We want the values for the first (and only) prediction passed in
    shap_values_for_instance = shap_values[0]

    # --- Generate Narrative using Ollama ---
    narrative = generate_narrative_explanation(raw_data_df.iloc[0], shap_values_for_instance)

    # --- Format SHAP values for the frontend ---
    # Create a list of dictionaries for easy plotting (e.g., with D3 or Chart.js)
    formatted_shap = []
    for feature, shap_value in zip(FEATURE_COLUMNS, shap_values_for_instance):
        formatted_shap.append({"feature": feature, "value": float(shap_value)})
    
    return {
        "shap_values": formatted_shap,
        "narrative": narrative
    }

def generate_narrative_explanation(patient_data: pd.Series, shap_values: np.ndarray) -> str:
    """
    Uses Ollama and Phi-3 to generate a human-readable explanation.
    """
    # Combine features, their actual values, and their SHAP values
    feature_impacts = []
    for feature, shap_val in zip(FEATURE_COLUMNS, shap_values):
        feature_impacts.append({
            "feature": feature,
            "value": patient_data[feature],
            "shap_value": shap_val
        })

    # Sort by the absolute SHAP value to find the most influential features
    feature_impacts.sort(key=lambda x: abs(x['shap_value']), reverse=True)
    
    # Select the top 4 most influential features for the explanation
    top_features = feature_impacts[:4]

    # --- Construct the prompt for Phi-3 ---
    prompt = f"""
    You are an expert medical assistant explaining a Parkinson's disease prediction model's result to a user who is not a data scientist.
    
    The model analyzed the following key voice measurements to make its prediction. Please provide a simple, 2-3 sentence summary explaining which factors were most influential.
    Do not use technical jargon like "SHAP values". Instead, talk about whether a feature's value "strongly suggested" or "pushed the prediction towards" a certain outcome.
    
    Here are the most important factors for this specific prediction:
    
    1. Feature: '{top_features[0]['feature']}' with a value of {top_features[0]['value']:.2f}. This was the most significant factor.
    2. Feature: '{top_features[1]['feature']}' with a value of {top_features[1]['value']:.2f}.
    3. Feature: '{top_features[2]['feature']}' with a value of {top_features[2]['value']:.2f}.
    4. Feature: '{top_features[3]['feature']}' with a value of {top_features[3]['value']:.2f}.
    
    Based on this, please generate the simple explanation.
    """
    
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False  # We want the full response at once
        }
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=700)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        
        # The response from Ollama is a stream of JSON objects, even with stream=False.
        # We parse the final one.
        response_json = json.loads(response.text)
        return response_json.get("response", "Could not generate a narrative.").strip()

    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama API: {e}")
        return "Narrative explanation is currently unavailable due to a network error."
    except Exception as e:
        print(f"An unexpected error occurred while generating narrative: {e}")
        return "An unexpected error occurred while generating the narrative."