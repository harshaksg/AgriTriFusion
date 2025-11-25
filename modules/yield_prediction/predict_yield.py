# modules/yield_prediction/predict_yield.py
# Stub for yield prediction. Exports predict_yield_from_fertilizer
# If you later have a trained model (models/yield_model.pkl) you can load it here.

import os

MODEL_PATH = os.path.join('models', 'yield_model.pkl')  # optional

def _mock_predict_from_fert(fert_json):
    fert = fert_json.get('fertilizer', 'NPK')
    if fert.lower() == 'urea':
        return {'yield':'8.2 tons/acre','days_left':30}
    if fert.lower() == 'npk':
        return {'yield':'9.5 tons/acre','days_left':15}
    if fert.lower() == 'mop':
        return {'yield':'10.0 tons/acre','days_left':5}
    # default
    return {'yield':'9.0 tons/acre','days_left':12}

def predict_yield_from_fertilizer(fert_json):
    """
    fert_json: {'fertilizer':'NPK','dose':'25 kg/acre','reason':'...','stage':'Semi-Ripe','crop':'Tomato'}
    returns: {'yield':'9.5 tons/acre','days_left':12}
    """
    # If you later add a real model, load and predict here.
    # Example:
    # try:
    #     import joblib
    #     model = joblib.load(MODEL_PATH)
    #     features = ... construct features ...
    #     pred = model.predict([features])
    # except Exception:
    #     return _mock_predict_from_fert(fert_json)

    return _mock_predict_from_fert(fert_json)

if __name__ == "__main__":
    print(predict_yield_from_fertilizer({'fertilizer':'NPK'}))
