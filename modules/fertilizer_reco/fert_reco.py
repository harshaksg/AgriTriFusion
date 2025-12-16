# modules/fertilizer_reco/fert_reco.py

import os
import joblib
import pandas as pd

# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "saved_models")

_preprocessor = None
_priority_models = None


# --------------------------------------------------
# Load models (lazy loading)
# --------------------------------------------------

def _load_models():
    global _preprocessor, _priority_models

    if _preprocessor is None:
        _preprocessor = joblib.load(
            os.path.join(MODEL_DIR, "fertilizer_preprocessor.joblib")
        )

    if _priority_models is None:
        _priority_models = joblib.load(
            os.path.join(MODEL_DIR, "nutrient_priority_models.joblib")
        )


# --------------------------------------------------
# MAIN FUNCTION (PIPELINE SAFE)
# --------------------------------------------------

def recommend_fertilizer(
    crop_name: str,
    crop_stage: str,
    N_mgkg: float,
    P_mgkg: float,
    K_mgkg: float
):
    """
    Fertilizer recommendation using XGBoost priority models

    Inputs:
    - crop_name  : from Abhi (tomato / banana / mango / papaya)
    - crop_stage : from Abhi (unripe / semiripe / ripe)
    - N_mgkg     : Nitrogen from soil test
    - P_mgkg     : Phosphorus from soil test
    - K_mgkg     : Potassium from soil test
    """

    _load_models()

    # --------------------------------------------------
    # DEFAULT AGRONOMIC VALUES
    # --------------------------------------------------

    DEFAULTS = {
        "temperature": 28.0,
        "humidity": 65.0,
        "soil_moisture": 40.0,
        "irrigation_type": "drip",
        "crop_age_days": 45,
        "plant_spacing_cm": 45,
        "yield_target_ton_acre": 20,
        "soil_PH": 6.5
    }

    # --------------------------------------------------
    # Build FULL feature vector
    # --------------------------------------------------

    input_df = pd.DataFrame([{
        "crop": crop_name.lower(),
        "stage": crop_stage.lower(),

        "N_mgkg": N_mgkg,
        "P_mgkg": P_mgkg,
        "K_mgkg": K_mgkg,

        "temperature": DEFAULTS["temperature"],
        "humidity": DEFAULTS["humidity"],
        "soil_moisture": DEFAULTS["soil_moisture"],
        "irrigation_type": DEFAULTS["irrigation_type"],
        "crop_age_days": DEFAULTS["crop_age_days"],
        "plant_spacing_cm": DEFAULTS["plant_spacing_cm"],
        "yield_target_ton_acre": DEFAULTS["yield_target_ton_acre"],
        "soil_PH": DEFAULTS["soil_PH"],
    }])

    # --------------------------------------------------
    # Preprocess
    # --------------------------------------------------

    X = _preprocessor.transform(input_df)

    # --------------------------------------------------
    # Run all three XGBoost models
    # --------------------------------------------------

    scores = {
        "N": _priority_models["N_priority"].predict(X)[0],
        "P": _priority_models["P_priority"].predict(X)[0],
        "K": _priority_models["K_priority"].predict(X)[0],
    }

    # Determine priority nutrient
    priority = max(scores, key=scores.get)

    # --------------------------------------------------
    # Final recommendation
    # --------------------------------------------------

    recommendation = {
        "Nitrogen (N)": "Increase" if priority == "N" else "Normal",
        "Phosphorus (P)": "Increase" if priority == "P" else "Normal",
        "Potassium (K)": "Increase" if priority == "K" else "Normal",
    }

    return {
        "crop": crop_name,
        "stage": crop_stage,
        "soil_nutrients": {
            "N_mgkg": N_mgkg,
            "P_mgkg": P_mgkg,
            "K_mgkg": K_mgkg
        },
        "used_defaults": DEFAULTS,
        "priority_scores": scores,
        "priority_nutrient": priority,
        "fertilizer_recommendation": recommendation
    }
