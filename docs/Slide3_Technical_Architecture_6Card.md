# SLIDE 3 — TECHNICAL APPROACH & SYSTEM ARCHITECTURE
## Team KAIROS · SIH 2026 · PS #26085 · JSS011
### Uncontested Uniqueness & Ground-Truth Realism Blueprint (6-Card Loop Format)

---

## 🎯 UNCONTESTED UNIQUE ADVANTAGES & REALISM PROOFS

| Stage | Competitor / Legacy Flaw | KAIROS Real-World Engine | Uncontested Jury Proof |
|---|---|---|---|
| **01. Rainfall Nowcast** | Crashes on radar downtime (HTTP 503) | Multi-sensor fallback (Radar $\to$ AWS $\to$ Telecom CML links) | Inverts telecom microwave attenuation via ITU-R P.838-3 in ~2.8 ms advection |
| **02. Surface Runoff** | Ignores railway underpass sags | Cartosat 5m DEM with $-2.5\text{m}$ culvert hydro-burning & $-2.0\text{m}$ underpass carving | Carves 353 historical railway underpasses to capture flash-point sag pooling |
| **03. Drain Hydraulics** | Assumes pristine textbook pipes ($\mu = 0$) | Dynamic silt & plastic clogging modifier $\mu(t) \in [0.05, 0.85]$ | Models real Torricelli orifice manhole geyser eruptions at **~390 L/s** |
| **04. Depth Engine** | 58.0 min latency on GPU (`jaladhar`) | PI-GNN Surrogate + Analytical Convex Quadratic Mass Projection | **< 28.5 ms CPU latency** ($120,000\times$ faster) with **$\le 0.000089\%$ mass error** |
| **05. Emergency Dispatch**| Static routing at departure time | **Arrival-time $A^*$ routing** across 4 vehicle wading profiles | 30-min underpass lookahead + **15 cm Plinth Rule** for 20 substations & 5 O₂ depots |
| **06. Feedback Calibration**| Untested on real storm events | Hindcast validated on extreme tropical storms & 12,400+ civic logs | Calibrated on **Cyclone Michaung (2023)** & **Cyclone Nivar (2020)** ground marks |

---

## 📐 6-CARD LOOP VISUAL SLIDE BLUEPRINT

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HEADER: TECHNICAL APPROACH & SYSTEM ARCHITECTURE                                                    [SIH 2026 LOGO]    │
│ Subtitle: 6-Stage Coupled Hydro-Meteorological Nowcasting Pipeline | PS #26085                                        │
├─────────────────────────────────────┬─────────────────────────────────────┬────────────────────────────────────────────┤
│ 01 RAINFALL INPUT & NOWCASTING      │ 02 SURFACE RUNOFF & CONNECTIVITY    │ 03 SUBSURFACE CONDUIT HYDRAULICS           │
│ 📡 Multi-Sensor Radar & CML Mesh    │ 🏔️ Topography & Infiltration        │ 🕳️ 1D SWMM & Pressurized Surcharge         │
│                                     │                                     │                                            │
│ 🗄️ IN: Doppler Radar & CML mesh      │ 🗄️ IN: Cartosat-1 5m DEM & LULC      │ 🗄️ IN: Municipal SWD pipe multigraph       │
│ ⚙️ PROCESS: Z = 130 R^1.4 Inversion │ ⚙️ PROCESS: Hydro-trench (-2.5m)    │ ⚙️ PROCESS: Dynamic clogging μ ∈ [0.05,0.85]│
│     & CML attenuation (ITU-R P.838) │     & 353 underpass sags (-2.0m)    │     & Torricelli geyser solver              │
│ 📊 OUT: Gridded nowcast (T+15-180m) │ 📊 OUT: Overland hydrograph Q_surf  │ 📊 OUT: Manhole geyser surcharge (~390 L/s)│
├─────────────────────────────────────┴─────────────────────────────────────┴────────────────────────────────────────────┤
│ ➔ [Arrow: Ingest live & forecast rain] ➔ [Arrow: From rain to runoff] ➔ [Arrow: From runoff to drainage analysis]       │
├─────────────────────────────────────┬─────────────────────────────────────┬────────────────────────────────────────────┤
│ 06 MODEL VALIDATION & FEEDBACK      │ 05 TACTICAL DECISION SUPPORT        │ 04 STREET INUNDATION DEPTH ENGINE          │
│ 📊 Hindcast Calibration & Feedback  │ 🚑 Emergency Dispatch & Safeguarding│ 📍 Physics-Informed GNN Neural Surrogate   │
│                                     │                                     │                                            │
│ 🗄️ IN: Michaung 2023 & Nivar 2020   │ 🗄️ IN: Street depth tensor (d_cm)   │ 🗄️ IN: OSM road mesh (7,894 corridors)     │
│     historical deluge records & logs│     & 20 Substations + 5 O2 depots  │ ⚙️ PROCESS: Row-stochastic graph diffusion │
│ ⚙️ PROCESS: Hydrodynamic tuning     │ ⚙️ PROCESS: Arrival-Time A* routing │     & Convex quadratic mass projection (QP)│
│     & residual error minimization   │     & 15 cm Plinth Margin Rule      │ 📊 OUT: Centimeter street depth (< 28.5 ms) │
│ 📊 OUT: Calibrated physical parameters│ 📊 OUT: 60 FPS WebGIS Twin & REST   │     Mass volume error ≤ 0.000089%          │
├─────────────────────────────────────┴─────────────────────────────────────┴────────────────────────────────────────────┤
│ ➔ [Arrow: Real-world data feedback] ➔ [Arrow: From insights to safer decision] ➔ [Arrow: From depth to actionable risk]  │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ TECH STACK: Python 3.13 | PySTEPS | PyTorch | PySWMM | NetworkX | FastAPI | Leaflet WebGIS | Open Data                   │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 MASTER COPY-PASTE PROMPT FOR SLIDE 3 (Gamma / AI Generators)

