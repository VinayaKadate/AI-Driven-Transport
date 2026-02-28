"""
metrics.py - Performance metrics for baseline vs smart routing comparison.

Metrics:
  - Average wait time per passenger
  - Overcrowding ratio (buses over 80% capacity)
  - Idle bus percentage (buses under 20% utilization)
  - Passenger frustration index (composite score 0-100)
  - % improvement vs baseline
"""

import numpy as np
from typing import List, Dict


def compute_avg_wait_time(snapshots: List[Dict], routes: Dict) -> float:
    """
    Estimate average wait time in minutes.
    Formula: wait_time = (unserved_demand / route_capacity) * headway_minutes
    Headway = 60 / num_buses (minutes between buses on a route)
    """
    wait_times = []
    for snap in snapshots:
        for route_id, demand in snap["route_demand"].items():
            capacity = snap["route_capacity"].get(route_id, 1)
            num_buses = snap["route_num_buses"].get(route_id, 1)
            if num_buses == 0:
                num_buses = 1
            headway = 60.0 / num_buses  # minutes between buses
            unserved_ratio = max(0, (demand - capacity) / max(demand, 1))
            wait = headway * (1 + unserved_ratio)  # base wait + overflow penalty
            wait_times.append(wait)
    return float(np.mean(wait_times)) if wait_times else 0.0


def compute_overcrowding_ratio(snapshots: List[Dict]) -> float:
    """
    Overcrowding ratio = fraction of (route, time) pairs where utilization > 80%.
    Formula: overcrowding_ratio = count(util > 0.8) / total_observations
    """
    total = 0
    overcrowded = 0
    for snap in snapshots:
        for route_id, util in snap["route_utilization"].items():
            total += 1
            if util > 0.8:
                overcrowded += 1
    return overcrowded / max(total, 1)


def compute_idle_bus_percentage(snapshots: List[Dict]) -> float:
    """
    Idle bus % = fraction of (route, time) pairs where utilization < 20%.
    Formula: idle_pct = count(util < 0.2) / total_observations
    """
    total = 0
    idle = 0
    for snap in snapshots:
        for route_id, util in snap["route_utilization"].items():
            total += 1
            if util < 0.2:
                idle += 1
    return (idle / max(total, 1)) * 100.0


def compute_frustration_index(avg_wait: float, overcrowding: float, idle_pct: float) -> float:
    """
    Passenger Frustration Index (0-100 scale, lower is better).
    Formula:
      frustration = 0.4 * normalized_wait + 0.4 * overcrowding_penalty + 0.2 * idle_penalty
    Where:
      normalized_wait       = min(avg_wait / 30, 1) * 100   [30 min = max tolerable wait]
      overcrowding_penalty  = overcrowding_ratio * 100
      idle_penalty          = idle_pct  (already 0-100)
    """
    normalized_wait = min(avg_wait / 30.0, 1.0) * 100.0
    overcrowding_penalty = overcrowding * 100.0
    idle_penalty = idle_pct

    frustration = (0.4 * normalized_wait) + (0.4 * overcrowding_penalty) + (0.2 * idle_penalty)
    return round(min(frustration, 100.0), 2)


def compute_unserved_passengers(snapshots: List[Dict]) -> int:
    """Total passengers who couldn't board due to overcapacity."""
    total_unserved = 0
    for snap in snapshots:
        for route_id, demand in snap["route_demand"].items():
            capacity = snap["route_capacity"].get(route_id, 0)
            total_unserved += max(0, demand - capacity)
    return total_unserved


def compute_all_metrics(snapshots, routes, label=""):

    avg_wait = compute_avg_wait_time(snapshots, routes)
    overcrowding = compute_overcrowding_ratio(snapshots)
    idle_pct = compute_idle_bus_percentage(snapshots)
    total_unserved = compute_unserved_passengers(snapshots)

    frustration = compute_frustration_index(
        avg_wait,
        overcrowding,
        idle_pct
    )

    return {
    "label": label,
    "avg_wait_time_min": round(avg_wait, 2),
    "overcrowding_pct": round(overcrowding * 100, 2),  # convert to percent
    "idle_bus_pct": round(idle_pct, 2),
    "frustration_index": frustration,
    "total_unserved_passengers": int(total_unserved),
}


def compute_improvement(baseline: Dict, smart: Dict) -> Dict:
    """
    Compute percentage improvement of smart vs baseline.
    Improvement = (baseline - smart) / baseline * 100 (positive = better)
    """
    def pct_improve(b, s):
        if b == 0:
            return 0.0
        return round((b - s) / b * 100, 2)

    return {
        "wait_time_improvement_pct":     pct_improve(baseline["avg_wait_time_min"],      smart["avg_wait_time_min"]),
        "overcrowding_improvement_pct":  pct_improve(baseline["overcrowding_pct"], smart["overcrowding_pct"]),
        "idle_improvement_pct":          pct_improve(baseline["idle_bus_pct"],            smart["idle_bus_pct"]),
        "frustration_improvement_pct":   pct_improve(baseline["frustration_index"],      smart["frustration_index"]),
        "unserved_improvement_pct":      pct_improve(baseline["total_unserved_passengers"], smart["total_unserved_passengers"]),
    }


def compute_per_step_metrics(snapshots: List[Dict]) -> List[Dict]:
    """Compute per-time-step aggregated metrics for time-series plotting."""
    results = []
    for snap in snapshots:
        utils = list(snap["route_utilization"].values())
        demands = list(snap["route_demand"].values())
        capacities = list(snap["route_capacity"].values())

        avg_util = np.mean(utils) if utils else 0
        overcrowded_routes = sum(1 for u in utils if u > 0.8)
        total_demand = sum(demands)
        total_cap = sum(capacities)

        results.append({
            "step": snap["step"],
            "time_label": snap["time_label"],
            "avg_utilization": round(avg_util, 3),
            "overcrowded_routes": overcrowded_routes,
            "total_demand": total_demand,
            "total_capacity": total_cap,
            "weather": snap["weather"],
            "events": ", ".join(snap["active_events"]) if snap["active_events"] else "—",
        })
    return results
