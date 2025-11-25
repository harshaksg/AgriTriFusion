# modules/stage_detection/predict_stage.py
# Stub for stage detection. Returns a JSON-like dict:
# {'crop':'Tomato','stage':'Semi-Ripe','confidence':0.88}
#
# If you later add a real model file at models/ripening_model.h5,
# you can update the loader section below.

from PIL import Image
import os

MODEL_PATH = os.path.join('models', 'ripening_model.h5')  # optional

def _mock_predict(image):
    # static mock prediction
    return {'crop': 'Tomato', 'stage': 'Semi-Ripe', 'confidence': 0.88}

def predict_stage(image):
    """
    Accepts:
      - a PIL.Image.Image object OR
      - a path (string) to an image file
    Returns:
      dict with keys: 'crop', 'stage', 'confidence'
    """
    # If a path is passed, open it
    if isinstance(image, str):
        try:
            image = Image.open(image)
        except Exception:
            # fallback: return mock
            return _mock_predict(image)

    # If you later add a keras model, load & predict here:
    # Example (optional, requires tensorflow):
    # try:
    #     from tensorflow.keras.models import load_model
    #     model = load_model(MODEL_PATH)
    #     # preprocess image, predict, map classes -> stage
    # except Exception:
    #     return _mock_predict(image)

    # For now return mock
    return _mock_predict(image)

if __name__ == "__main__":
    # quick local test (make sure assets/sample_tomato.jpg exists)
    try:
        img = Image.open(os.path.join('assets', 'sample_tomato.jpg'))
        print(predict_stage(img))
    except Exception as e:
        print("Local test failed:", e)
