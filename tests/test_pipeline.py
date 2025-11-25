# tests/test_pipeline.py
from modules.stage_detection.predict_stage import predict_stage
from modules.fertilizer_reco.fert_reco import recommend_fertilizer
from modules.yield_prediction.predict_yield import predict_yield_from_fertilizer

def test_end_to_end_mock():
    s = predict_stage(None)  # mock
    assert 'stage' in s and 'crop' in s
    f = recommend_fertilizer(s)
    assert 'fertilizer' in f and 'dose' in f
    y = predict_yield_from_fertilizer(f)
    assert 'yield' in y and 'days_left' in y
