from modules.stage_detection.abhi_predict import predict_image


def predict_stage_real(image_path: str):
    """
    Calls Abhi's deep learning model and returns crop & stage.
    """
    result = predict_image(image_path)
    return result["crop"], result["stage"]
