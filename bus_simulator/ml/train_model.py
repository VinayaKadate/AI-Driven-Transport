"""
train_model.py - Generate training data from simulation and train a RandomForest model.
Features: step, hour, route_index, num_buses, weather_encoded, is_event, prev_demand
Target: route_demand (next interval)
"""

import numpy as np
import pandas as pd
import pickle
import os
from typing import Dict
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

from simulation.city import build_city, RANDOM_SEED, TIME_STEPS
from simulation.demand_generator import (
    generate_demand,
    generate_route_demand,
    simulate_bus_service,
    get_active_events,
    WEATHER_SEQUENCE,
    EVENTS
)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "demand_model.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "feature_meta.pkl")

WEATHER_ENCODING = {
    "clear": 0,
    "cloudy": 1,
    "rain": 2,
    "heavy_rain": 3,
    "storm": 4
}


def generate_training_data(num_days: int = 30) -> pd.DataFrame:
    rows = []
    np.random.seed(RANDOM_SEED)

    for day in range(num_days):

        city = build_city()
        stops = city["stops"]
        routes = city["routes"]
        buses = city["buses"]

        prev_route_demand = {r.route_id: 0 for r in routes}

        for step in range(TIME_STEPS):

            demand_map = generate_demand(stops, step)
            route_demand = generate_route_demand(routes, demand_map)
            simulate_bus_service(routes, buses, stops)

            weather = WEATHER_SEQUENCE[step]
            weather_enc = WEATHER_ENCODING[weather]

            hour = (step * 15) / 60.0
            is_peak = 1 if (6 <= hour < 9 or 17 <= hour < 20) else 0

            for r_idx, route in enumerate(routes):

                route_id = route.route_id

                is_event = 0
                for stop_id in route.stops:
                    if any(
                        e["start"] <= step < e["end"] and stop_id in e["stops"]
                        for e in EVENTS
                    ):
                        is_event = 1
                        break

                num_buses = sum(1 for b in buses if b.route_id == route_id)

                route_buses = [b for b in buses if b.route_id == route_id]
                if route_buses:
                    utilization = np.mean(
                        [b.current_load / b.capacity for b in route_buses]
                    )
                else:
                    utilization = 0

                demand = route_demand.get(route_id, 0)

                rows.append({
                    "day": day,
                    "step": step,
                    "hour": hour,
                    "route_idx": r_idx,
                    "num_buses": num_buses,
                    "weather_enc": weather_enc,
                    "is_event": is_event,
                    "is_peak": is_peak,
                    "prev_demand": prev_route_demand[route_id],
                    "avg_utilization": utilization,
                    "demand": demand,
                })

                prev_route_demand[route_id] = demand

    df = pd.DataFrame(rows)
    print("Generated rows:", len(df))
    return df


def train_and_save_model(num_days: int = 30) -> Dict:
    """Train RandomForest on simulated data and save to disk."""
    print(f"Generating {num_days} days of training data...")
    df = generate_training_data(num_days)
    print("Dataset shape:", df.shape)

    feature_cols = [
        "step", "hour", "route_idx", "num_buses",
        "weather_enc", "is_event", "is_peak",
        "prev_demand", "avg_utilization"
    ]
    X = df[feature_cols].values
    y = df["demand"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED
    )

    print("Training RandomForest model...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=12,
        min_samples_leaf=5,
        random_state=RANDOM_SEED,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"Model trained — MAE: {mae:.2f} | R²: {r2:.4f}")

    # Save model and metadata
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    meta = {"feature_cols": feature_cols, "mae": mae, "r2": r2}
    with open(SCALER_PATH, "wb") as f:
        pickle.dump(meta, f)

    print(f"Model saved to {MODEL_PATH}")
    return {"mae": mae, "r2": r2}


if __name__ == "__main__":
    results = train_and_save_model(num_days=30)
    print(results)
