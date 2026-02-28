"""
demand_generator.py
Generates passenger demand and aggregates to route level.
Compatible with current city.py structure.
"""

import numpy as np
from typing import Dict, List
from simulation.city import Stop, Route, Bus, TIME_STEPS, RANDOM_SEED

np.random.seed(RANDOM_SEED)

# Weather multipliers (must match your train_model encoding)
WEATHER_CONDITIONS = {
    "clear": 1.0,
    "cloudy": 0.95,
    "rain": 1.2,
    "heavy_rain": 1.4,
    "storm": 0.7,
}

WEATHER_SEQUENCE = list(WEATHER_CONDITIONS.keys()) * (TIME_STEPS // 5 + 1)
WEATHER_SEQUENCE = WEATHER_SEQUENCE[:TIME_STEPS]


# ----------------------------
# Time of day demand multiplier
# ----------------------------
def time_of_day_multiplier(step: int) -> float:
    hour = (step * 15) / 60

    if 0 <= hour < 6:
        return 0.1
    elif 6 <= hour < 9:
        return 1.8
    elif 9 <= hour < 12:
        return 0.9
    elif 12 <= hour < 14:
        return 1.1
    elif 14 <= hour < 17:
        return 0.85
    elif 17 <= hour < 20:
        return 1.9
    elif 20 <= hour < 22:
        return 0.7
    else:
        return 0.2


# ----------------------------
# Event simulation
# ----------------------------
EVENTS = [
    {"start": 24, "end": 32, "stops": [0, 2, 7, 16], "multiplier": 2.2},
    {"start": 44, "end": 52, "stops": [6, 5, 20], "multiplier": 3.5},
]


def event_multiplier(step: int, stop_idx: int) -> float:
    mult = 1.0
    for event in EVENTS:
        if event["start"] <= step < event["end"] and stop_idx in event["stops"]:
            mult = max(mult, event["multiplier"])
    return mult


def get_active_events(step: int):
    return [e for e in EVENTS if e["start"] <= step < e["end"]]


# ----------------------------
# Demand Generation
# ----------------------------
def generate_demand(stops: List[Stop], step: int) -> Dict[int, int]:
    weather = WEATHER_SEQUENCE[step]
    weather_mult = WEATHER_CONDITIONS[weather]
    time_mult = time_of_day_multiplier(step)

    demand_map = {}

    for stop in stops:
        evt_mult = event_multiplier(step, stop.stop_id)
        raw = stop.base_demand * time_mult * weather_mult * evt_mult
        noise = np.random.normal(0, raw * 0.1)
        demand = max(0, int(raw + noise))

        demand_map[stop.stop_id] = demand
        stop.current_waiting += demand

    return demand_map


# ----------------------------
# Route Aggregation
# ----------------------------
def generate_route_demand(routes, demand_map):
    """
    Aggregate stop-level demand to route-level demand.
    Works for routes as dict {route_id: Route}
    """
    route_demand = {}

    for route_id, route in routes.items():
        total = sum(
            demand_map.get(stop_id, 0)
            for stop_id in route.stops
        )
        route_demand[route_id] = total

    return route_demand


# ----------------------------
# Bus Simulation
# ----------------------------
def simulate_bus_service(routes, buses, stops):
    """
    Simulate buses serving passengers.
    routes: dict {route_id: Route}
    buses: list of Bus
    stops: list of Stop
    """

    for route_id, route in routes.items():

        route_buses = [b for b in buses if b.route_id == route_id]

        if not route_buses:
            continue

        total_capacity = sum(b.capacity for b in route_buses)
        total_waiting = sum(stops[s].current_waiting for s in route.stops)

        served = min(total_capacity, total_waiting)

        # distribute load evenly
        for bus in route_buses:
            share = int(served / len(route_buses))
            bus.current_load = min(bus.capacity, share)

        # reduce waiting passengers proportionally
        if total_waiting > 0:
            for stop_id in route.stops:
                stop = stops[stop_id]
                reduction = int(served * (stop.current_waiting / total_waiting))
                stop.current_waiting = max(0, stop.current_waiting - reduction)

        # simulate passengers alighting
        for bus in route_buses:
            alight = int(bus.current_load * 0.4)
            bus.current_load = max(0, bus.current_load - alight)

def step_to_time(step: int) -> str:
    """Convert simulation step (0–95) to HH:MM format."""
    minutes = step * 15
    h = minutes // 60
    m = minutes % 60
    return f"{int(h):02d}:{int(m):02d}"