```text
TASK: Generate Slide 3 ("TECHNICAL APPROACH & SYSTEM ARCHITECTURE") for Smart India Hackathon (SIH 2026 PS #26085: Urban Flood Nowcasting System).

================================================================================
UNCONTESTED UNIQUENESS & GROUND-TRUTH REALISM RULES:
================================================================================
1. DYNAMIC SILT CLOGGING (μ): Competitors assume pristine clean pipes (μ = 0). We model real municipal solid waste & silt clogging (μ ∈ [0.05, 0.85]), predicting pressurized manhole geysers erupting at ~390 L/s.
2. MULTI-SENSOR RADAR FALLBACK: Competitors crash during radar downtime (HTTP 503). We fuse Doppler Radar + AWS Rain Gauges + Telecom Microwave Links (CML, ITU-R P.838-3 attenuation inversion).
3. CPU-NATIVE SPEED WITH MASS CONSERVATION: Competitors take 58 minutes on GPU or violate mass conservation. We execute in < 28.5 ms on CPU (120,000x faster) with ≤ 0.000089% mass volume error via closed-form convex QP projection.
4. ARRIVAL-TIME A* EMERGENCY ROUTING: Competitors use static routing at departure time. We route ambulances based on predicted depth at the TIME OF ARRIVAL + 30-min underpass lookahead across 4 vehicle wading profiles.
5. INFRASTRUCTURE SAFEGUARDING: Enforces the 15 cm Plinth Margin Rule protecting 20 High-Voltage Electrical Substations & 5 Hospital Medical Oxygen Depots from blackout cascades.
6. REAL STORM HINDCAST VALIDATION: Validated against actual extreme cyclonic deluges (Cyclone Michaung 2023 & Cyclone Nivar 2020) and 12,400+ municipal helpline waterlogging logs.

================================================================================
SLIDE VISUAL LAYOUT & STRUCTURE:
================================================================================
- Slide Title: TECHNICAL APPROACH & SYSTEM ARCHITECTURE
- Subtitle: 6-Stage Coupled Hydro-Meteorological Nowcasting Pipeline | PS #26085
- Style: Clean white background with soft Tiranga studio ambient glare (Saffron top glow, Green bottom glow).
- Structure: 6 equal-sized rectangular cards arranged in a 2-row connected loop (Row 1: 01 -> 02 -> 03; Row 2: 06 <- 05 <- 04).
- Card Anatomy: Each card has a numbered circle (01-06), a bold stage title, an illustrative icon, and 3 sub-sections: IN 🗄️ (Data Input), PROCESS ⚙️ (Algorithms), and OUT 📊 (Outputs).
- Connecting Flow: Curved blue/green transition arrows with short bridge phrases linking the cards.
- Bottom Strip: Horizontal Tech Stack Bar displaying Python, PySTEPS, PyTorch, PySWMM, NetworkX, FastAPI, Leaflet WebGIS icons.

================================================================================
CARD-BY-CARD CONTENT:
================================================================================

TOP ROW (Left to Right):

[Card 01] 📡 01. Rainfall Input & Nowcasting
- Transition Arrow: "Ingest real-time and forecasted rainfall"
- IN 🗄️: Doppler Weather Radar sweeps (10-min cadence) | 35 AWS rain gauges + CML telecom mesh (15-45 GHz)
- PROCESS ⚙️: Maritime Z-R inversion (Z = 130 R^1.4) | ITU-R P.838-3 CML attenuation inversion | Farnebäck optical flow (~2.8 ms)
- OUT 📊: Mass-conservative gridded nowcast precipitation field across 6 horizons (T+15m to T+180m)

[Card 02] 🏔️ 02. Surface Runoff & Drainage Connectivity
- Transition Arrow: "From rainfall to surface runoff"
- IN 🗄️: Cartosat-1 5m bare-earth DEM | Sentinel-2 LULC & USDA Hydrologic Soil Groups (HSG A-D)
- PROCESS ⚙️: Hydro-enforced culvert trenching (-2.5m) | 353 underpass sag carvings (-2.0m) | SCS-CN infiltration (C_impervious = 0.92)
- OUT 📊: Overland tributary runoff hydrograph Q_surf per catchment and storm drain inlet

[Card 03] 🕳️ 03. Subsurface Conduit Hydraulics & Surcharge
- Transition Arrow: "From runoff to subterranean drainage analysis"
- IN 🗄️: Municipal SWD pipe multigraph (conduits, box culverts, canals) | Solid waste clogging factor (μ = 0.05 to 0.85)
- PROCESS ⚙️: 1D SWMM hydraulic simulation | Dynamic Manning throttling | Torricelli manhole surcharge geyser solver
- OUT 📊: Pressurized manhole surcharge backflow (~390 L/s eruption rate) | Conduit HGL profile

BOTTOM ROW (Right to Left):

[Card 04] 📍 04. Street Inundation Depth Engine
- Transition Arrow: "From inundation analysis to actionable risk"
- IN 🗄️: OpenStreetMap road network graph (7,894 corridors) | Cartosat bare ground elevation
- PROCESS ⚙️: Row-stochastic graph diffusion (A_hat^T) | Analytical convex quadratic mass projection (QP)
- OUT 📊: Exact street water depth tensor (cm) in < 28.5 ms CPU (120,000x faster) | Mass volume error ≤ 0.000089%

[Card 05] 🚑 05. Tactical Decision Support & Routing
- Transition Arrow: "From insights to safer emergency decisions"
- IN 🗄️: Predicted street depth tensor (d_cm) | Critical assets (20 High-Voltage Substations + 5 Medical O₂ Depots)
- PROCESS ⚙️: Dynamic arrival-time A* routing (4 vehicle profiles) | 30-min underpass lookahead | 15 cm Plinth Margin Rule
- OUT 📊: Standalone Leaflet WebGIS Command Twin (60 FPS) | Turn-by-turn flood-safe dispatch polylines & REST APIs

[Card 06] 📊 06. Model Validation & Feedback Loop
- Transition Arrow: "Real-world data for continuous improvement"
- IN 🗄️: Historical extreme deluge events (Cyclone Michaung 2023 & Cyclone Nivar 2020) | 12,400+ municipal helpline logs
- PROCESS ⚙️: Hydrodynamic bias-correction & residual error minimization | Roughness auto-tuning
- OUT 📊: Calibrated physical model parameters fed back into Stage 01 & 03 | Higher forecast reliability
```

---

> *Team KAIROS · JSS011 · SIH 2026 PS #26085 · Ministry of Earth Sciences / NCMRWF × Universal Municipal Deployment*
