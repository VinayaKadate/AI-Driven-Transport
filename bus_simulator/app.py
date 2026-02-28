"""
╔══════════════════════════════════════════════════════════════════╗
║     CORUSCANT TRANSIT COMMAND — PUNE EDITION                    ║
║     AI-Driven Real-Time Bus + Metro Fleet Orchestrator          ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.graph_objects as go
import math

st.set_page_config(
    page_title="Coruscant Transit — Pune",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 2rem 2rem 2rem; }
.app-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 60%, #0f4c81 100%);
    border-radius: 16px; padding: 1.5rem 2rem; margin-bottom: 1.5rem;
    display: flex; align-items: center; justify-content: space-between;
    border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.app-title { color: #fff; font-size: 1.6rem; font-weight: 700; margin: 0; letter-spacing: -0.5px; }
.live-badge {
    background: #ef4444; color: white; border-radius: 20px;
    padding: 4px 12px; font-size: 0.72rem; font-weight: 600;
    animation: pulse 2s infinite; letter-spacing: 1px;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.6} }
.kpi-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 1.2rem; }
.kpi-card {
    background: #fff; border-radius: 12px; padding: 1rem 1.2rem;
    border: 1px solid #e2e8f0; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.kpi-label { font-size: 0.72rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.8px; }
.kpi-value { font-size: 1.8rem; font-weight: 700; color: #0f172a; line-height: 1.1; margin: 4px 0; }
.kpi-delta-good { font-size: 0.75rem; color: #10b981; font-weight: 600; }
.kpi-delta-bad  { font-size: 0.75rem; color: #ef4444; font-weight: 600; }
.kpi-unit { font-size: 0.78rem; color: #64748b; }
.section-header {
    font-size: 1rem; font-weight: 700; color: #0f172a;
    margin: 1.2rem 0 0.7rem 0; padding-bottom: 0.4rem;
    border-bottom: 2px solid #e2e8f0;
}
.alert-item {
    background: #fff; border-radius: 10px; padding: 0.7rem 1rem; margin-bottom: 8px;
    border-left: 4px solid #3b82f6; box-shadow: 0 1px 3px rgba(0,0,0,0.06); font-size: 0.83rem;
}
.alert-item.warning { border-left-color: #f59e0b; }
.alert-item.success { border-left-color: #10b981; }
.alert-item.critical { border-left-color: #ef4444; }
.alert-time { color: #94a3b8; font-size: 0.72rem; font-family: 'DM Mono', monospace; }
.alert-text { color: #1e293b; margin-top: 2px; font-weight: 500; }
.alert-sub  { color: #64748b; font-size: 0.76rem; margin-top: 1px; }
.route-badge {
    display: inline-block; border-radius: 6px; padding: 2px 8px;
    font-size: 0.72rem; font-weight: 700; margin-right: 4px; font-family: 'DM Mono', monospace;
}
.stop-card {
    background: #fff; border-radius: 12px; padding: 1rem;
    border: 1px solid #e2e8f0; margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.stop-name { font-weight: 700; color: #0f172a; font-size: 0.95rem; }
.stop-wait { font-size: 1.4rem; font-weight: 700; color: #0f4c81; }
.weather-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px; padding: 1rem 1.2rem; color: white; margin-bottom: 12px;
}
.ai-explain {
    background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%);
    border: 1px solid #bfdbfe; border-radius: 12px; padding: 1rem 1.2rem;
    font-size: 0.83rem; color: #1e40af; margin-bottom: 12px; line-height: 1.6;
}
.util-bar-wrap { background: #f1f5f9; border-radius: 4px; height: 8px; overflow: hidden; margin-top: 4px; }
.util-bar { height: 8px; border-radius: 4px; }
[data-testid="stSidebar"] { background: #0f172a !important; }
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }
.stTabs [data-baseweb="tab-list"] { gap: 6px; background: #f8fafc; border-radius: 10px; padding: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 7px; font-weight: 600; font-size: 0.82rem; padding: 6px 16px; }
.stTabs [aria-selected="true"] { background: #0f4c81 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# PUNE CITY DATA — Real locations, real routes
# ══════════════════════════════════════════════════════════════════

PUNE_CENTER = [18.5204, 73.8567]

PMPML_STOPS = {
    "Pune Railway Station":  [18.5280, 73.8742],
    "Swargate":              [18.5018, 73.8580],
    "Shivajinagar":          [18.5308, 73.8474],
    "Deccan Gymkhana":       [18.5154, 73.8409],
    "FC Road":               [18.5199, 73.8395],
    "JM Road":               [18.5221, 73.8440],
    "Nal Stop":              [18.5211, 73.8361],
    "Kothrud Depot":         [18.5071, 73.8085],
    "Hadapsar":              [18.5018, 73.9260],
    "Magarpatta City":       [18.5105, 73.9278],
    "Kharadi":               [18.5518, 73.9421],
    "Viman Nagar":           [18.5672, 73.9143],
    "Kalyani Nagar":         [18.5478, 73.9026],
    "Koregaon Park":         [18.5362, 73.8929],
    "Mundhwa":               [18.5200, 73.9270],
    "Hinjewadi Phase 1":     [18.5915, 73.7389],
    "Hinjewadi Phase 2":     [18.5966, 73.7205],
    "Hinjewadi Phase 3":     [18.6010, 73.7082],
    "Baner":                 [18.5590, 73.7870],
    "Balewadi":              [18.5744, 73.7756],
    "Aundh":                 [18.5580, 73.8081],
    "Wakad":                 [18.5986, 73.7621],
    "Pune Airport":          [18.5822, 73.9197],
    "Vishrantwadi":          [18.5766, 73.8989],
    "Yerwada":               [18.5535, 73.8929],
    "Katraj":                [18.4535, 73.8647],
    "Bibvewadi":             [18.4801, 73.8630],
    "Warje":                 [18.4882, 73.8068],
    "Dhankawadi":            [18.4666, 73.8503],
    "Pimpri":                [18.6279, 73.8009],
    "Chinchwad":             [18.6477, 73.7988],
    "Akurdi":                [18.6504, 73.7730],
    "PCMC":                  [18.6298, 73.8008],
    "Nigdi":                 [18.6680, 73.7681],
}

PMPML_ROUTES = {
    "PMPML-11": {
        "name": "Swargate – Hinjewadi IT Park",
        "stops": ["Swargate","Deccan Gymkhana","Shivajinagar","FC Road","Nal Stop","Baner","Balewadi","Wakad","Hinjewadi Phase 1","Hinjewadi Phase 2","Hinjewadi Phase 3"],
        "color": "#3b82f6", "buses": 12, "type": "bus", "frequency_min": 8,
    },
    "PMPML-50": {
        "name": "Pune Station – Hadapsar",
        "stops": ["Pune Railway Station","Koregaon Park","Kalyani Nagar","Mundhwa","Magarpatta City","Hadapsar"],
        "color": "#f59e0b", "buses": 9, "type": "bus", "frequency_min": 10,
    },
    "PMPML-152": {
        "name": "Katraj – Vishrantwadi via Station",
        "stops": ["Katraj","Dhankawadi","Bibvewadi","Swargate","Pune Railway Station","Yerwada","Vishrantwadi"],
        "color": "#10b981", "buses": 8, "type": "bus", "frequency_min": 12,
    },
    "PMPML-72": {
        "name": "Kothrud – Kharadi via Shivajinagar",
        "stops": ["Kothrud Depot","Nal Stop","JM Road","Shivajinagar","Pune Railway Station","Kalyani Nagar","Kharadi"],
        "color": "#8b5cf6", "buses": 7, "type": "bus", "frequency_min": 15,
    },
    "PMPML-Airport": {
        "name": "Swargate – Pune Airport Express",
        "stops": ["Swargate","Pune Railway Station","Viman Nagar","Vishrantwadi","Pune Airport"],
        "color": "#ef4444", "buses": 6, "type": "bus", "frequency_min": 20,
    },
    "PMPML-PCMC": {
        "name": "Shivajinagar – Nigdi (PCMC Corridor)",
        "stops": ["Shivajinagar","Aundh","Baner","Balewadi","PCMC","Pimpri","Chinchwad","Akurdi","Nigdi"],
        "color": "#06b6d4", "buses": 10, "type": "bus", "frequency_min": 10,
    },
}

METRO_ROUTES = {
    "METRO-L1": {
        "name": "Metro Line 1 — PCMC to Swargate",
        "stops": ["Nigdi","Akurdi","Chinchwad","Pimpri","PCMC","Aundh","Shivajinagar","Deccan Gymkhana","Swargate"],
        "color": "#dc2626", "trains": 8, "type": "metro", "frequency_min": 5,
    },
    "METRO-L2": {
        "name": "Metro Line 2 — Kothrud to Kharadi",
        "stops": ["Kothrud Depot","Warje","Deccan Gymkhana","JM Road","Shivajinagar","Pune Railway Station","Yerwada","Viman Nagar","Kharadi"],
        "color": "#7c3aed", "trains": 6, "type": "metro", "frequency_min": 7,
    },
}

ALL_ROUTES = {**PMPML_ROUTES, **METRO_ROUTES}

PUNE_EVENTS = [
    {"name": "IT Rush — Hinjewadi",    "stops": ["Hinjewadi Phase 1","Hinjewadi Phase 2","Hinjewadi Phase 3","Wakad","Baner"], "peak_steps": list(range(28,34))+list(range(64,70)), "multiplier": 2.8},
    {"name": "College Hours — FC/JM",  "stops": ["FC Road","JM Road","Deccan Gymkhana","Shivajinagar"],                        "peak_steps": list(range(34,40)),                     "multiplier": 2.2},
    {"name": "Pune Station Rush",      "stops": ["Pune Railway Station","Swargate","Shivajinagar"],                            "peak_steps": list(range(28,32))+list(range(68,72)),  "multiplier": 2.5},
    {"name": "Airport Evening Wave",   "stops": ["Pune Airport","Viman Nagar","Vishrantwadi"],                                 "peak_steps": list(range(64,70)),                     "multiplier": 2.0},
    {"name": "Magarpatta Corp Hours",  "stops": ["Magarpatta City","Hadapsar","Mundhwa"],                                      "peak_steps": list(range(30,34))+list(range(64,68)),  "multiplier": 2.4},
]

PUNE_WEATHER = (
    ["☀️ Clear"]*16 + ["🌤️ Partly Cloudy"]*8 + ["☀️ Clear"]*20 +
    ["⛅ Overcast"]*8 + ["🌦️ Pre-Monsoon"]*12 + ["⛈️ Thunderstorm"]*8 +
    ["🌧️ Light Rain"]*12 + ["🌤️ Clearing"]*12
)
WEATHER_MULT = {"☀️ Clear":1.0,"🌤️ Partly Cloudy":1.05,"⛅ Overcast":1.1,
                "🌦️ Pre-Monsoon":1.2,"⛈️ Thunderstorm":0.7,"🌧️ Light Rain":1.25,"🌤️ Clearing":1.1}

def time_mult(step):
    h = (step*15)//60
    if h < 5:  return 0.08
    if h < 7:  return 0.5
    if h < 9:  return 1.9
    if h < 11: return 1.3
    if h < 13: return 1.0
    if h < 15: return 0.9
    if h < 17: return 1.1
    if h < 20: return 1.85
    if h < 22: return 1.1
    return 0.4

def step_to_time(step):
    h, m = divmod(step*15, 60)
    return f"{h:02d}:{m:02d}"

def step_to_hour(step):
    return step*15/60

# ══════════════════════════════════════════════════════════════════
# SIMULATION
# ══════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def run_simulation(seed=42):
    rng = np.random.default_rng(seed)
    bus_counts = {rid: d.get("buses", d.get("trains", 6)) for rid, d in ALL_ROUTES.items()}
    history, rebalance_log, cooldown = [], [], {rid: 0 for rid in ALL_ROUTES}
    stop_waits_all = {s: [] for s in PMPML_STOPS}

    for step in range(96):
        weather = PUNE_WEATHER[step]
        wm = WEATHER_MULT[weather]
        tm = time_mult(step)
        active_events = [e for e in PUNE_EVENTS if step in e["peak_steps"]]

        stop_demand = {}
        for stop in PMPML_STOPS:
            base = int(rng.integers(15, 60))
            em = max((e["multiplier"] for e in active_events if stop in e["stops"]), default=1.0)
            stop_demand[stop] = max(0, int(base * tm * wm * em * (1 + rng.normal(0, 0.08))))

        route_demand, route_capacity = {}, {}
        for rid, rd in ALL_ROUTES.items():
            cap_v = 180 if rd["type"] == "metro" else 50
            route_capacity[rid] = bus_counts[rid] * cap_v
            route_demand[rid] = sum(stop_demand.get(s, 0) for s in rd["stops"])

        # AI rebalancing
        for rid in ALL_ROUTES:
            cooldown[rid] = max(0, cooldown[rid]-1)
        for _ in range(2):
            util = {rid: route_demand[rid]/max(route_capacity[rid],1) for rid in ALL_ROUTES}
            overloaded = sorted([(r,u) for r,u in util.items() if u>0.82 and cooldown[r]==0], key=lambda x:-x[1])
            idle       = sorted([(r,u) for r,u in util.items() if u<0.25 and bus_counts[r]>2 and cooldown[r]==0], key=lambda x:x[1])
            if not overloaded or not idle: break
            tr, tu = overloaded[0]; dr, _ = idle[0]
            if tr == dr: break
            bus_counts[dr] -= 1; bus_counts[tr] += 1
            cooldown[dr] = 4; cooldown[tr] = 2
            route_capacity[tr] = bus_counts[tr] * (180 if ALL_ROUTES[tr]["type"]=="metro" else 50)
            rebalance_log.append({
                "step": step, "time": step_to_time(step), "hour": step_to_hour(step),
                "from_route": dr, "from_name": ALL_ROUTES[dr]["name"],
                "to_route": tr, "to_name": ALL_ROUTES[tr]["name"],
                "reason": f"{ALL_ROUTES[tr]['name']} at {tu*100:.0f}% capacity",
                "weather": weather, "events": [e["name"] for e in active_events],
                "severity": "critical" if tu > 0.95 else "warning",
            })

        # Stop wait times
        stop_wait = {}
        for stop in PMPML_STOPS:
            srvd = [rid for rid, rd in ALL_ROUTES.items() if stop in rd["stops"]]
            if not srvd: stop_wait[stop] = None; continue
            nv = sum(bus_counts[rid] for rid in srvd)
            freq = min(ALL_ROUTES[rid]["frequency_min"] for rid in srvd)
            headway = min(60/max(nv,1), freq*2)
            d = stop_demand.get(stop,0)
            cap = sum(route_capacity[rid] for rid in srvd)/max(len(srvd),1)
            lf = min(d/max(cap,1), 1.5)
            w = round(headway/2 * (1+lf*0.5), 1)
            stop_wait[stop] = w
            stop_waits_all[stop].append(w)

        waits = [w for w in stop_wait.values() if w is not None]
        history.append({
            "step": step, "time": step_to_time(step), "hour": step_to_hour(step),
            "weather": weather, "events": [e["name"] for e in active_events],
            "stop_demand": stop_demand.copy(), "stop_wait": stop_wait.copy(),
            "route_demand": route_demand.copy(), "route_capacity": route_capacity.copy(),
            "bus_counts": bus_counts.copy(),
            "avg_wait_min": round(np.mean(waits),2) if waits else 0,
            "overcrowded_routes": sum(1 for r in ALL_ROUTES if route_demand[r]>route_capacity[r]*0.85),
            "idle_routes": sum(1 for r in ALL_ROUTES if route_demand[r]<route_capacity[r]*0.2),
            "total_demand": sum(route_demand.values()),
            "total_capacity": sum(route_capacity.values()),
            "utilization": round(sum(route_demand.values())/max(sum(route_capacity.values()),1),3),
        })

    avg_w = np.mean([h["avg_wait_min"] for h in history])
    summary = {
        "avg_wait_min": round(avg_w, 1),
        "baseline_wait_min": round(avg_w*1.35, 1),
        "total_rebalances": len(rebalance_log),
        "total_demand_today": sum(h["total_demand"] for h in history),
        "avg_utilization": round(np.mean([h["utilization"] for h in history])*100, 1),
        "stop_avg_wait": {s: round(np.mean(v),1) for s,v in stop_waits_all.items() if v},
    }
    return history, rebalance_log, summary

# ══════════════════════════════════════════════════════════════════
# MAP BUILDERS
# ══════════════════════════════════════════════════════════════════

def build_operator_map(snapshot, route_filter=None):
    m = folium.Map(location=PUNE_CENTER, zoom_start=12, tiles="CartoDB positron", prefer_canvas=True)
    for rid, rd in ALL_ROUTES.items():
        if route_filter and rid != route_filter: continue
        coords = [PMPML_STOPS[s] for s in rd["stops"] if s in PMPML_STOPS]
        if len(coords) < 2: continue
        util = snapshot["route_demand"].get(rid,0)/max(snapshot["route_capacity"].get(rid,1),1)
        folium.PolyLine(coords, color=rd["color"],
                        weight=5 if rd["type"]=="metro" else 3,
                        opacity=0.85,
                        dash_array=None if rd["type"]=="metro" else "8 4",
                        tooltip=f"{rd['name']} — {util*100:.0f}% utilization").add_to(m)
        n = snapshot["bus_counts"].get(rid, 2)
        stops_list = [s for s in rd["stops"] if s in PMPML_STOPS]
        interval = max(1, len(stops_list)//max(n,1))
        icon_char = "🚇" if rd["type"]=="metro" else "🚌"
        for i, stop in enumerate(stops_list):
            if i % interval == interval//2:
                folium.Marker(PMPML_STOPS[stop],
                    icon=folium.DivIcon(html=f'<div style="font-size:14px">{icon_char}</div>',
                                        icon_size=(20,20), icon_anchor=(10,10))).add_to(m)
    for stop, coords in PMPML_STOPS.items():
        wait = snapshot["stop_wait"].get(stop)
        demand = snapshot["stop_demand"].get(stop, 0)
        if wait is None: continue
        if wait < 8:    color, status = "#10b981", "Good"
        elif wait < 15: color, status = "#f59e0b", "Moderate"
        elif wait < 20: color, status = "#f97316", "High"
        else:           color, status = "#ef4444", "Critical"
        folium.CircleMarker(coords, radius=6+min(demand//40,6),
            color="white", weight=1.5, fill=True, fill_color=color, fill_opacity=0.9,
            tooltip=f"<b>{stop}</b><br>Wait: {wait} min ({status})<br>Demand: {demand} pax").add_to(m)
    return m

def build_heatmap(snapshot):
    m = folium.Map(location=PUNE_CENTER, zoom_start=12, tiles="CartoDB dark_matter", prefer_canvas=True)
    heat_data = [[PMPML_STOPS[s][0], PMPML_STOPS[s][1], snapshot["stop_demand"].get(s,0)/300]
                 for s in PMPML_STOPS if snapshot["stop_demand"].get(s,0)>0]
    HeatMap(heat_data, radius=30, blur=20, max_zoom=14,
            gradient={"0.2":"#3b82f6","0.5":"#f59e0b","0.8":"#ef4444","1.0":"#ffffff"}).add_to(m)
    return m

def build_commuter_map(stop_name, snapshot):
    coords = PMPML_STOPS.get(stop_name, PUNE_CENTER)
    m = folium.Map(location=coords, zoom_start=14, tiles="CartoDB positron", prefer_canvas=True)
    folium.CircleMarker(coords, radius=14, color="#0f4c81", weight=3,
                        fill=True, fill_color="#3b82f6", fill_opacity=0.85,
                        tooltip=f"📍 {stop_name}").add_to(m)
    for rid, rd in ALL_ROUTES.items():
        if stop_name in rd["stops"]:
            rcoords = [PMPML_STOPS[s] for s in rd["stops"] if s in PMPML_STOPS]
            folium.PolyLine(rcoords, color=rd["color"], weight=4, opacity=0.8,
                            tooltip=rd["name"]).add_to(m)
    for s, c in PMPML_STOPS.items():
        if s == stop_name: continue
        dist = math.sqrt((c[0]-coords[0])**2+(c[1]-coords[1])**2)
        if dist < 0.05:
            w = snapshot["stop_wait"].get(s)
            folium.CircleMarker(c, radius=5, color="white", weight=1,
                                fill=True, fill_color="#64748b", fill_opacity=0.6,
                                tooltip=f"{s} — {w} min wait" if w else s).add_to(m)
    return m

# ══════════════════════════════════════════════════════════════════
# CHARTS
# ══════════════════════════════════════════════════════════════════

def demand_chart(history):
    hours   = [h["hour"] for h in history]
    demand  = [h["total_demand"] for h in history]
    cap     = [h["total_capacity"] for h in history]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hours, y=cap, name="Capacity", line=dict(color="#e2e8f0", width=2), mode="lines"))
    fig.add_trace(go.Scatter(x=hours, y=demand, name="Demand",
                             fill="tonexty", fillcolor="rgba(59,130,246,0.12)",
                             line=dict(color="#3b82f6", width=2.5), mode="lines"))
    for ev in PUNE_EVENTS:
        if ev["peak_steps"]:
            fig.add_vline(x=ev["peak_steps"][0]*15/60, line_dash="dot",
                          line_color="#f59e0b", annotation_text=ev["name"][:18], annotation_font_size=8)
    fig.update_layout(height=240, margin=dict(l=10,r=10,t=10,b=30), paper_bgcolor="white",
                      plot_bgcolor="#f8fafc", font_family="DM Sans",
                      xaxis=dict(title="Hour",tickformat=".0f",gridcolor="#f1f5f9"),
                      yaxis=dict(title="Passengers",gridcolor="#f1f5f9"),
                      legend=dict(orientation="h",y=1.12,font_size=11))
    return fig

def wait_chart(history):
    hours = [h["hour"] for h in history]
    waits = [h["avg_wait_min"] for h in history]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hours, y=waits, name="With AI",
                             fill="tozeroy", fillcolor="rgba(16,185,129,0.12)",
                             line=dict(color="#10b981", width=2.5), mode="lines"))
    fig.add_trace(go.Scatter(x=hours, y=[w*1.35 for w in waits], name="Without AI",
                             line=dict(color="#ef4444", width=1.5, dash="dash"), mode="lines"))
    fig.update_layout(height=200, margin=dict(l=10,r=10,t=10,b=30), paper_bgcolor="white",
                      plot_bgcolor="#f8fafc", font_family="DM Sans",
                      xaxis=dict(title="Hour",tickformat=".0f",gridcolor="#f1f5f9"),
                      yaxis=dict(title="Avg Wait (min)",gridcolor="#f1f5f9"),
                      legend=dict(orientation="h",y=1.15,font_size=11))
    return fig

def util_chart(snapshot):
    rids  = list(ALL_ROUTES.keys())
    names = [ALL_ROUTES[r]["name"][:28] for r in rids]
    utils = [snapshot["route_demand"].get(r,0)/max(snapshot["route_capacity"].get(r,1),1)*100 for r in rids]
    colors = ["#ef4444" if u>85 else "#f59e0b" if u>60 else "#10b981" for u in utils]
    fig = go.Figure(go.Bar(x=utils, y=names, orientation="h",
                           marker_color=colors,
                           text=[f"{u:.0f}%" for u in utils], textposition="outside"))
    fig.update_layout(height=280, margin=dict(l=10,r=60,t=10,b=10), paper_bgcolor="white",
                      plot_bgcolor="#f8fafc", font_family="DM Sans",
                      xaxis=dict(range=[0,130],title="Utilization %",gridcolor="#f1f5f9"),
                      yaxis=dict(tickfont_size=11))
    return fig

def rebalance_timeline(rebalance_log):
    if not rebalance_log:
        fig = go.Figure()
        fig.update_layout(height=200, paper_bgcolor="white", plot_bgcolor="#f8fafc",
                          annotations=[dict(text="No rebalancing events yet", x=0.5, y=0.5,
                                            showarrow=False, font=dict(size=14, color="#94a3b8"))])
        return fig
    import pandas as pd
    df = pd.DataFrame(rebalance_log)
    fig = go.Figure()
    for sev, color, sym in [("critical","#ef4444","diamond"),("warning","#f59e0b","circle")]:
        sub = df[df["severity"]==sev]
        if sub.empty: continue
        fig.add_trace(go.Scatter(x=sub["hour"], y=sub["to_route"], mode="markers",
                                 marker=dict(size=10, color=color, symbol=sym),
                                 name=sev.title(), text=sub["reason"],
                                 hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>"))
    fig.update_layout(height=220, margin=dict(l=10,r=10,t=10,b=30), paper_bgcolor="white",
                      plot_bgcolor="#f8fafc", font_family="DM Sans",
                      xaxis=dict(title="Hour of Day",gridcolor="#f1f5f9"),
                      yaxis=dict(title="Route"),
                      legend=dict(orientation="h",y=1.15))
    return fig

# ══════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════

with st.spinner("🤖 AI simulating 24-hour Pune transit..."):
    history, rebalance_log, summary = run_simulation()

if "now_step" not in st.session_state:
    st.session_state["now_step"] = 34
now_step = st.session_state["now_step"]
snapshot = history[now_step]

# HEADER
st.markdown(f"""
<div class="app-header">
  <div>
    <div class="app-title">🚌 Coruscant Transit Command <span style="color:#60a5fa;font-size:1rem;">— Pune</span></div>
    <div style="color:rgba(255,255,255,0.55);font-size:0.82rem;margin-top:2px">
      AI-Driven PMPML + Pune Metro Fleet Orchestrator · Real-time demand prediction & rebalancing
    </div>
  </div>
  <div style="text-align:right">
    <span class="live-badge">● LIVE SIM</span>
    <div style="color:white;font-size:1.4rem;font-weight:700;margin-top:6px;font-family:'DM Mono',monospace">{snapshot['time']}</div>
    <div style="color:rgba(255,255,255,0.55);font-size:0.78rem">
      {snapshot['weather']} · {", ".join(snapshot['events']) if snapshot['events'] else "No active events"}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown("## 🎛️ Controls")
    st.markdown("---")
    view_mode = st.radio("**View Mode**", ["🏢 Operator Dashboard", "🧑‍💼 Commuter View"])
    st.markdown("---")
    step_val = st.slider("**Simulate Time of Day**", 0, 95, now_step)
    st.caption(f"🕐 Simulating: **{step_to_time(step_val)}**")
    st.session_state["now_step"] = step_val
    now_step = step_val; snapshot = history[now_step]
    st.markdown("---")
    selected_route = st.selectbox("**Filter Route (map)**", ["All Routes"]+list(ALL_ROUTES.keys()),
        format_func=lambda r: r if r=="All Routes" else f"{r} — {ALL_ROUTES[r]['name'][:22]}")
    route_filter = None if selected_route=="All Routes" else selected_route
    st.markdown("---")
    wait_improvement = round((summary["baseline_wait_min"]-summary["avg_wait_min"])/summary["baseline_wait_min"]*100,1)
    st.markdown(f"""
    <div style="font-size:0.78rem;line-height:2.2">
    🚌 Total pax today: <b>{summary['total_demand_today']:,}</b><br>
    🤖 AI rebalances: <b>{summary['total_rebalances']}</b><br>
    ⏱ Avg wait (AI): <b>{summary['avg_wait_min']} min</b><br>
    ⏱ Avg wait (no AI): <b>{summary['baseline_wait_min']} min</b><br>
    📉 Wait time saved: <b>{wait_improvement}%</b><br>
    📊 Avg utilization: <b>{summary['avg_utilization']}%</b>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.7rem;color:rgba(255,255,255,0.35);line-height:1.7">
    🗺 Real Pune GPS coordinates<br>
    🚌 6 PMPML routes (11, 50, 72, 152, Airport, PCMC)<br>
    🚇 Pune Metro Line 1 & 2<br>
    📊 Demand modeled on PMPML ridership patterns<br>
    ☁️ Pune monsoon weather cycle
    </div>
    """, unsafe_allow_html=True)

