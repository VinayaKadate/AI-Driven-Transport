"""
predict.py - Load trained model and predict demand for each route at a given time step.
"""

import numpy as np
import pickle
import os
from typing import Dict, List

MODEL_PATH = os.path.join(os.path.dirname(__file__), "demand_model.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "feature_meta.pkl")

WEATHER_ENCODING = {"sunny": 0, "cloudy": 1, "rainy": 2, "stormy": 3}
ROUTE_LIST = [
    "R1_Central_Airport", "R2_Hospital_Loop", "R3_University_Tech",
    "R4_Suburb_North_South", "R5_East_West_Mall", "R6_Sports_Beach",
    "R7_Industrial_Ring", "R8_Old_Town_Lakeside"
]

_model = None
_meta = None


def load_model():
    """Load model from disk (cached after first call)."""
    global _model, _meta
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. Run ml/train_model.py first."
            )
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
        with open(SCALER_PATH, "rb") as f:
            _meta = pickle.load(f)
    return _model, _meta


def predict_route_demands(
    step: int,
    routes: Dict,
    weather: str,
    active_event_stops: List[int],
    prev_demands: Dict[str, int],
) -> Dict[str, float]:
    """
    Predict demand for each route at the given time step.

    Args:
        step: Current time step (0-95)
        routes: Dict of Route objects
        weather: Current weather string
        active_event_stops: List of stop indices affected by events
        prev_demands: Dict of route_id -> demand from previous step

    Returns:
        Dict of route_id -> predicted_demand (float)
    """
    model, meta = load_model()

    hour = (step * 15) / 60.0
    weather_enc = WEATHER_ENCODING.get(weather, 0)
    is_peak = 1 if (6 <= hour < 9 or 17 <= hour < 20) else 0
    event_stop_set = set(active_event_stops)

    feature_rows = []
    for r_idx, route_id in enumerate(ROUTE_LIST):
        route = routes.get(route_id)
        if route is None:
            feature_rows.append([step, hour, r_idx, 2, weather_enc, 0, is_peak, 0, 0.5])
            continue

        is_event = 1 if any(s in event_stop_set for s in route.stop_indices) else 0
        num_buses = route.num_buses
        avg_util = route.avg_utilization
        prev_demand = prev_demands.get(route_id, 0)

        feature_rows.append([
            step, hour, r_idx, num_buses,
            weather_enc, is_event, is_peak,
            prev_demand, avg_util
        ])

    X = np.array(feature_rows)
    predictions = model.predict(X)

    return {route_id: max(0.0, float(pred))
            for route_id, pred in zip(ROUTE_LIST, predictions)}


def is_model_available() -> bool:
    """Check if trained model exists on disk."""
    return os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH)
