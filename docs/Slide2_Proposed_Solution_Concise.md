# SLIDE 2 — PROPOSED SOLUTION & NOVELTY (CLEAN & GENERALIZED)
## Team KAIROS · SIH 2026 · PS #26085 · JSS011
### Generalized Master Blueprint: Universal Municipal Terminology & Clean Headers

---

## 📐 CONCISE VISUAL SLIDE LAYOUT (Universal & Pan-India)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HEADER: PROPOSED SOLUTION — Urban Flood Nowcasting Digital Twin | PS #26085                  [SIH 2026 LOGO]    │
│ Sub-Badge: 250 mm / 24h Cloudburst Event — Airport shut, fatalities, ambulances had zero flood-depth routing     │
├─────────────────────────────────────┬────────────────────────────────────────────────────────────────────────────┤
│ PROBLEM                             │ PROPOSED SOLUTION PIPELINE                                                 │
│ Why current systems fall short      │ Urban Flood Nowcasting Digital Twin                                        │
│                                     │                                                                            │
│ 01 Micro-Topography Matters         │ 📡 Doppler Radar         🏔️ Terrain Runoff      🕳️ Drain Hydraulics    📍 Street Intelligence │
│ • Water does not flow uniformly     │    (0-3h Rain Ingestion)    (Cartosat DEM Mesh)    (1D SWMM Model)      (Real-Time Flood Map) │
│ • Underpass sags & low points       │ • Doppler radar sweeps  • 5m Cartosat bare DEM• Municipal drain mesh • Street depth (cm)   │
│ • Same rain → different flood depths│ • Z-R reflectivity      • Flow accumulation    • Clogging factor μ  • 0-3h forecast       │
│                                     │ • Multi-sensor fallback • Hydro-trench (-2.5m) • Torricelli geysers • Risk map & safe route│
│ 02 Drainage Network Limitations     │                                                                            │
│ • Drains choked with plastic/silt   ├────────────────────────────────────────────────────────────────────────────┤
│ • Models assume clean pipes (μ = 0) │ UNIQUENESS OF OUR SOLUTION                                                 │
│ • Surcharge causes manhole geysers  │                                                                            │
│                                     │ ♾️ Blockage-Aware      📡 Multi-Radar Fallback   🚑 Arrival-Time Route   ⚡ Plinth Safeguard  │
│ 03 Lack of Actionable Info          │    Clogging μ in [0.05,0.85] P1 Radar → P2 AWS      4 Vehicle Profiles     15 cm Plinth Rule    │
│ • District alerts are too broad     │    replaces clean pipes  → P3 CML fallback      30-min subway lookahead Protects Substations │
│ • No street-level flood depth (cm)  │                                                                            │
│ • Responders need 0-3h lead time    │                                                                            │
├─────────────────────────────────────┴────────────────────────────────────────────────────────────────────────────┤
│ FROM: ☁️  "City will receive 85 mm rainfall today."  ➔ TO: 📍 "Central Railway Underpass floods to 48 cm in 35 mins│
│           (Passive Weather Forecast)                              — Divert 108 Ambulance via Arterial Ring Road."  │
│                                                                   (Actionable Emergency Command)                   │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ BOTTOM METRICS BAR:  Inference Latency: < 28.5 ms on CPU  |  Mass Error ≤ 0.000089%  |  7,894 Streets  |  ₹0 Capex  │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 EXACT COPY-PASTE CONTENT (Organized by Box)

---

### 🔴 BOX 1: PROBLEM — Why Current Systems Fall Short (Left Column)

#### 01 Micro-Topography Matters
* Water does not flow uniformly across urban catchments.
* Railway underpass sags and low-lying roads create immediate flash-points.
* Same rainfall volume $\rightarrow$ drastically different street flood depths.

#### 02 Drainage Network Limitations
* Municipal storm drains are heavily silted and plastic-clogged in monsoon reality.
* Standard weather models assume pristine, textbook open conduits ($\mu = 0$).
* Hydraulic surcharge causes pressurized manhole geysers erupting onto streets (~$390\text{ L/s}$).

