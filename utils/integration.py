import os
import csv
from PIL import Image
import numpy as np

FERT_RULES_PATH = os.path.join('modules', 'fertilizer_reco', 'fertilizer_rules.csv')

def load_fertilizer_rules(path=FERT_RULES_PATH):
    """Return rules as dict[crop][stage] -> row dict"""
    if not os.path.exists(path):
        return {}
    rules = {}
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            crop = r.get('crop','Unknown').strip()
            stage = r.get('stage','Unknown').strip()
            rules.setdefault(crop, {})[stage] = r
    return rules

def preprocess_image_pil(image, size=(224,224)):
    """PIL image -> normalized numpy array"""
    image = image.convert('RGB').resize(size)
    arr = np.array(image).astype('float32') / 255.0
    return arr

# --- Mock functions expected by app.py ---
def predict_stage_mock(image):
    """Mock stage predictor — returns JSON contract used by app.py"""
    return {'crop': 'Tomato', 'stage': 'Semi-Ripe', 'confidence': 0.88}

def fertilizer_mock(stage_output, rules=None):
    """Rule-based fertilizer mock — uses rules if available"""
    crop = stage_output.get('crop','Tomato')
    stage = stage_output.get('stage','Semi-Ripe')
    if rules and crop in rules and stage in rules[crop]:
        r = rules[crop][stage]
        return {
            'fertilizer': r.get('recommended_fertilizer','NPK'),
            'dose': r.get('dose','25 kg/acre'),
            'reason': r.get('reason','Rule-based recommendation'),
            'stage': stage,
            'crop': crop
        }
    # fallback defaults
    if stage == 'Unripe':
        return {'fertilizer':'Urea','dose':'40 kg/acre','reason':'Promote vegetative growth','stage':stage,'crop':crop}
    if stage == 'Semi-Ripe':
        return {'fertilizer':'NPK','dose':'25 kg/acre','reason':'Support fruit formation','stage':stage,'crop':crop}
    return {'fertilizer':'MOP','dose':'20 kg/acre','reason':'Enhance color & firmness','stage':stage,'crop':crop}

def yield_mock(fert_output):
    """Mock yield predictor using fertilizer type"""
    fert = fert_output.get('fertilizer','NPK')
    if fert == 'Urea':
        return {'yield':'8.2 tons/acre','days_left':30}
    if fert == 'NPK':
        return {'yield':'9.5 tons/acre','days_left':15}
    if fert == 'MOP':
        return {'yield':'10.0 tons/acre','days_left':5}
    return {'yield':'9.0 tons/acre','days_left':12}
