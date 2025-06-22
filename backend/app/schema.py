# backend/app/schema.py

from pydantic import BaseModel, Field  # <-- CORRECTED IMPORT: Add Field here
from typing import List, Dict, Any

# --- Schema for Input Data ---
class PatientRecord(BaseModel):
    """
    Patient voice measurement data for Parkinson's disease prediction.
    All 22 features are required.
    """
    # Fundamental frequency features
    # CORRECTED: Use Field(...) directly, not BaseModel.Field(...)
    MDVP_Fo_Hz: float = Field(..., alias='MDVP:Fo(Hz)')
    MDVP_Fhi_Hz: float = Field(..., alias='MDVP:Fhi(Hz)')
    MDVP_Flo_Hz: float = Field(..., alias='MDVP:Flo(Hz)')
    
    # Jitter features
    MDVP_Jitter_percent: float = Field(..., alias='MDVP:Jitter(%)')
    MDVP_Jitter_Abs: float = Field(..., alias='MDVP:Jitter(Abs)')
    MDVP_RAP: float = Field(..., alias='MDVP:RAP')
    MDVP_PPQ: float = Field(..., alias='MDVP:PPQ')
    Jitter_DDP: float = Field(..., alias='Jitter:DDP')
    
    # Shimmer features
    MDVP_Shimmer: float = Field(..., alias='MDVP:Shimmer')
    MDVP_Shimmer_dB: float = Field(..., alias='MDVP:Shimmer(dB)')
    Shimmer_APQ3: float = Field(..., alias='Shimmer:APQ3')
    Shimmer_APQ5: float = Field(..., alias='Shimmer:APQ5')
    MDVP_APQ: float = Field(..., alias='MDVP:APQ')
    Shimmer_DDA: float = Field(..., alias='Shimmer:DDA')
    
    # Noise features
    NHR: float
    HNR: float
    
    # Nonlinear features
    RPDE: float
    DFA: float
    spread1: float
    spread2: float
    D2: float
    PPE: float

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary with original column names"""
        # This uses the aliased names for the dictionary keys
        return self.model_dump(by_alias=True)

# --- Schema for Output Data ---
class ShapValue(BaseModel):
    feature: str
    value: float

class Explanation(BaseModel):
    shap_values: List[ShapValue]
    narrative: str

class PredictionResult(BaseModel):
    prediction: int
    probability_healthy: float
    probability_parkinsons: float
    original_data: Dict[str, Any]
    explanation: Explanation

    class Config:
        from_attributes = True

# --- Schema for Bulk Prediction Response ---
class PredictionResponse(BaseModel):
    results: List[PredictionResult]