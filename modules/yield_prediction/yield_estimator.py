# modules/yield_prediction/yield_estimator.py

def estimate_yield(
    crop: str,
    area_hectares: float,
    number_of_plants: int,
    soil_ph: float,
    productivity_level: str
):
    """
    Independent Yield Estimation Module
    """

    # Average yield per hectare (tons)
    BASE_YIELD = {
        "tomato": 65,
        "banana": 40,
        "mango": 15,
        "papaya": 50
    }

    if crop not in BASE_YIELD:
        raise ValueError("Unsupported crop")

    base_yield = BASE_YIELD[crop]

    # Productivity factor
    productivity_factor = {
        "low": 0.7,
        "medium": 0.9,
        "high": 1.1
    }[productivity_level]

    # Soil pH factor
    if 6.0 <= soil_ph <= 7.0:
        ph_factor = 1.0
    elif 5.5 <= soil_ph <= 7.5:
        ph_factor = 0.9
    else:
        ph_factor = 0.75

    # Plant density factor
    density_factor = min(1.0, number_of_plants / (area_hectares * 10000))

    # Final yield
    yield_tons = base_yield * area_hectares * productivity_factor * ph_factor
    yield_kg = yield_tons * 1000

    return {
        "crop": crop,
        "area_hectares": area_hectares,
        "estimated_yield_kg": round(yield_kg, 2),
        "estimated_yield_tons": round(yield_tons, 2),
        "productivity_level": productivity_level,
        "soil_ph": soil_ph
    }
