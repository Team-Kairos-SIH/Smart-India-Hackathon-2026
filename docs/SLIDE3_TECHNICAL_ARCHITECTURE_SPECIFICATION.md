# SLIDE 3: TECHNICAL APPROACH & SYSTEM ARCHITECTURE
## 6-Stage Coupled Hydro-Meteorological Nowcasting Pipeline
**Problem Statement #26085:** Urban Flood Nowcasting System (Coupled Drainage & Rainfall)  
**Nodal Ministry:** Ministry of Earth Sciences (MoES) / NCMRWF  
**Pilot Domain:** Greater Chennai Corporation (GCC) — 7,894 Road Segments, 1,894 km SWD Network  

---

### Slide Header & Banner
* **Main Title:** `TECHNICAL APPROACH & SYSTEM ARCHITECTURE`
* **Subtitle:** *KAIROS: Coupled Radar Ingestion to Subsurface Hydraulics and Street Depth Nowcasting*
* **Top Header Badges:** `MoES / NCMRWF` | `SIH 2026 Grand Finale` | `Team Kairos`

---

## The 6-Stage Architectural Pipeline

```
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│  01. Rainfall Input     │ ──> │  02. Surface Runoff     │ ──> │  03. Subsurface Conduit │
│      & Nowcasting       │     │      & Connectivity     │     │      Hydraulics         │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
             │                                                               │
             v                                                               v
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│  06. Model Validation   │ <── │  05. Tactical Decision  │ <── │  04. Street Inundation  │
│      & Feedback Loop    │     │      Support & Routing  │     │      Depth Engine       │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
```

---

### 🔹 Stage 01: Rainfall Input & Nowcasting
> *"Turn radar data into actionable rainfall."*

* **IN (Data Ingestion):**
  * Primary: IMD Doppler Weather Radar (10-minute polar S-band sweeps).
  * Calibration: 82 AWS Automatic Rain Gauges & Telecom Microwave Link (CML) mesh.
  * Fallback: NCMRWF Unified Model & GPM Satellite Precipitation.
* **DO (Processing & Algorithms):**
  * Marshall-Palmer $Z\text{--}R$ empirical inversion: $Z = 200 R^{1.6}$.
  * Spatial quality control and 2D-Var Kalman multi-sensor data fusion.
  * PySTEPS semi-Lagrangian optical flow advection nowcasting.
* **OUT (Outputs):**
  * Calibrated, high-resolution precipitation field ($1\text{ km}$ downscaled to road mesh).
  * 0–3 Hour probabilistic rainfall nowcast at 10-minute intervals ($T+10\text{m}$ to $T+180\text{m}$).

---

### 🔹 Stage 02: Surface Runoff & Drainage Connectivity
> *"From rainfall to surface runoff."*

* **IN (Topography & Catchments):**
  * ISRO Cartosat-1 10m Digital Elevation Model (DEM).
  * High-resolution Sentinel-2 Land Use / Land Cover (LULC) and Soil Hydrologic Group data.
  * Greater Chennai Corporation stormwater drain (SWD) centerline vectors (1,894 km).
* **DO (Processing & Hydrology):**
  * Wang & Liu priority-queue depression filling and SWD stream-burning.
  * Soil Conservation Service Curve Number (SCS-CN) infiltration dynamics.
  * Modified Rational Overland Runoff generation ($C_{\text{impervious}} = 0.92$).
  * D8 multi-direction flow routing & Topographic Wetness Index (TWI): $\ln(a / \tan \beta)$.
* **OUT (Outputs):**
  * Overland inflow hydrograph per drain inlet junction ($m^3/s$).
  * Micro-catchment overland flow routing accumulation paths.

---

### 🔹 Stage 03: Subsurface Conduit Hydraulics & Surcharge
> *"From runoff to subterranean constraints."*

* **IN (Conduit Attributes & Boundary Conditions):**
  * 1,894 km SWD pipe geometries, conduit cross-sections, and invert slopes.
  * **Dynamic Solid Waste Clogging Factor ($\mu_{\text{clog}}$)** parameterized via GCC ward solid waste tonnage (TPD) and 1913 grievance records.
  * Real-time INCOIS coastal astronomical tide and storm surge sea surface height (SSH).
* **DO (Hydraulic Modeling):**
  * 1D Saint-Venant dynamic wave routing engine (PySWMM multigraph).
  * Dynamic conduit conveyance throttling: $A_{\text{eff}} = A_0(1 - \mu_{\text{clog}}), \quad n_{\text{eff}} = n_0(1 + 1.8\mu_{\text{clog}})$.
  * **Pressurized reverse manhole surcharge modeling ($HGL > Z_{\text{ground}}$)**:
    $$Q_{\text{backflow}} = C_d A_{\text{lid}} \sqrt{2g(HGL - Z_{\text{ground}})}$$
  * Tidal backpressure locking at coastal outfalls (Cooum, Adyar, Buckingham Canal).