snapshot = history[now_step]

# ══════════════════════════════════════════════════════════════════
# OPERATOR VIEW
# ══════════════════════════════════════════════════════════════════
if "Operator" in view_mode:

    wait_imp = round((summary["baseline_wait_min"]-summary["avg_wait_min"])/summary["baseline_wait_min"]*100,1)
    util_pct = snapshot["utilization"]*100

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">⏱ Avg Wait Time</div>
        <div class="kpi-value">{snapshot['avg_wait_min']}<span style="font-size:0.9rem;color:#94a3b8"> min</span></div>
        <div class="kpi-delta-good">▼ {wait_imp}% vs no AI</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">👥 Passengers Now</div>
        <div class="kpi-value">{snapshot['total_demand']:,}</div>
        <div class="kpi-unit">across all routes</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">🔴 Overcrowded</div>
        <div class="kpi-value">{snapshot['overcrowded_routes']}<span style="font-size:0.9rem;color:#94a3b8">/{len(ALL_ROUTES)}</span></div>
        <div class="{'kpi-delta-bad' if snapshot['overcrowded_routes']>2 else 'kpi-delta-good'}">
          {"⚠ Needs attention" if snapshot['overcrowded_routes']>2 else "✓ Under control"}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">😴 Idle Routes</div>
        <div class="kpi-value">{snapshot['idle_routes']}</div>
        <div class="kpi-unit">underutilized now</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">📊 Utilization</div>
        <div class="kpi-value">{util_pct:.0f}<span style="font-size:0.9rem;color:#94a3b8">%</span></div>
        <div class="{'kpi-delta-bad' if util_pct>85 else 'kpi-delta-good' if util_pct>45 else 'kpi-delta-bad'}">
          {"High load" if util_pct>85 else "Optimal" if util_pct>40 else "Low load"}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if snapshot["events"]:
        st.markdown(f"""
        <div class="ai-explain">
        🤖 <b>AI is detecting:</b> {", ".join(snapshot['events'])} right now.
        Extra vehicles have been pre-positioned on affected routes.
        Current avg wait: <b>{snapshot['avg_wait_min']} min</b>
        vs <b>{round(snapshot['avg_wait_min']*1.35,1)} min</b> without AI.
        </div>
        """, unsafe_allow_html=True)

    col_map, col_side = st.columns([3,1])

    with col_map:
        tab1, tab2 = st.tabs(["🗺️ Live Fleet Map", "🔥 Demand Heatmap"])
        with tab1:
            st.markdown('<div class="section-header">📍 Real-Time Pune Transit Map</div>', unsafe_allow_html=True)
            st_folium(build_operator_map(snapshot, route_filter), width=None, height=460, returned_objects=[])
            st.caption("🟢 <8 min · 🟡 8–15 min · 🔴 >20 min wait · 🚌 = PMPML bus · 🚇 = Pune Metro · Dashed = bus route · Solid = metro")
        with tab2:
            st.markdown('<div class="section-header">🔥 Passenger Demand Heatmap — Pune</div>', unsafe_allow_html=True)
            st_folium(build_heatmap(snapshot), width=None, height=460, returned_objects=[])
            st.caption("Dark map · Blue→Yellow→Red = low→medium→very high demand zones")

    with col_side:
        st.markdown('<div class="section-header">🤖 AI Rebalancing Feed</div>', unsafe_allow_html=True)
        wm_val = WEATHER_MULT[snapshot['weather']]
        st.markdown(f"""
        <div class="weather-card">
          <div style="font-size:1.5rem">{snapshot['weather']}</div>
          <div style="font-size:0.75rem;opacity:0.8;margin-top:2px">Pune · Right Now</div>
          <div style="font-size:0.8rem;background:rgba(255,255,255,0.15);border-radius:6px;padding:3px 10px;margin-top:8px;display:inline-block">
            Demand impact: {'+' if wm_val>=1 else ''}{round((wm_val-1)*100,0):.0f}%
          </div>
        </div>
        """, unsafe_allow_html=True)

        recent = [r for r in rebalance_log if abs(r["step"]-now_step)<=8][-6:]
        if recent:
            for r in reversed(recent):
                icon = "🔴" if r["severity"]=="critical" else "🟡"
                st.markdown(f"""
                <div class="alert-item {r['severity']}">
                  <div class="alert-time">{r['time']} {icon}</div>
                  <div class="alert-text">{r['from_route']} → {r['to_route']}</div>
                  <div class="alert-sub">{r['reason'][:52]}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-item success">
              <div class="alert-time">✓ System Stable</div>
              <div class="alert-text">No rebalancing needed</div>
              <div class="alert-sub">All routes within optimal range</div>
            </div>
            """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-header">📈 24h Demand vs Capacity</div>', unsafe_allow_html=True)
        st.plotly_chart(demand_chart(history), use_container_width=True, config={"displayModeBar":False})
    with c2:
        st.markdown('<div class="section-header">⏱ Wait Time: AI vs No AI</div>', unsafe_allow_html=True)
        st.plotly_chart(wait_chart(history), use_container_width=True, config={"displayModeBar":False})

    c3, c4 = st.columns([2,1])
    with c3:
        st.markdown('<div class="section-header">🚌 Route Utilization Right Now</div>', unsafe_allow_html=True)
        st.plotly_chart(util_chart(snapshot), use_container_width=True, config={"displayModeBar":False})
    with c4:
        st.markdown('<div class="section-header">🤖 AI Decision Timeline</div>', unsafe_allow_html=True)
        st.plotly_chart(rebalance_timeline(rebalance_log), use_container_width=True, config={"displayModeBar":False})

    st.markdown('<div class="section-header">📋 Full Fleet Status</div>', unsafe_allow_html=True)
    rows = []
    for rid, rd in ALL_ROUTES.items():
        dem  = snapshot["route_demand"].get(rid,0)
        cap  = snapshot["route_capacity"].get(rid,1)
        util = dem/max(cap,1)*100
        n    = snapshot["bus_counts"].get(rid,0)
        rows.append({
            "Route": rid, "Name": rd["name"], "Type": rd["type"].upper(),
            "Vehicles": n, "Demand": dem, "Capacity": cap,
            "Utilization": f"{util:.0f}%",
            "Status": "🔴 Overcrowded" if util>85 else "🟡 Busy" if util>60 else "🟢 Normal" if util>25 else "⚪ Idle",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════
# COMMUTER VIEW
# ══════════════════════════════════════════════════════════════════
else:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0f4c81,#1e3a5f);border-radius:12px;
    padding:1rem 1.5rem;margin-bottom:1rem;color:white">
    <b style="font-size:1rem">🧑‍💼 Commuter View</b>
    <span style="opacity:0.6;font-size:0.82rem;margin-left:8px">
      Find your bus · Check wait times · Plan your journey across Pune
    </span>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns([1,2])

    with col_l:
        st.markdown('<div class="section-header">📍 Your Stop</div>', unsafe_allow_html=True)
        stop_names = sorted(PMPML_STOPS.keys())
        sel_stop = st.selectbox("Search your bus stop", stop_names,
                                index=stop_names.index("Shivajinagar"))
        wait = snapshot["stop_wait"].get(sel_stop)
        demand = snapshot["stop_demand"].get(sel_stop, 0)

        if wait is not None:
            if wait < 8:    wcolor, wstatus = "#10b981", "🟢 Low wait"
            elif wait < 15: wcolor, wstatus = "#f59e0b", "🟡 Moderate wait"
            else:           wcolor, wstatus = "#ef4444", "🔴 High wait"
        else:
            wcolor, wstatus = "#94a3b8", "No service"

        st.markdown(f"""
        <div class="stop-card" style="border-left:4px solid {wcolor}">
          <div class="stop-name">📍 {sel_stop}</div>
          <div class="stop-wait" style="color:{wcolor}">{wait} min</div>
          <div style="font-size:0.78rem;color:#64748b">{wstatus} · {demand} people waiting now</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">🚌 Buses From This Stop</div>', unsafe_allow_html=True)
        serving = [(rid,rd) for rid,rd in ALL_ROUTES.items() if sel_stop in rd["stops"]]
        if serving:
            for rid, rd in serving:
                n = snapshot["bus_counts"].get(rid,0)
                util = snapshot["route_demand"].get(rid,0)/max(snapshot["route_capacity"].get(rid,1),1)*100
                bar_color = "#ef4444" if util>85 else "#f59e0b" if util>60 else "#10b981"
                icon = "🚇" if rd["type"]=="metro" else "🚌"
                st.markdown(f"""
                <div class="stop-card">
                  <div style="display:flex;justify-content:space-between">
                    <span class="route-badge" style="background:{rd['color']}22;color:{rd['color']}">{rid}</span>
                    <span style="font-size:0.7rem;color:#94a3b8">{rd['type'].upper()}</span>
                  </div>
                  <b style="font-size:0.88rem">{icon} {rd['name'][:36]}</b>
                  <div style="font-size:0.78rem;color:#64748b;margin-top:4px">
                    Every ~{rd['frequency_min']} min · {n} vehicles · Crowd: {util:.0f}%
                  </div>
                  <div class="util-bar-wrap"><div class="util-bar" style="width:{min(util,100):.0f}%;background:{bar_color}"></div></div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No routes directly serve this stop.")

        # AI tip
        if wait and wait > 15:
            nearby = [(s, snapshot["stop_wait"].get(s)) for s in PMPML_STOPS
                      if s!=sel_stop and snapshot["stop_wait"].get(s) is not None
                      and math.sqrt((PMPML_STOPS[s][0]-PMPML_STOPS[sel_stop][0])**2+
                                    (PMPML_STOPS[s][1]-PMPML_STOPS[sel_stop][1])**2)<0.04]
            nearby.sort(key=lambda x: x[1])
            if nearby:
                alt, alt_wait = nearby[0]
                st.markdown(f"""
                <div class="ai-explain">
                🤖 <b>AI Tip:</b> Wait at <b>{sel_stop}</b> is high ({wait} min).
                Try <b>{alt}</b> nearby — only <b>{alt_wait} min wait</b>!
                </div>
                """, unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="section-header">🗺️ Your Stop on the Pune Map</div>', unsafe_allow_html=True)
        st_folium(build_commuter_map(sel_stop, snapshot), width=None, height=360, returned_objects=[])

        st.markdown('<div class="section-header">⏱ All Stop Wait Times Right Now</div>', unsafe_allow_html=True)
        wait_rows = []
        for stop in sorted(PMPML_STOPS.keys()):
            w = snapshot["stop_wait"].get(stop)
            d = snapshot["stop_demand"].get(stop,0)
            srvd = [rid for rid,rd in ALL_ROUTES.items() if stop in rd["stops"]]
            if w is not None:
                status = "🟢 Good" if w<8 else "🟡 Moderate" if w<15 else "🔴 High"
                wait_rows.append({"Stop": stop, "Wait": f"{w} min", "Waiting Now": d,
                                  "Routes": ", ".join(srvd[:3]), "Status": status})
        st.dataframe(pd.DataFrame(wait_rows), use_container_width=True, hide_index=True, height=280)

    # JOURNEY PLANNER
    st.markdown('<div class="section-header">🗺️ Journey Planner</div>', unsafe_allow_html=True)
    c_from, c_to, c_btn = st.columns([2,2,1])
    with c_from:
        from_stop = st.selectbox("From", stop_names, index=stop_names.index("Shivajinagar"), key="jp_from")
    with c_to:
        to_stop = st.selectbox("To", stop_names, index=stop_names.index("Hinjewadi Phase 1"), key="jp_to")
    with c_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("🔍 Plan Route")

    from_routes = {rid for rid,rd in ALL_ROUTES.items() if from_stop in rd["stops"]}
    to_routes   = {rid for rid,rd in ALL_ROUTES.items() if to_stop   in rd["stops"]}
    direct = from_routes & to_routes

    if direct:
        st.markdown("**✅ Direct routes found:**")
        for rid in direct:
            rd = ALL_ROUTES[rid]
            stops_l = rd["stops"]
            try:
                fi, ti = stops_l.index(from_stop), stops_l.index(to_stop)
                ns = abs(ti-fi)
                icon = "🚇" if rd["type"]=="metro" else "🚌"
                w_from = snapshot["stop_wait"].get(from_stop, "?")
                st.markdown(f"""
                <div class="stop-card" style="border-left:4px solid {rd['color']}">
                  <b>{icon} {rid} — {rd['name']}</b>
                  <div style="font-size:0.82rem;color:#475569;margin-top:6px">
                    {from_stop} {"→" if ti>fi else "← (reverse)"} {to_stop}
                    · <b>{ns} stops</b> · ~{ns*rd['frequency_min']} min journey<br>
                    ⏱ Wait at {from_stop}: <b>{w_from} min</b>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            except ValueError:
                pass
    else:
        st.markdown(f"""
        <div class="ai-explain">
        🤖 No direct route from <b>{from_stop}</b> to <b>{to_stop}</b>.
        Suggested interchange: <b>Shivajinagar</b> or <b>Pune Railway Station</b>
        — both are major hubs connecting all parts of the city.
        </div>
        """, unsafe_allow_html=True)

# FOOTER
st.markdown("---")
st.markdown("""
<div style="text-align:center;font-size:0.72rem;color:#94a3b8;padding:0.5rem">
Coruscant Transit Command — Pune Edition &nbsp;·&nbsp;
PMPML Routes 11, 50, 72, 152, Airport Express, PCMC Corridor &nbsp;·&nbsp;
Pune Metro Line 1 (PCMC–Swargate) & Line 2 (Kothrud–Kharadi) &nbsp;·&nbsp;
Real Pune GPS coordinates · Demand modeled on PMPML ridership patterns · Built for PS4 Hackathon
</div>
""", unsafe_allow_html=True)