#### 03 Lack of Actionable Information
* District-level rain alerts (Red/Orange) are too broad and offer zero street depth.
* Emergency responders lack 0–3 hour predictive lead time.
* Authorities need exact street water depth ($d_{\text{cm}}$) to navigate safe corridors.

---

### 🔵 BOX 2: PROPOSED SOLUTION PIPELINE (Top Right)

#### 1. Multi-Sensor Rain Ingestion (Layer 0)
* **Doppler Weather Radar sweeps** ($10\text{-min}$ cadence).
* **Multi-sensor calibration:** Automatic Rain Gauges (AWS) + Telecom Microwave Links (CML backhaul).
* **Optical flow nowcaster:** 6 forecast horizons ($T+15\text{m}$ to $T+180\text{m}$).

#### 2. Terrain & Surface Runoff (Layer 1)
* **Cartosat 5m bare-earth DEM** hydro-conditioned with $-2.5\text{m}$ culvert trenching.
* **SCS-CN Infiltration & Modified Rational Runoff:** $C_{\text{impervious}} = 0.92$.
* Identifies micro-catchment flow accumulation and low-lying sag basins.

#### 3. Underground Drainage Hydraulics (Layer 2)
* **Municipal stormwater drain multigraph** (conduits, box culverts, open canals).
* **Dynamic solid waste clogging factor $\mu \in [0.05, 0.85]$** parameterized from municipal waste logs.
* **Torricelli orifice surcharge solver:** $Q_{\text{backflow}} = C_d A_{\text{lid}} \sqrt{2g(\text{HGL} - Z_{\text{ground}})}$.

#### 4. Street-Level Intelligence Map (Layers 3 & 4)
* **PI-GNN Surrogate + Convex Mass QP:** Computes exact street depth ($d_{\text{cm}}$) across city streets.
* **Execution latency:** **< 28.5 ms on CPU** ($120,000\times$ faster than 2D SWE solvers).
* Serves dynamic risk maps and turn-by-turn safe emergency routing APIs.

---

### 🟡 BOX 3: UNIQUENESS OF OUR SOLUTION (Middle Right — 4 Pill Cards)

#### ♾️ 1. Blockage-Aware Drain Clogging
* Replaces the "clean pipe illusion" ($\mu = 0$). Computes live clogging factor $\mu \in [0.05, 0.85]$ from municipal desilting & waste logs.

#### 📡 2. Multi-Radar Fallback Circuit
* Solves live radar downtime. Fuses Radar $\to$ Rain Gauges (AWS) $\to$ Telecom Microwave Links (CML) with automatic failover.

#### 🚑 3. Arrival-Time Emergency Routing
* Evaluates water depth at projected vehicle arrival time across 4 wading clearance profiles (10cm Bike, 18cm Car, 30cm Ambulance, 45cm NDRF Truck) with **30-minute underpass lookahead**.

#### ⚡ 4. Critical Infrastructure Plinth Safeguard
* Enforces the **15 cm Plinth Margin Rule** ($\Delta Z_{\text{plinth}} \le 15\text{ cm}$) to protect electrical substations and hospital medical O₂ plants from blackout cascades.

---

### ↔️ BOX 4: PARADIGM SHIFT BANNER (Bottom Full-Width)

* ☁️ **FROM (Passive Weather Forecast):**
  > *"City will receive 85 mm rainfall today."*
* 📍 **TO (Actionable Emergency Command):**
  > *"Central Railway Underpass will flood to 48 cm in 35 mins — Divert 108 Ambulance via Arterial Ring Road."*

---

### 💻 BOTTOM STATUS STRIP
`Inference Latency: < 28.5 ms on CPU` | `Mass Volume Error: ≤ 0.000089%` | `Coverage: City-Wide Corridors` | `Hardware Capex: ₹0 (Zero New Sensors)`

---

> *Team KAIROS · JSS011 · SIH 2026 PS #26085 · Ministry of Earth Sciences / NCMRWF × Universal Municipal Deployment*
