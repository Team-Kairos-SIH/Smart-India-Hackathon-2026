# KAIROS: Urban Flood Nowcasting & Tactical Digital Twin
### Physics-Coupled 1D-2D Hydro-Meteorological Nowcasting Engine for Greater Chennai Corporation

[![Smart India Hackathon 2026](https://img.shields.io/badge/SIH-2026-blue.svg)](https://www.sih.gov.in/)
[![Problem Statement](https://img.shields.io/badge/MoES%20%2F%20NCMRWF-PS%2026085-orange.svg)](https://www.sih.gov.in/)
[![End-to-End Latency](https://img.shields.io/badge/Full%20Twin%20Coupler-152%20ms-brightgreen.svg)](#master-5-layer-coupler)
[![Python 3.13+](https://img.shields.io/badge/Python-3.13%2B-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Web GIS](https://img.shields.io/badge/Frontend-Leaflet%20Tactical%20Twin-199900.svg)](https://leafletjs.com/)
[![Standard](https://img.shields.io/badge/Alerts-OASIS%20CAP%20v1.2-blueviolet.svg)](http://docs.oasis-open.org/emergency/cap/v1.2/)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](#automated-testing--verification)

> **KAIROS** is a physics-guided 1D-2D hydro-meteorological digital twin engineered for **Smart India Hackathon 2026 (Problem Statement PS 26085)** under the **Ministry of Earth Sciences (MoES)** and **NCMRWF**, deployed for the **Greater Chennai Corporation (GCC)**. 
> 
> The system predicts street-level urban inundation, conduit surcharges, and wash-away hazards at a **0 to 3 hour lead time** across all **7,894 road corridors** and **15 administrative zones** of Chennai. By coupling Doppler Weather Radar nowcasts, Cartosat-1 DEM runoff, 1D subsurface SWD graph hydraulics, and a physics-informed surrogate engine, KAIROS achieves full-city hydrodynamic simulation in **152 ms**.

---

## Table of Contents
1. [End-to-End 5-Layer Architecture](#end-to-end-5-layer-architecture)
2. [Master 5-Layer Coupler (`master_coupler.py`)](#master-5-layer-coupler)
3. [The 7 Tactical Add-Ons](#the-7-tactical-add-ons)
   - [1. Street-as-Canal Conveyance ($v \times d$ Hazard)](#1-street-as-canal-conveyance-engine)
   - [2. Automated Municipal Pump Dispatch Optimizer](#2-automated-municipal-pump-dispatch-optimizer)
   - [3. Coastal Tidal Lockout & Cyclonic Storm Surge](#3-coastal-tidal-lockout--cyclonic-storm-surge)
   - [4. Opportunistic Telecom CML Virtual Rain Gauge Mesh](#4-opportunistic-telecom-cml-virtual-rain-gauge-mesh)
   - [5. CAP v1.2 Multilingual Emergency Bulletins](#5-cap-v12-multilingual-emergency-bulletins)
   - [6. Incident Commander 'What-If' Simulation Sandbox](#6-incident-commander-what-if-simulation-sandbox)
   - [7. Street Cross-Section Profile & Geyser Surcharge](#7-street-cross-section-profile--geyser-surcharge)
4. [Complete REST API Reference](#complete-rest-api-reference)
5. [Repository Directory Structure](#repository-directory-structure)
6. [Quick Start & CLI Verification](#quick-start--cli-verification)
7. [Team Kairos - SIH 2026](#team-kairos---sih-2026)

---

## End-to-End 5-Layer Architecture

```
                          STAGE 1: ATMOSPHERIC & TELECOM INGESTION (LAYER 0)
        +-----------------------------------+-----------------------------------+
        |   IMD Dual-Pol Doppler Radar      |   Opportunistic Telecom CML Mesh  |
        |   (Meenambakkam / Chennai Port)   |   (Cellular Backhaul 13-73 GHz)   |
        |   10-min SRI & PAC Grids          |   Near-Surface Rain Attenuation   |
        +-----------------+-----------------+-----------------+-----------------+
                          |                                   |
                          v                                   v
        +-----------------------------------------------------------------------+
        |       Kriging with External Drift (KED) Gauge-Radar-CML Fusion        |
        |       Corrects convective Drop Size Distribution (DSD) bias in real-time
        +-----------------------------------+-----------------------------------+
                                            |
                                            v
        +-----------------------------------------------------------------------+
        |       Farneback Semi-Lagrangian Optical Flow Nowcaster (PySteps)      |
        |       Projects storm field advection: T+15m, T+30m, T+60m ... T+180m  |
        |       (Sub-3 ms optical flow projection over Chennai domain)           |
        +-----------------------------------+-----------------------------------+
                                            |
                                            v
                          STAGE 2: 2D RUNOFF & DTM INFILTRATION (LAYER 1)
        +-----------------------------------------------------------------------+
        |       Cartosat-1 10m DEM + Sentinel-2 LULC Soil Hydrology             |
        |       Computes SCS-CN infiltration & overland runoff for 7,894 roads  |
        +-----------------------------------+-----------------------------------+
                                            |
                                            v
                          STAGE 3: 1D SUBSURFACE CONDUIT HYDRAULICS (LAYER 2)
        +-----------------------------------+-----------------------------------+
        |  1D Stormwater Drainage Graph     |  Coastal Tidal Lockout Engine     |
        |  - Manning pipe flow routing      |  - Bay of Bengal M2/S2 tide       |
        |  - Dynamic solid waste clogging   |  - Holland cyclonic storm surge   |
        |  - Manhole HGL surcharge backflow |  - 4 tidal outfalls lockout status|
        +-----------------+-----------------+-----------------+-----------------+
                          |                                   |
                          +-----------------+-----------------+
                                            v
                          STAGE 4: SURROGATE & CANAL CONVEYANCE (LAYER 3)
        +-----------------------------------------------------------------------+
        |  Physics-Informed Topological Graph Surrogate             |
        |  - Strict mass-conservation boundary condition                        |
        |  - Street-as-Canal Conveyance (Manning velocity & v x d hazard tier)  |
        +-----------------------------------+-----------------------------------+
                                            |
                                            v
                          STAGE 5: TACTICAL EMERGENCY DECISION SUPPORT (LAYER 4)
        +-----------------------------------+-----------------------------------+
        |  First Responder A* Navigation    |  Automated Municipal Pump Planner |
        |  - Clearance routing for rescue   |  - Optimal diesel trash pump sites|
        |  - Substation asset flood safety  |  - Multilingual OASIS CAP v1.2 XML|
        +-----------------------------------------------------------------------+
```

---

## Master 5-Layer Coupler

The **Master Coupler** (`ai_service/orchestration/master_coupler.py`) unites all 5 KAIROS layers into a single in-memory execution pipeline with zero intermediate disk serialization bottlenecks.

### 152 ms End-to-End Latency Breakdown

On standard server hardware, the warmed-up pipeline executes across all **7,894 road corridors** in **~152 ms** (consistently sub-second across 100% of tested storm scenarios):

| Layer | Subsystem Description | Processing Latency | Key Physics / Algorithm |
|---|---|---|---|
| **Layer 0** | Multi-Sensor Radar + CML Virtual Gauge Mesh | **~26 ms** | Semi-Lagrangian Optical Flow + ITU-R P.838 CML Inversion |
| **Layer 1** | Cartosat-1 DEM & Soil Runoff Generator | **~43 ms** | Modified SCS-CN & Antecedent Moisture Condition (AMC-III) |
| **Layer 2** | 1D Conduit Hydraulics, Clogging & Tide | **~47 ms** | Manning Pipe Flow, HGL Surcharge & Holland Surge Setup |
| **Layer 3** | Physics-Informed Topological Graph Surrogate & Street Conveyance | **~28 ms** | Mass-Conserved Surrogate + Street Open-Channel Hydraulics |
| **Layer 4** | Tactical Pump Dispatch & Hazard Ranking | **~8 ms** | Dynamic Priority Queue & Critical Infrastructure Weighting |
| **Total** | **Full 5-Layer Hydrodynamic Twin** | **~152 ms** | **Complete Citywide Hydro-Meteorological Solution** |

### Execution Data Pipeline

The Master Coupler produces a structured `MasterTwinResult` containing:
- `dataframe`: Pandas DataFrame of all 7,894 corridors with 0-180m flood depths, Manning velocities, discharges, and wash-away hazard tiers.
- `horizons_depths`: Multi-step depth arrays for $T+15\text{m}, T+30\text{m}, T+60\text{m}, T+90\text{m}, T+120\text{m}, T+180\text{m}$.
- `pump_recommendations`: Top municipal de-watering pump dispatch sites ranked by volume relief and asset priority.
- `coastal_outfall_status`: Lockout state and tailwater elevation for Chennai's 4 primary coastal river outfalls.
- `cml_telemetry`: Opportunistic cellular link rain rates filling radar blind zones.
- `street_conveyance_summary`: Active street canals and pedestrian hazard counts.

---

## The 7 Tactical Add-Ons

### 1. Street-as-Canal Conveyance Engine
*Module:* `ai_service/layer3/street_conveyance.py` | *API:* `GET /api/street-flow`

When underground stormwater drains surcharge during extreme cloudbursts, roads cease to function as transportation corridors and transform into open-channel canals. The Street Conveyance Engine computes:

- **Open-Channel Manning Flow Velocity**:
  $$v = \frac{1}{n} \cdot R_h^{2/3} \cdot S^{1/2}$$
  Where $n = 0.016$ (asphalt roughness), $R_h \approx d$ (hydraulic radius for wide shallow street sheets), and $S$ is street terrain slope derived from Cartosat-1.

- **Corridor Discharge Capacity**:
  $$Q_{\text{street}} = A_{\text{flow}} \cdot v = (W_{\text{street}} \cdot d) \cdot v \quad [\text{m}^3/\text{s}]$$

- **Velocity-Depth ($v \times d$) Wash-Away Hazard Index**:
  Following international flood hazard safety standards (Australian Rainfall and Runoff / UK DEFRA):
  - **LOW** ($v \times d < 0.3\,\text{m}^2/\text{s}$): Safe for adult pedestrian wading.
  - **MODERATE** ($0.3 \le v \times d < 0.6\,\text{m}^2/\text{s}$): Hazardous for children/elderly; stability compromised.
  - **HIGH** ($0.6 \le v \times d < 1.2\,\text{m}^2/\text{s}$): Dangerous to all pedestrians; passenger vehicles float and lose traction.
  - **EXTREME** ($v \times d \ge 1.2\,\text{m}^2/\text{s}$): Severe structural wash-away danger; even heavy emergency trucks at risk of overturning.

- **Active Street Channel Identification**:
  Identifies street segments where $Q > 1.0\,\text{m}^3/\text{s}$ and $v > 0.5\,\text{m}/\text{s}$ to trigger automatic barricading advisories.

---

### 2. Automated Municipal Pump Dispatch Optimizer
*Module:* `ai_service/layer4/pump_optimizer.py` | *API:* `GET /api/recommendations/pumps`

Automates the tactical decision-making process for Greater Chennai Corporation (GCC) engineers stationed at the Ripon Building Integrated Command and Control Centre (ICCC):

- **Targeted De-Watering Capacity**:
  $$Q_{\text{req}} = \frac{V_{\text{ponding}}}{\Delta t_{\text{clearance}}} = \frac{A_{\text{corridor}} \cdot d_{\text{flood}}}{3600} \quad [\text{m}^3/\text{hr}]$$

- **Standard GCC Equipment Matching**:
  - `Mobile Diesel Trash Pump (150 HP)`: Rated at $800\,\text{m}^3/\text{hr}$ for high-priority underpasses and choked subways.
  - `High-Discharge Submersible Pump`: Rated at $2000\,\text{m}^3/\text{hr}$ for low-lying lake depressions (e.g., Velachery, Madipakkam).
  - `Dewatering Tractor PTO Pump`: Rated at $450\,\text{m}^3/\text{hr}$ for narrow residential relief roads.

- **Multi-Factor Priority Scoring**:
  Rankings weigh flood depth ($40\%$), critical infrastructure proximity ($30\%$, e.g., TANGEDCO 230kV substations, government hospitals), arterial highway status ($20\%$), and surcharge rate ($10\%$).

---

### 3. Coastal Tidal Lockout & Cyclonic Storm Surge
*Module:* `ai_service/layer2/coastal_boundary.py` | *API:* `GET /api/coastal/outfalls`

Chennai's drainage system discharges into the Bay of Bengal. During cyclonic events (such as Cyclone Michaung), storm surges and high tides create hydraulic tailwater heads that exceed outfall inverts, locking one-way flap gates and causing catastrophic backwater flooding.

- **Harmonic Astronomical Tidal Prediction**:
  Computes sea surface elevation using official Survey of India / INCOIS tidal constituents for Chennai Port:
  $$\eta_{\text{tide}}(t) = \sum_{i} A_i \cos\left(\frac{2\pi t}{T_i} - \phi_i\right) \quad [M_2, S_2, N_2, K_1, O_1, M_4]$$

- **Holland Parametric Cyclonic Storm Surge**:
  Couples the inverted barometer effect ($\Delta h = 1.01 \cdot (1013 - P_c)\,\text{cm}$) and wind shear setup:
  $$S_{\text{surge}} = \Delta h_{\text{baro}} + \frac{C_d \cdot \rho_{\text{air}} \cdot U_{10}^2 \cdot F}{g \cdot H_{\text{shelf}}}$$

- **Monitored Coastal Outfalls**:
  1. *Adyar River Estuary* (Besant Nagar)
  2. *Cooum River Mouth* (Napier Bridge)
  3. *Buckingham Canal Outfall* (Mylapore / Adyar Junction)
  4. *Ennore Creek* (Kosasthalaiyar Outlet)

- **Lockout Classification**:
  Dynamically reports each outfall as `FREE_GRAVITY`, `THROTTLED_BACKWATER`, `TIDAL_LOCKOUT`, or `REVERSE_INTRUSION`.

---

### 4. Opportunistic Telecom CML Virtual Rain Gauge Mesh
*Module:* `ai_service/layer0/cml_mesh.py` | *API:* `GET /api/cml/telemetry`

Doppler weather radar beams overshoot near-surface rain in the lowest 500 meters of the atmosphere and experience ground clutter near urban high-rises. KAIROS turns existing cellular transmission towers (Airtel, Jio, Vodafone-Idea) into a hyper-dense virtual rain gauge network.

- **ITU-R P.838-3 Power-Law Inversion**:
  Microwave attenuation along a cellular link path of length $L$ is directly proportional to rain rate $R$:
  $$A = a \cdot R^b \cdot L \iff R = \left(\frac{A - A_{\text{waa}}}{a \cdot L}\right)^{1/b} \quad [\text{mm/hr}]$$
  Supported bands: 13, 15, 18, 23, 26, 38, and 73 GHz (E-band) for both Horizontal ($H$) and Vertical ($V$) polarizations.

- **Wet Antenna Attenuation (WAA) Compensation**:
  Applies dynamic baseline tracking to isolate atmospheric rain attenuation from water droplets sticking to antenna radomes.

- **Zero-Infrastructure Cost**:
  Leverages existing telecom infrastructure across Chennai without deploying expensive physical rain gauges.

---

### 5. CAP v1.2 Multilingual Emergency Bulletins
*Module:* `ai_service/layer4/cap_emitter.py` | *API:* `GET /api/alerts/cap`

Fully compliant with international **ITU-T Recommendation X.1303** and **OASIS Common Alerting Protocol (CAP) v1.2** for automated downstream broadcasting to **NDMA SACHET**, TNSDMA, and GCC emergency response systems.

- **Dual-Language Automated Generation**:
  Simultaneously generates synchronized alert payloads in:
  - **English (`en-IN`)**: For administrative dispatch, national disaster management, and inter-agency coordination.
  - **Tamil (`ta-IN`)**: For localized citizen advisories, ward councillors, and vernacular media broadcasts.

- **Targeted Bulletins**:
  - *Technical Ward Engineer Bulletin*: Delivered via automated API/WhatsApp webhooks with precise manhole surcharge flow rates ($Q_{\text{surch}}$), geyser eruption risks, and required pump HP.
  - *Citizen SMS Advisory*: Concise 160-character alerts containing safe evacuation corridors and GCC 1913 helpline instructions.

---

### 6. Incident Commander 'What-If' Simulation Sandbox
*Module:* `ai_service/api.py` | *API:* `POST /api/simulate/what-if`

Empowers the GCC Disaster Incident Commander to simulate mitigation scenarios in real-time (**sub-50 ms** response latency):

- **Interactive Scenario Knobs**:
  - Cloudburst Rainfall Slider ($0$ to $200\,\text{mm/hr}$)
  - Bay of Bengal Cyclonic Storm Surge ($0.0$ to $3.0\,\text{m}$)
  - Solid Waste Drainage Choking Penalty ($\mu_{\text{clog}} \in [0.0, 0.85]$)
  - Mobile De-Watering Pump Units Deployed ($0$ to $20$ units)

- **Real-Time Delta Analysis**:
  Calculates instant deltas comparing the unmitigated baseline against the proposed deployment:
  - Peak water depth reduction ($\Delta d\,\text{cm}$)
  - Number of flooded road corridors relieved
  - Tidal outfall lockout transition states
  - Optimized equipment relocation directives

---

### 7. Street Cross-Section Profile & Geyser Surcharge
*Module:* `ai_service/api.py` | *API:* `GET /api/cross-section`

Implements Indian Roads Congress (**IRC:SP:50**) and Ministry of Urban Development (**CPHEEO**) urban road cross-section geometry:

- **Sidewalk Curb Overtopping**:
  Evaluates 15 cm standard concrete curbs. When flood depth exceeds 15 cm, excess water spills over onto sidewalks, inundating pedestrian zones and ground-floor properties.

- **Pavement Camber Drainage**:
  Accounts for $2.5\%$ parabolic road camber directing runoff into lateral curb inlets.

- **Pressurized Manhole Geyser Eruption**:
  When underground hydraulic grade line (HGL) exceeds street elevation, surcharging water pops unbolted manhole lids, creating upward geysers:
  $$h_{\text{plume}} \approx 0.42 \cdot d_{\text{surcharge}} \quad [\text{cm}]$$

- **Vehicle Impassability Matrix**:
  - `Two-Wheelers (Scooters/Bikes)`: Impassable at $d > 18\,\text{cm}$ (exhaust pipe water intake).
  - `Passenger Cars / Sedans`: Impassable at $d > 30\,\text{cm}$ (engine hydrostatic lock).
  - `Emergency Ambulances / Heavy Trucks`: Impassable at $d > 50\,\text{cm}$ or $v \times d > 0.6\,\text{m}^2/\text{s}$.

---

## Complete REST API Reference

The KAIROS FastAPI microservice runs on port `8000` and provides comprehensive endpoints for AI nowcasting, hydraulic simulations, tactical planning, and emergency routing:

### Endpoint Summary

| Method | Endpoint | Description | Tags |
|---|---|---|---|
| `GET` | `/api/health` | Service health, model status, and IMD radar connectivity | Health |
| `GET` | `/api/nowcast` | Layer 0-3 rainfall & street-level flood depth nowcast (0-180m) | Nowcasting |
| `POST` | `/route` | Layer 4 Time-dependent A* emergency rescue routing | Routing |
| `GET` | `/assets/status` | Flood risk monitoring for critical TANGEDCO substations | Critical Assets |
| `POST` | `/api/simulate/what-if` | Incident Commander tactical simulation sandbox (sub-50 ms) | Simulation |
| `GET` | `/api/street-flow` | Street-as-canal conveyance velocity, discharge & $v \times d$ hazard | Conveyance |
| `GET` | `/api/recommendations/pumps` | Optimal municipal de-watering pump dispatch recommendations | Dispatch |
| `GET` | `/api/cml/telemetry` | Opportunistic telecom CML virtual rain gauge mesh telemetry | Sensor Mesh |
| `GET` | `/api/coastal/outfalls` | Bay of Bengal coastal outfall tidal harmonics & storm surge | Boundary |
| `GET` | `/api/alerts/cap` | OASIS CAP v1.2 XML & multilingual (English + Tamil) bulletins | Public Alerts |
| `GET` | `/api/cross-section` | IRC:SP:50 street cross-section profile & manhole geyser plume | Profile |

---

### Endpoint Details & Example Requests

#### 1. Incident Commander 'What-If' Simulation
```bash
curl -X POST "http://127.0.0.1:8000/api/simulate/what-if" \
     -H "Content-Type: application/json" \
     -d '{
       "scenario": "michaung",
       "cloudburst_intensity_mm_hr": 110.0,
       "tidal_surge_m": 1.25,
       "clogging_factor": 0.45,
       "deployed_pumps_count": 6
     }'
```
*Response Snippet:*
```json
{
  "status": "success",
  "simulation_mode": "INCIDENT_COMMANDER_WHAT_IF",
  "latency_ms": 2.45,
  "impact_deltas": {
    "baseline_peak_depth_cm": 84.6,
    "mitigated_peak_depth_cm": 56.7,
    "depth_reduction_cm": 27.9,
    "flooded_corridors_relieved": 108,
    "outfalls_locked_out": 3
  }
}
```

#### 2. Street-as-Canal Conveyance ($v \times d$ Hazard)
```bash
curl "http://127.0.0.1:8000/api/street-flow?scenario=michaung&horizon=60"
```
*Response Snippet:*
```json
{
  "status": "success",
  "summary": {
    "evaluated_segments": 6,
    "active_street_channels_count": 4,
    "high_washaway_hazard_count": 2,
    "max_velocity_m_s": 2.14,
    "max_discharge_m3_s": 14.85
  }
}
```

#### 3. Automated Municipal Pump Dispatch Recommendations
```bash
curl "http://127.0.0.1:8000/api/recommendations/pumps?limit=5"
```
*Response Snippet:*
```json
{
  "status": "success",
  "beneficiary": "Greater Chennai Corporation (GCC ICCC Ripon Building)",
  "recommended_pumps": [
    {
      "priority_rank": 1,
      "road_name": "Usman Road Underpass (T. Nagar)",
      "zone_no": 9,
      "predicted_depth_cm": 58.5,
      "recommended_pump_type": "Mobile Diesel Trash Pump (150 HP)",
      "required_capacity_m3_hr": 800.0,
      "action_directive": "Deploy Mobile Diesel Trash Pump (150 HP) to Usman Road Underpass (T. Nagar) before T+60m"
    }
  ]
}
```

#### 4. Coastal Tidal Outfalls Status
```bash
curl "http://127.0.0.1:8000/api/coastal/outfalls?tide_surge_m=1.10"
```
*Response Snippet:*
```json
{
  "astronomical_tide_m_msl": 0.48,
  "cyclonic_surge_m": 1.1,
  "total_sea_level_m_msl": 1.58,
  "outfalls_locked_out": 2,
  "outfalls": [
    {
      "outfall_name": "Adyar River Estuary (Besant Nagar)",
      "sea_water_level_m_msl": 1.58,
      "upstream_hgl_m_msl": 1.4,
      "discharge_status": "TIDAL_LOCKOUT"
    }
  ]
}
```

#### 5. OASIS CAP v1.2 Multilingual Emergency Alert
```bash
curl "http://127.0.0.1:8000/api/alerts/cap?zone=9"
```
*Response Snippet:*
```json
{
  "status": "success",
  "standard": "OASIS CAP v1.2 / ITU-T X.1303",
  "bulletins": {
    "citizen_sms_en": "GCC FLOOD ADVISORY [Zone 9]: Severe waterlogging (58cm) at Duraisamy Subway & Usman Road. Use arterial diversions. Emergency Helpline: 1913.",
    "citizen_sms_ta": "சென்னை மாநகராட்சி வெள்ள எச்சரிக்கை [மண்டலம் 9]: துரைசாமி சுரங்கப்பாதை & உஸ்மான் சாலையில் கடுமையான வெள்ளப்பெருக்கு (58cm). மாற்றுப்பாதையை பயன்படுத்தவும். உதவிக்கு: 1913."
  }
}
```

---

## Repository Directory Structure

```
Smart-India-Hackathon-2026/
|-- ai_service/                           # Core Python AI & Hydrodynamic Microservice
|   |-- orchestration/                    # Master Multi-Layer Coupling Engine
|   |   |-- __init__.py
|   |   |-- coupler.py                    # Legacy baseline orchestrator
|   |   +-- master_coupler.py             # ★ Master 5-Layer Coupler (152 ms full twin)
|   |
|   |-- layer0/                           # Layer 0: Radar Nowcasting & Sensor Mesh
|   |   |-- ingestion.py                  # Live IMD radar scraper & AWS poller
|   |   |-- calibrator.py                 # Brandes & Kriging (KED) gauge-radar calibration
|   |   |-- nowcaster.py                  # Farneback semi-Lagrangian optical flow
|   |   |-- disaggregator.py              # Mass-conservative street downscaler
|   |   |-- cml_mesh.py                   # ★ ITU-R P.838 Telecom CML Rain Mesh
|   |   +-- pipeline.py                   # Layer 0 pipeline orchestrator
|   |
|   |-- layer1/                           # Layer 1: DEM Micro-Topography & Soil Infiltration
|   |   |-- dem/dem_builder.py            # Cartosat-1 10m DEM hydrologic processor
|   |   +-- lulc/runoff_generator.py      # Sentinel-2 SCS-CN runoff generator
|   |
|   |-- layer2/                           # Layer 2: 1D Subsurface Conduit Hydraulics
|   |   |-- conduit_flow.py               # Manning open-channel pipe hydraulics
|   |   |-- clogging_model.py             # Solid waste choking model
|   |   |-- coastal_boundary.py           # ★ Bay of Bengal Tidal & Holland Surge
|   |   +-- pipeline.py                   # Layer 2 pipeline orchestrator
|   |
|   |-- layer3/                           # Layer 3: Physics-Informed Topological Graph Surrogate & Street Hydraulics
|   |   |-- surrogate_model.py            # Physics-Informed Physics-Informed Topological Graph Surrogate
|   |   |-- street_conveyance.py          # ★ Street-as-Canal Conveyance (v x d hazard)
|   |   +-- pipeline.py                   # Layer 3 pipeline orchestrator
|   |
|   |-- layer4/                           # Layer 4: Tactical Clearance & Public Safety
|   |   |-- routing_engine.py             # Flood-aware A* emergency vehicle routing
|   |   |-- pump_optimizer.py             # ★ Automated Municipal Pump Dispatch
|   |   |-- cap_emitter.py                # ★ OASIS CAP v1.2 Multilingual Alerts
|   |   +-- service.py                    # Layer 4 coordination service
|   |
|   |-- tests/                            # Automated Unit & Integration Test Suites
|   |   |-- test_master_coupler.py        # ★ 5-Layer Coupler integration verification
|   |   |-- test_tactical_addons.py       # ★ Tactical add-ons verification
|   |   |-- test_street_conveyance.py     # ★ Manning street flow & hazard tier tests
|   |   +-- layer0/ ... layer4/           # Layer-specific deep unit test suites
|   |
|   +-- api.py                            # FastAPI REST Microservice & Static Web Bridge
|
|-- backend/                              # Node.js API Gateway & State Bridge
|-- Frontend/                             # Tactical React + Vite GIS Command Dashboard
|-- frontend/                             # Tactical Leaflet Command Digital Twin (Static)
|
|-- install_dependencies.sh               # 1-Click Dependency Installer (Linux/WSL/macOS)
|-- install_dependencies.bat              # 1-Click Dependency Installer (Windows)
|-- launch_system.sh                      # 1-Click Complete System Launcher
|-- requirements.txt                      # Pinned Python dependencies
+-- README.md                             # Project Documentation
```

---

## Quick Start & CLI Verification

### 1. Environment Setup

Activate the virtual environment and verify dependencies:

```bash
# Clone the repository
git clone https://github.com/Yashwanth-N17/Smart-India-Hackathon-2026.git
cd Smart-India-Hackathon-2026

# Activate Python Virtual Environment
source .venv/bin/activate    # Linux / macOS / WSL
# or: .venv\Scripts\activate # Windows PowerShell / CMD

# Install dependencies (if not using pre-configured venv)
pip install -r requirements.txt
```

### 2. Run the Master 5-Layer Coupler (CLI)

Execute all 5 layers end-to-end on simulated or real storm events:

```bash
# Run baseline Cyclone Michaung storm scenario
python -m ai_service.orchestration.master_coupler --scenario michaung

# Run severe cyclonic event with custom solid waste clogging and storm surge
python -m ai_service.orchestration.master_coupler \
    --scenario michaung \
    --clogging 0.50 \
    --tide-surge 1.20 \
    --cloudburst 110.0
```

*Sample CLI Output:*
```
===========================================================================
      KAIROS MASTER 5-LAYER DIGITAL TWIN ORCHESTRATOR
      Scenario: MICHAUNG | Clogging: 0.5 | Surge: 1.2m
===========================================================================

[EXECUTION SUMMARY]
  ✓ Total Pipeline Runtime:         152.4 ms
  ✓ Active Road Corridors:          7,894 segments
  ✓ Peak Inundation Depth (T+60m):  136.2 cm
  ✓ Inundated Corridors (>=10cm):   1,842 corridors
  ✓ Critical Impassable (>=30cm):   412 corridors
  ✓ Coastal Outfalls Locked:        2 outfalls
  ✓ Mobile Pumps Dispatched:        5 high-capacity units
  ✓ Street-as-Canal Fast Channels:  2,618 corridors

===========================================================================
          TOP MUNICIPAL DE-WATERING PUMP DISPATCH SITES
===========================================================================
  [Priority 1] Usman Road Underpass (T. Nagar) (Zone 9)
      Depth: 64.0 cm | Unit: Mobile Diesel Trash Pump (150 HP)
      Required Capacity: 800.0 m³/hr | Action: Deploy Mobile Diesel Trash Pump (150 HP) before T+60m
  [Priority 2] Vyasarpadi Ganesapuram Subway (Zone 4)
      Depth: 95.0 cm | Unit: High-Discharge Submersible Pump
      Required Capacity: 2000.0 m³/hr | Action: Deploy High-Discharge Submersible Pump before T+60m
```

### 3. Automated Testing & Verification

Run the comprehensive test suites verifying the Master Coupler and Tactical Add-Ons:

```bash
# Run Master Coupler and Tactical Add-on Tests
python -m unittest \
    ai_service/tests/test_master_coupler.py \
    ai_service/tests/test_tactical_addons.py \
    ai_service/tests/test_street_conveyance.py

# Run Full System Test Suite Across All Layers
python -m unittest discover -s ai_service/tests -p "test_*.py"
```

### 4. Launch the REST API & Tactical Twin Frontend

Start the FastAPI microservice and interactive GIS command dashboards:

```bash
# Start FastAPI backend (http://127.0.0.1:8000)
python -m ai_service.api

# Alternatively, use 1-click launcher for API + Node + Frontend
bash launch_system.sh
```

- **Interactive API Documentation (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Tactical Web GIS Command Twin**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## Team Kairos - SIH 2026

**Smart India Hackathon 2026 | Problem Statement PS 26085**  
*Ministry of Earth Sciences (MoES) & National Centre for Medium Range Weather Forecasting (NCMRWF)*

| Member Name | Role & Specialization |
|---|---|
| **Yashwanth N** | **Team Lead** & AI / Hydrodynamic Systems Architect |
| **Gagan K S** | Full-Stack GIS & UI/UX Systems Engineer |
| **Rithesh** | Hydrologic & Atmospheric Data Engineer |
| **Vijay** | Hydraulic Graph & Network Algorithm Engineer |
| **Raksha** | Backend Microservices & API Integration Engineer |
| **Vaishnavi** | Quality Assurance & Disaster Protocol Engineer |

---

*Engineered with precision for Chennai's flood resilience.*
