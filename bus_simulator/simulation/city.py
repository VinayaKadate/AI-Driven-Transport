"""
city.py - Core city simulation: routes, stops, buses, and passenger logic.
"""
import numpy as np
from dataclasses import dataclass, field
from typing import List

RANDOM_SEED = 42
NUM_ROUTES = 8
NUM_STOPS = 40
NUM_BUSES = 20
TIME_STEPS = 96
BUS_CAPACITY = 50
MIN_BUSES_PER_ROUTE = 1

STOP_NAMES = [
    "Central Station", "City Hall", "University", "Hospital", "Airport",
    "Mall East", "Mall West", "Stadium", "Tech Park", "Old Town",
    "Harbor", "Museum", "Library", "Park North", "Park South",
    "Market Square", "Industrial Zone", "Residential A", "Residential B",
    "Residential C", "Suburb North", "Suburb South", "Suburb East",
    "Suburb West", "School District", "Business Hub", "Finance District",
    "Convention Ctr", "Sports Complex", "Night Market",
    "Hill Top", "River Crossing", "Botanical Garden", "Zoo",
    "Train Depot", "Bus Terminal", "Civic Center", "Arts District",
    "Waterfront", "Gateway Plaza",
]

@dataclass
class Stop:
    stop_id: int
    name: str
    x: float
    y: float
    base_demand: float
    current_waiting: float = 0.0

@dataclass
class Route:
    route_id: int
    name: str
    stops: List[int]
    base_frequency: int

@dataclass
class Bus:
    bus_id: int
    route_id: int
    capacity: int = BUS_CAPACITY
    current_load: int = 0
    utilization_history: List[float] = field(default_factory=list)

def build_city():
    rng = np.random.RandomState(RANDOM_SEED)
    stops = [
    Stop(
        stop_id=i,
        name=n,
        x=rng.uniform(0,1),
        y=rng.uniform(0,1),
        base_demand=rng.uniform(5, 25)  # realistic passenger base rate
    )
    for i, n in enumerate(STOP_NAMES)
]

    route_stop_map = [
        [0,1,2,3,4], [0,5,6,7,8], [9,10,11,12,13],
        [14,15,16,17,18], [19,20,21,22,23], [24,25,26,27,28],
        [29,30,31,32,33], [34,35,36,37,38],
    ]
    route_names = [
        "Airport Express","Tech Shuttle","Old Town Loop","Market Residential",
        "Suburb Ring","Civic Connector","Leisure Line","Harbor Link",
    ]
    base_alloc = [3,3,2,3,2,2,2,3]

    routes = [Route(i, route_names[i], route_stop_map[i], base_alloc[i]) for i in range(NUM_ROUTES)]
    buses, bus_id = [], 0
    for r in routes:
        for _ in range(r.base_frequency):
            buses.append(Bus(bus_id=bus_id, route_id=r.route_id))
            bus_id += 1
    return {
    "stops": stops,
    "routes": routes,
    "buses": buses
}

WEATHER_CONDITIONS = ["clear","cloudy","rain","heavy_rain","storm"]
WEATHER_MULTIPLIER = {"clear":1.0,"cloudy":1.05,"rain":1.3,"heavy_rain":1.55,"storm":1.8}

def get_weather_sequence(seed=RANDOM_SEED):
    rng = np.random.RandomState(seed)
    transition = {
        "clear":      [0.70,0.20,0.07,0.02,0.01],
        "cloudy":     [0.30,0.45,0.18,0.05,0.02],
        "rain":       [0.10,0.20,0.45,0.20,0.05],
        "heavy_rain": [0.05,0.10,0.30,0.40,0.15],
        "storm":      [0.02,0.05,0.20,0.35,0.38],
    }
    current, seq = "clear", []
    for _ in range(TIME_STEPS):
        seq.append(current)
        current = rng.choice(WEATHER_CONDITIONS, p=transition[current])
    return seq

def get_event_multipliers(seed=RANDOM_SEED):
    rng = np.random.RandomState(seed+1)
    mults = np.ones((TIME_STEPS, NUM_ROUTES))
    for _ in range(rng.randint(3,6)):
        t0 = rng.randint(20,80)
        t1 = min(t0 + rng.randint(2,6), TIME_STEPS)
        r  = rng.randint(0, NUM_ROUTES)
        mults[t0:t1, r] *= rng.uniform(1.5, 3.0)
    return mults
