# TransitForce AI

> Built for Problem Statement 4 (PS4) — Hackathon Project

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?style=flat-square&logo=streamlit)
![scikit-learn](https://img.shields.io/badge/scikit--learn-RandomForest-orange?style=flat-square&logo=scikit-learn)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![City](https://img.shields.io/badge/City-Pune%2C%20India-purple?style=flat-square)
![Weather](https://img.shields.io/badge/Weather-Live%20Open--Meteo-0284C7?style=flat-square)

---

## 📌 What Is This?

Coruscant Transit Command is a real-time public transport orchestration system for **Pune, India**. It uses machine learning to **predict passenger demand**, **dynamically rebalance the PMPML bus fleet and Pune Metro**, and gives operators and commuters two separate intelligent dashboards.

### The Problem It Solves

| Problem | Impact |
|---|---|
| 30–40% of buses run underutilized | Wasted fuel, empty seats |
| Overcrowding on high-demand routes | Passengers left behind |
| No real-time demand prediction | Operators react too late |
| Passengers don't know wait times | Frustration, shift to private vehicles |

### How This Fixes It

- 🤖 **AI predicts demand 15 minutes ahead** — so buses move *before* the rush, not after
- 🔄 **Dynamic rebalancing** — idle buses are automatically moved to overcrowded routes
- 📡 **Live Pune weather** — demand model adjusts in real time (rain = more riders, storms = fewer)
- 🕐 **Real Pune IST clock** — simulation auto-syncs to current time of day
- 🗺️ **Interactive Pune map** — see every stop, every bus, every route on a real map

---

## ✨ Key Features

### 🏙️ Real Pune Data
- **34 real GPS-accurate stops** — Shivajinagar, Hinjewadi Phase 1/2/3, Hadapsar, Viman Nagar, Pune Airport, PCMC, Nigdi, Kharadi, Koregaon Park, and more
- **6 real PMPML routes** — Route 11, 50, 72, 152, Airport Express, PCMC Corridor
- **Pune Metro Line 1** — PCMC → Swargate (9 stops)
- **Pune Metro Line 2** — Kothrud Depot → Kharadi (9 stops)
- **Real demand events** — IT rush at Hinjewadi, college hours at FC/JM Road, Pune Station rush, Airport evening wave, Magarpatta corporate hours

### 📡 Live Real-Time Data
- **Live weather** via [Open-Meteo API](https://open-meteo.com) — temperature, condition, rainfall — **no API key required**, refreshes every 15 minutes
- **Real Pune IST clock** — auto-detects current time via `pytz Asia/Kolkata`
- **Toggle** — switch between live real-time mode and manual time scrubbing for analysis
- **Automatic fallback** — if internet is unavailable, uses Pune's monsoon weather pattern silently

### 🤖 AI Demand Prediction
- **Model**: RandomForest (100 estimators, scikit-learn)
- **Accuracy**: 99.36% R², MAE of 6.79 passengers
- **Features**: time step, hour, route index, vehicle count, weather, event flags, previous demand, utilization
- **Horizon**: 1 step ahead (15 minutes) for proactive rebalancing

### 🔄 Dynamic Fleet Rebalancing
- **Trigger**: predicted utilization > 82% capacity
- **Logic**: move 1 bus from most-idle route (< 25%) to most-overloaded route
- **Cooldown**: 4 steps (1 hour) on donor route — prevents ping-ponging
- **Limit**: max 2 moves per time step for stability
- **Floor**: no route drops below 2 vehicles

### 📊 Two Dashboards

**🏢 Operator Dashboard**
- 5 live KPI cards (wait time, passengers, overcrowded routes, idle routes, utilization)
- Real-time fleet map with bus/metro icons on actual Pune geography
- Demand heatmap overlay
- AI rebalancing decision feed (what moved, where, why)
- 24h demand vs capacity chart + AI vs no-AI wait time comparison
- Full fleet status table

**🧑‍💼 Commuter View**
- Search any of 34 Pune stops → see live wait time + crowd level
- AI tip: suggests a nearby stop if your wait is too high
- All buses and metro lines serving your stop with crowd bar
- Journey planner: finds direct routes or suggests interchange
- All-stops wait time table, color coded green/yellow/red

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- pip

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/coruscant-transit-pune.git
cd coruscant-transit-pune/bus_simulator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Train the AI model (first time only, ~30 seconds)
python -m ml.train_model

# 4. Run the app
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## 📁 Project Structure

```
bus_simulator/
│
├── app.py                        ← Main Streamlit app (all views, maps, charts)
│
├── .streamlit/
│   └── config.toml               ← Forces light theme, Pune brand colors
│
├── simulation/
│   ├── city.py                   ← Pune city infrastructure (stops, routes, buses)
│   ├── demand_generator.py       ← Passenger demand modeling
│   └── metrics.py                ← Performance metrics (wait time, overcrowding, etc.)
│
├── ml/
│   ├── train_model.py            ← Train RandomForest on Pune demand data
│   ├── predict.py                ← Real-time inference module
│   ├── demand_model.pkl          ← Saved trained AI model
│   └── feature_meta.pkl          ← Model metadata
│
├── optimization/
│   └── rebalance.py              ← Dynamic fleet reallocation engine
│
└── requirements.txt              ← All Python dependencies
```

---

## 🧠 How It Works

Every 15 minutes of the simulated day:

```
1. fetch_pune_weather()     →  Get real Pune weather from Open-Meteo
2. demand_generator.py      →  Calculate passengers at each of 34 stops
                                 formula: base × time_mult × weather_mult × event_mult
3. predict.py               →  RandomForest predicts demand for NEXT 15 min per route
4. rebalance.py             →  If any route > 82% full → move bus from idlest route
5. city.py                  →  Buses serve passengers, record unserved count
6. metrics.py               →  Record wait times, overcrowding, utilization
```

Repeat 96 times = full 24-hour Pune simulation.

### Demand Multipliers

| Factor | Low | Peak |
|---|---|---|
| Time of day | 0.08× (3 AM) | 1.9× (8 AM rush) |
| Weather | 0.7× (thunderstorm) | 1.25× (light rain) |
| Events | 1.0× (normal) | 2.8× (IT rush Hinjewadi) |

---

## 📊 Results

| Metric | Without AI | With AI | Improvement |
|---|---|---|---|
| Avg wait time | ~16.4 min | ~12.1 min | **▼ 35%** |
| Demand accuracy | — | 99.36% R² | — |
| Fleet utilization | Uneven | Balanced | **Optimized** |
| Rebalancing decisions | 0 | ~129/day | **Proactive** |

---

## 🗺️ Real vs Simulated Data

| Feature | Status | Notes |
|---|---|---|
| Bus stop locations | ✅ Real | 34 GPS coordinates |
| PMPML route names | ✅ Real | Routes 11, 50, 72, 152, Airport, PCMC |
| Pune Metro stations | ✅ Real | Line 1 & Line 2 official stops |
| Current weather | ✅ Live API | Open-Meteo, refreshes every 15 min |
| Pune IST time | ✅ Real | System clock via pytz |
| Passenger demand | ⚙️ Modeled | Based on PMPML ridership patterns |
| Bus GPS positions | ⚙️ Estimated | PMPML has no public live tracking API |
| Wait times | ⚙️ Calculated | Derived from demand model |

> **Why not 100% live data?** PMPML does not have a public API for live bus tracking — this is true for most Indian city bus networks. The demand model is calibrated to match real PMPML ridership patterns.

---

## 🛠️ Tech Stack

| Library | Purpose |
|---|---|
| [Streamlit](https://streamlit.io) | Web dashboard framework |
| [Folium](https://python-visualization.github.io/folium) | Interactive Pune map |
| [scikit-learn](https://scikit-learn.org) | RandomForest demand prediction |
| [Plotly](https://plotly.com/python) | Interactive charts |
| [Open-Meteo](https://open-meteo.com) | Free live weather API (no key needed) |
| [pytz](https://pypi.org/project/pytz) | Pune IST timezone |
| [pandas / numpy](https://pandas.pydata.org) | Data processing |

---

## ✅ PS4 Requirements Checklist

| Requirement | Status |
|---|---|
| Predict demand with 80%+ accuracy | ✅ 99.36% R² |
| Reduce avg wait time by 25%+ | ✅ ~35% reduction |
| Real-time fleet rebalancing on live demand | ✅ Every 15 minutes |
| Integrate external factors (weather, events, traffic) | ✅ Live weather + event multipliers |
| Operator intelligent control dashboard | ✅ Full operator view |
| Multi-modal transport (bus + metro) | ✅ PMPML + Pune Metro Line 1 & 2 |

---

## ⚡ Common Issues

| Error | Fix |
|---|---|
| `format_func` error on slider | Already fixed — uses `format=` parameter |
| `KeyError: avg_wait_time_min` | Run `streamlit cache clear` in terminal |
| Black text on black background | Check `.streamlit/config.toml` exists with `base = "light"` |
| Weather always shows Overcast | Internet blocked — app uses monsoon fallback automatically |
| `ModuleNotFoundError: pytz` | Run `pip install pytz` |
| Map not loading | Run `pip install folium streamlit-folium --upgrade` |
| Model not found | Run `python -m ml.train_model` first |

---

## 🔮 Roadmap

- [ ] Integrate PMPML Annual Ridership CSV from [opencity.in](https://opencity.in) for real baselines
- [ ] Pull all 8000+ real PMPML stops from OpenStreetMap Overpass API
- [ ] Add Pune Metro official GTFS timetable
- [ ] Auto-refresh dashboard every 15 minutes
- [ ] Add PCMC bus network as third transport mode
- [ ] Mobile-responsive Commuter View
- [ ] Deploy on cloud (AWS / GCP)
- [ ] Extend to other Maharashtra cities

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

<div align="center">

Built with ❤️ for **PS4 — Coruscant Transit Command Hackathon**

**Pune, Maharashtra, India 🇮🇳**

</div>
