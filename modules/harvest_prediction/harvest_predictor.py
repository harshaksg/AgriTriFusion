# modules/harvest_prediction/harvest_predictor.py

import cv2
import numpy as np
import joblib
from datetime import datetime, timedelta
from sklearn.preprocessing import LabelEncoder

# --------------------------------------------------
# Crop-specific base harvest durations (days)
# --------------------------------------------------

BASE_HARVEST_DAYS = {
    "tomato": {
        "unripe": {"early": 3.0, "mid": 1.5, "late": 0.7},
        "semiripe": {"early": 2.5, "mid": 1.2, "late": 0.5},
        "ripe": {"early": 0.2, "mid": 0.1, "late": 0.1},
    },
    "banana": {
        "unripe": {"early": 4.0, "mid": 2.5, "late": 1.2},
        "semiripe": {"early": 3.0, "mid": 1.8, "late": 0.8},
        "ripe": {"early": 0.3, "mid": 0.2, "late": 0.2},
    },
    "mango": {
        "unripe": {"early": 5.0, "mid": 3.0, "late": 1.5},
        "semiripe": {"early": 3.5, "mid": 2.0, "late": 1.0},
        "ripe": {"early": 0.4, "mid": 0.3, "late": 0.3},
    },
    "papaya": {
        "unripe": {"early": 3.5, "mid": 2.0, "late": 1.0},
        "semiripe": {"early": 2.8, "mid": 1.5, "late": 0.6},
        "ripe": {"early": 0.3, "mid": 0.2, "late": 0.2},
    },
}

# --------------------------------------------------
# Feature Extraction
# --------------------------------------------------

def extract_visual_features(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Invalid image path")

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

    hue_mean = np.mean(hsv[:, :, 0])
    sat_mean = np.mean(hsv[:, :, 1])
    brightness_mean = np.mean(hsv[:, :, 2])
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    a_channel_mean = np.mean(lab[:, :, 1])

    return {
        "hue": hue_mean,
        "saturation": sat_mean,
        "brightness": brightness_mean,
        "laplacian": laplacian_var,
        "a_channel": a_channel_mean,
    }

# --------------------------------------------------
# Sub-Stage Classification
# --------------------------------------------------

def classify_sub_stage(features, crop, stage):
    hue = features["hue"]
    lap = features["laplacian"]
    a_ch = features["a_channel"]

    if stage == "ripe":
        return "late"

    if crop in ["tomato", "papaya"]:
        if a_ch < 135:
            return "early"
        elif a_ch < 150:
            return "mid"
        else:
            return "late"

    if crop == "banana":
        if hue > 55:
            return "early"
        elif hue > 40:
            return "mid"
        else:
            return "late"

    if crop == "mango":
        if lap > 120:
            return "early"
        elif lap > 80:
            return "mid"
        else:
            return "late"

    return "mid"

# --------------------------------------------------
# Harvest Predictor Class
# --------------------------------------------------

class HarvestPredictor:
    """
    Random Forest based harvest predictor with window estimation
    """

    def __init__(self, rf_model_path=None):
        self.crop_encoder = LabelEncoder()
        self.stage_encoder = LabelEncoder()
        self.substage_encoder = LabelEncoder()

        self.crop_encoder.fit(["tomato", "banana", "mango", "papaya"])
        self.stage_encoder.fit(["unripe", "semiripe", "ripe"])
        self.substage_encoder.fit(["early", "mid", "late"])

        if rf_model_path:
            self.rf = joblib.load(rf_model_path)
        else:
            self.rf = None  # fallback to rule-based

    # --------------------------------------------------

    def predict(self, image_path, crop, stage):
        features = extract_visual_features(image_path)
        sub_stage = classify_sub_stage(features, crop, stage)

        base_days = BASE_HARVEST_DAYS[crop][stage][sub_stage]

        # ML feature vector
        X = np.array([[
            self.crop_encoder.transform([crop])[0],
            self.stage_encoder.transform([stage])[0],
            self.substage_encoder.transform([sub_stage])[0],
            features["hue"],
            features["saturation"],
            features["brightness"],
            features["laplacian"],
        ]])

        # --------------------------------------------------
        # Random Forest Harvest Window
        # --------------------------------------------------

        if self.rf:
            tree_preds = np.array([tree.predict(X)[0] for tree in self.rf.estimators_])
            min_days = float(np.min(tree_preds))
            avg_days = float(np.mean(tree_preds))
            max_days = float(np.max(tree_preds))
        else:
            # Rule-based fallback
            min_days = base_days * 0.8
            avg_days = base_days
            max_days = base_days * 1.2

        today = datetime.now()
        return {
            "crop": crop,
            "stage": stage,
            "sub_stage": sub_stage,
            "harvest_window_days": {
                "earliest": round(min_days, 2),
                "expected": round(avg_days, 2),
                "latest": round(max_days, 2),
            },
            "harvest_window_dates": {
                "earliest": (today + timedelta(days=min_days)).strftime("%Y-%m-%d"),
                "expected": (today + timedelta(days=avg_days)).strftime("%Y-%m-%d"),
                "latest": (today + timedelta(days=max_days)).strftime("%Y-%m-%d"),
            },
        }