* **OUT (Outputs):**
  * Pressurized reverse surcharge discharge ($m^3/s$) per manhole junction.
  * Subsurface pipe Hydraulic Grade Line (HGL) profile.
* **Bottom Physical Callout:** *"Tidal backpressure & solid waste siltation zeroes outfall capacity when sea tide level exceeds conduit invert."*

---

### 🔹 Stage 04: Street Inundation Depth Engine
> *"From subterranean backflow to street depths."*

* **Depth Classification Legend:**
  * 🟢 **Low:** $< 10\text{ cm}$ (Safe for all vehicles)
  * 🟡 **Moderate:** $10\text{--}30\text{ cm}$ (Caution; small vehicle wading limit)
  * 🔴 **High:** $30\text{--}45\text{ cm}$ (Ambulance critical limit; only heavy trucks)
  * 🟣 **Critical:** $> 45\text{ cm}$ (Completely impassable; active drowning hazard)
* **IN (Hydrodynamic Forcing):**
  * Pressurized manhole surcharge discharge vectors from Stage 03.
  * Pre-computed Cartosat-1 DEM depression storage basins and street cross-sections.
  * Greater Chennai Corporation 7,894 road network centerline segments.
* **DO (Deep Hydrodynamic Surrogate):**
  * **Physics-Informed Graph Neural Network (PI-GNN) Surrogate** trained on 2D Saint-Venant equations with strict fluid mass conservation penalty ($\Delta M < 0.1\%$).
  * Topographic mass-conservative depression pooling.
  * **Sub-second metropolitan execution ($< 350\text{ ms}$)** vs 3–5 hours for classical 2D hydrodynamic solvers.
* **OUT (Outputs):**
  * **Exact Street Water Depth ($d_{\text{cm}}$) for all 7,894 road segments**.
  * Dynamic 15-minute inundation evolution time-series (0 to 180 min).

---

### 🔹 Stage 05: Tactical Decision Support & Evacuation
> *"From street depths to actionable rescue."*

* **4 Visual Feature Panels:**
  * 🚨 Civic Warnings | 🚑 Safe Emergency Routes | 🖥️ Tactical Web GIS Twin | ⚡ Critical Infrastructure Monitor
* **IN (Decision Forcing):**
  * 7,894 street water depth vectors from Stage 04.
  * Vehicle-specific physical wading exhaust thresholds (Ambulance: 30cm, NDRF Truck: 45cm, Bus: 45cm, Car: 18cm).
  * TANGEDCO 110kV/230kV electrical substation coordinates and plinth heights ($P_{\text{elevation}}$).
* **DO (Tactical Operations & Routing):**
  * **Time-Dependent Dynamic A\* Safe Navigation** utilizing Water Hazard Potential Fields (WHPF):
    $$C_{\text{hazard}} = t_{\text{travel}} \cdot \left(1 + \alpha \left(\frac{d}{d_{\text{clearance}}}\right)^4\right)$$
  * **Underpass Flash-Flood 15-Minute Crest Lookahead** (predicts subway traps before vehicle arrival).
  * **Plinth Vulnerability Index (PVI)** for pre-emptive power cut-off alerts.
* **OUT (Outputs):**
  * Turn-by-turn flood-safe emergency dispatch corridors.
  * Real-time Web GIS Command Twin (Leaflet / MapLibre with 15-minute time slider).
  * Automated 60-minute advance warnings for TANGEDCO electrical substations and medical depots.

---

### 🔹 Stage 06: Model Validation & Ground-Truth Feedback
> *"Ground-truth calibration & continuous learning."*

* **4 Feedback Channels:**
  * 📞 GCC 1913 Grievance Logs | 🌧️ AWS Gauges | 🌊 Michaung Hindcasts | 🔄 Automated Tuning
* **IN (Ground-Truth Datasets):**
  * Greater Chennai Corporation 1913 civic waterlogging complaint records (12,400+ entries).
  * 82 IMD Automatic Weather Station (AWS) tipping-bucket records.
  * Ground inundation survey marks from **Cyclone Michaung (Dec 2023 - 450 mm deluge)**.
* **DO (Feedback & Verification):**
  * Hydrodynamic residual error calculation and spatial bias-correction.
  * Dynamic roughness parameter ($n$) and infiltration capacity updating.
  * Automated regression verification across **200 / 200 automated pytest integration tests**.
* **OUT (Outputs):**
  * Calibrated physical model parameters continuously fed back to Stage 01 and Stage 03.
  * Auditable mathematical confidence interval for every forecasted road segment.

---

### 🔹 Production Tech Stack Bar

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ TECH STACK:  Python 3.12  |  PySTEPS  |  PyTorch (PyG)  |  PySWMM  |  NetworkX  |  FastAPI  |  Leaflet │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
