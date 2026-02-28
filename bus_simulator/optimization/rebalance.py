"""
rebalance.py
Simple dynamic fleet reallocation for list-based routes + buses architecture.
"""

from typing import List, Dict
import numpy as np
from simulation.city import Route, Bus, MIN_BUSES_PER_ROUTE

CAPACITY_THRESHOLD_RATIO = 0.85
MAX_REALLOCATIONS_PER_STEP = 2


def route_capacity(route: Route, buses: List[Bus]) -> int:
    return sum(b.capacity for b in buses if b.route_id == route.route_id)


def route_num_buses(route: Route, buses: List[Bus]) -> int:
    return sum(1 for b in buses if b.route_id == route.route_id)


def rebalance_fleet(
    routes: List[Route],
    buses: List[Bus],
    predicted_demands: Dict[int, float],
    reallocation_log: List[Dict],
    current_step: int,
    time_label: str,
) -> List[Route]:

    moves_made = 0

    # Compute predicted utilization for each route
    route_pressure = []

    for rid, route in routes.items():
        capacity = route_capacity(route, buses)
        pred_demand = predicted_demands.get(rid, 0)

        if capacity == 0:
            util = 1.0
        else:
            util = pred_demand / capacity

        route_pressure.append((util, rid))

    # Sort highest pressure first
    route_pressure.sort(reverse=True)

    for util, target_rid in route_pressure:

        if moves_made >= MAX_REALLOCATIONS_PER_STEP:
            break

        if util <= CAPACITY_THRESHOLD_RATIO:
            continue

        # Find donor route (lowest utilization)
        donor_candidates = []

        for route in routes:
            rid = route.route_id
            if rid == target_rid:
                continue

            num_b = route_num_buses(route, buses)
            if num_b <= MIN_BUSES_PER_ROUTE:
                continue

            capacity = route_capacity(route, buses)
            pred_demand = predicted_demands.get(rid, 0)
            donor_util = pred_demand / capacity if capacity > 0 else 1.0

            donor_candidates.append((donor_util, rid))

        if not donor_candidates:
            continue

        donor_candidates.sort()  # lowest utilization first
        donor_rid = donor_candidates[0][1]

        # Select a bus from donor
        donor_bus = next((b for b in buses if b.route_id == donor_rid), None)
        if donor_bus is None:
            continue

        # Transfer bus
        donor_bus.route_id = target_rid
        donor_bus.current_load = 0

        moves_made += 1

        reallocation_log.append({
            "time": time_label,
            "step": current_step,
            "from_route": donor_rid,
            "to_route": target_rid,
            "bus_id": donor_bus.bus_id,
            "reason": f"Predicted utilization {util:.0%} exceeded threshold"
        })

    return routes


def get_fleet_summary(routes: List[Route], buses: List[Bus]) -> Dict[int, Dict]:

    summary = {}

    for route in routes:
        rid = route.route_id
        route_buses = [b for b in buses if b.route_id == rid]

        total_capacity = sum(b.capacity for b in route_buses)
        avg_util = (
            np.mean([b.current_load / b.capacity for b in route_buses])
            if route_buses else 0
        )

        summary[rid] = {
            "num_buses": len(route_buses),
            "total_capacity": total_capacity,
            "avg_utilization": round(avg_util, 3)
        }

    return summary