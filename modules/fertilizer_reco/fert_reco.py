import os
import joblib
import numpy as np
import pandas as pd

# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "saved_models")

_preprocessor = None
_priority_models = None


# --------------------------------------------------
# Load ML models (only once)
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
# Main fertilizer recommendation function
# --------------------------------------------------
def recommend_fertilizer(
    crop: str,
    stage: str,
    N_mgkg: float,
    P_mgkg: float,
    K_mgkg: float,
):
    """
    Crop + stage comes from Abhi
    NPK comes from manual user input
    Other features use safe default values
    """

    _load_models()

    # -----------------------------
    # Default values (as agreed)
    # -----------------------------
    input_data = pd.DataFrame([{
        "crop": crop,
        "stage": stage,
        "temperature": 28.0,
        "humidity": 65.0,
        "soil_moisture": 40.0,
        "irrigation_type": "drip",
        "crop_age_days": 45,
        "plant_spacing_cm": 45,
        "yield_target_ton_acre": 20,
        "soil_PH": 6.5,
        "N_mgkg": N_mgkg,
        "P_mgkg": P_mgkg,
        "K_mgkg": K_mgkg,
    }])

    # -----------------------------
    # Preprocess input
    # -----------------------------
    X = _preprocessor.transform(input_data)

    # -----------------------------
    # Predict nutrient priorities
    # -----------------------------
    N_score = float(_priority_models["N_priority"].predict(X)[0])
    P_score = float(_priority_models["P_priority"].predict(X)[0])
    K_score = float(_priority_models["K_priority"].predict(X)[0])

    priority_scores = {
        "Nitrogen (N)": N_score,
        "Phosphorus (P)": P_score,
        "Potassium (K)": K_score,
    }

    # -----------------------------
    # Deficiency logic (IMPORTANT)
    # -----------------------------
    DEFICIENCY_THRESHOLD = 0.35

    deficient = [
        nutrient for nutrient, score in priority_scores.items()
        if score > DEFICIENCY_THRESHOLD
    ]

    deficient_sorted = sorted(
        deficient,
        key=lambda n: priority_scores[n],
        reverse=True
    )

    # -----------------------------
    # Fertilizer mapping
    # -----------------------------
    def fertilizer_map(nutrient):
        if nutrient == "Nitrogen (N)":
            return "Urea (46% N)", "Nitrogenous"
        if nutrient == "Phosphorus (P)":
            return "DAP (Di-Ammonium Phosphate)", "Phosphatic"
        if nutrient == "Potassium (K)":
            return "MOP (Muriate of Potash)", "Potassic"

    response = {
        "crop": crop,
        "stage": stage,
        "soil_nutrients": {
            "N_mgkg": N_mgkg,
            "P_mgkg": P_mgkg,
            "K_mgkg": K_mgkg,
        },
        "priority_scores": priority_scores,
    }

    # -----------------------------
    # PRIMARY fertilizer (always)
    # -----------------------------
    primary_nutrient = deficient_sorted[0]
    fert_name, fert_type = fertilizer_map(primary_nutrient)

    response["primary"] = {
        "nutrient": primary_nutrient,
        "fertilizer_type": fert_type,
        "fertilizer_name": fert_name,
        "dose_kg_acre": round(priority_scores[primary_nutrient] * 100, 2),
        "message": f"Apply {fert_name} to correct major nutrient deficiency."
    }

    # -----------------------------
    # SECONDARY fertilizer (ONLY if >1 deficiency)
    # -----------------------------
    if len(deficient_sorted) > 1:
        secondary_nutrient = deficient_sorted[1]
        fert_name, fert_type = fertilizer_map(secondary_nutrient)

        response["secondary"] = {
            "nutrient": secondary_nutrient,
            "fertilizer_type": fert_type,
            "fertilizer_name": fert_name,
            "dose_kg_acre": round(priority_scores[secondary_nutrient] * 80, 2),
            "message": f"Apply {fert_name} if required."
        }

    return response
