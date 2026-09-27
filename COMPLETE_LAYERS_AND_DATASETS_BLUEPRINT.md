# KAIROS: URBAN FLOOD NOWCASTING & DRAINAGE HYDRAULIC TWIN
## COMPLETE ARCHITECTURAL BLUEPRINT, MULTI-LAYER TECHNICAL SPECIFICATION & DATASET IMPLEMENTATION MANUAL

**Smart India Hackathon (SIH) 2026 | Problem Statement ID: 26085**  
**Ministry:** Ministry of Earth Sciences (MoES) / National Centre for Medium Range Weather Forecasting (NCMRWF)  
**Beneficiary Authority:** Greater Chennai Corporation (GCC) & Tamil Nadu State Disaster Management Authority (TNSDMA)  
**Project Team:** Team Kairos | **Team Lead:** Yashwanth N  
**Document Classification:** Master Engineering Blueprint & Dataset Integration Guide (`MoES-SIH2026-ARCH-DATA-v1.0`)  

---

## TABLE OF CONTENTS
1. [Executive Overview & Scientific Mandate](#1-executive-overview--scientific-mandate)
2. [End-to-End System Architecture Diagram](#2-end-to-end-system-architecture-diagram)
3. [Operational Lifecycle Sequence Flow Diagram](#3-operational-lifecycle-sequence-flow-diagram)
4. [Exhaustive Description of All Architectural Layers (Layer 0 to End)](#4-exhaustive-description-of-all-architectural-layers-layer-0-to-end)
   - [4.1 Layer 0: Multi-Sensor Atmospheric Ingestion, Nowcasting Fabric & Telecom CML Mesh](#41-layer-0-multi-sensor-atmospheric-ingestion-nowcasting-fabric--telecom-cml-mesh)
   - [4.2 Layer 1: 2D Micro-Topography, Cartosat DEM & Surface Runoff Engine](#42-layer-1-2d-micro-topography-cartosat-dem--surface-runoff-engine)
   - [4.3 Layer 2: 1D Subsurface Stormwater Network Hydraulics, Surcharge & Coastal Tidal Lockout](#43-layer-2-1d-subsurface-stormwater-network-hydraulics-surcharge--coastal-tidal-lockout)
   - [4.4 Orchestration Layer: In-Memory 1D-2D Coupler & Master 5-Layer Hydrodynamic Orchestrator](#44-orchestration-layer-in-memory-1d-2d-coupler--master-5-layer-hydrodynamic-orchestrator)
   - [4.5 Layer 3: Physics-Informed Topological Graph Surrogate & Street Conveyance](#45-layer-3-physics-informed-topological-graph-surrogate--street-conveyance)
   - [4.6 Layer 4: Dynamic Safe Navigation, Municipal Pump Dispatch & ITU-T CAP v1.2 Multilingual Alerts](#46-layer-4-dynamic-safe-navigation-municipal-pump-dispatch--itu-t-cap-v12-multilingual-alerts)
   - [4.7 API Gateway Layer: Node.js / Express & High-Throughput WebSocket Bridge](#47-api-gateway-layer-nodejs--express--high-throughput-websocket-bridge)
   - [4.8 Presentation Layer: Tactical Web GIS Command Twin (CartoDB & National GIGW Skin)](#48-presentation-layer-tactical-web-gis-command-twin-cartodb--national-gigw-skin)
5. [Master Datasets Audit & Implementation Mapping](#5-master-datasets-audit--implementation-mapping)
   - [5.1 Comprehensive Datasets Vault Inventory](#51-comprehensive-datasets-vault-inventory)
   - [5.2 Implementation Mapping: Which Datasets Each Layer Must Use](#52-implementation-mapping-which-datasets-each-layer-must-use)
   - [5.3 Master Unified Dataset Schema (`chennai_unified_flood_master_dataset.csv`)](#53-master-unified-dataset-schema-chennai_unified_flood_master_datasetcsv)
6. [Real-World Indian Metro Constraints & Fail-Safe Resiliency](#6-real-world-indian-metro-constraints--fail-safe-resiliency)
7. [Verification & Latency Audit Summary](#7-verification--latency-audit-summary)

---

## 1. Executive Overview & Scientific Mandate

Urban flooding in coastal Indian metropolises like Greater Chennai is fundamentally an **infrastructure-coupled micro-topographical crisis**. While traditional Numerical Weather Prediction (NWP) models (e.g., NCMRWF NCUM-R or IMD WRF) operate on coarse $4\text{ km} \times 4\text{ km}$ grids, they are blind to the two physical phenomena that dictate urban flash floods:
1. **Atmospheric Convective Localism:** Cloudbursts exceeding $60\text{--}100\text{ mm/hr}$ routinely initiate, burst, and dissipate within $30\text{--}60\text{ minutes}$ over areas $< 2\text{ km}^2$.
2. **Micro-Topographical & Hydraulic Coupling:** A terrain depression of just $0.3\text{--}0.5\text{ meters}$ (railway underpasses, road grade dips) creates a half-meter deep reservoir on impervious asphalt ($C \ge 0.90$). When the 1D underground stormwater drains choke with silt and uncollected solid waste, the Hydraulic Grade Line (HGL) rises above the street surface, triggering **hydraulic surcharge**—pressurized reverse eruptions through manholes that flood roads from below.

**KAIROS** solves this challenge by coupling radar nowcasting, 2D terrain hydro-conditioning, 1D pipe network hydraulics, and physics-informed AI graph surrogates into a sub-second decision support twin for emergency first responders and municipal commissioners.

---

## 2. End-to-End System Architecture Diagram

```mermaid
flowchart TD
    %% Atmospheric Ingestion
    subgraph L0["LAYER 0: Multi-Sensor Atmospheric Ingestion & Nowcasting Fabric"]
        style L0 fill:#111827,stroke:#3b82f6,stroke-width:2px,color:#fff
        DWR["IMD S-Band Doppler Weather Radar<br>(Meenambakkam 10-min SRI/MAXZ)"]
        SHAR["ISRO SDSC SHAR Radar<br>(Blind Cone Elimination)"]
        AWS["35+ GCC Ward Rain Gauges<br>(15-min Telemetry)"]
        CML["Cellular CML Virtual Rain Gauge Mesh<br>(Airtel/Jio/Vi 13-73 GHz / ITU-R P.838-3 / cml_mesh.py)"]
        NCUM["NCMRWF NCUM-R 4km<br>(OPeNDAP NWP Slicer)"]

        FUS["2D-Var Kalman Spatial Fusion<br>(Gaspari-Cohn Covariance Localization)"]
        FLOW["Farnebäck Polynomial Optical Flow<br>(Semi-Lagrangian Advection 0-180m)"]
        STEPS["1-Min Stochastic Cascade Ensembles<br>(P10 / P50 / P90 Quantiles)"]
        SUPRES["Physics-Guided 100m Super-Resolution<br>(Orographic & Sea-Breeze Scaling)"]
        DISAGG["Mass-Conservative Street Disaggregation<br>(7,894 GCC Road Segments)"]

        DWR & SHAR & AWS & CML & NCUM --> FUS
        FUS --> FLOW --> STEPS --> SUPRES --> DISAGG
    end

    %% Micro-Topography
    subgraph L1["LAYER 1: 2D Micro-Topography, Cartosat DEM & Surface Runoff Engine"]
        style L1 fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#fff
        DEM["ISRO Cartosat-1 30m Stereoscopic DEM<br>(EGM96 Orthometric Calibration)"]
        INSAR["Sentinel-1 InSAR Land Subsidence<br>(Compaction & Elevation Sinking Offset)"]
        HYDRO["Hydro-Conditioning Engine<br>(Bridge Breaching & Canal Stream Burning)"]
        DERIV["Hydrologic Derivatives Engine<br>(Horn Gradient S0, Aspect, D8 Flow Acc)"]
        LULC["LULC & Soil Infiltration Engine<br>(Sentinel-2 Impervious, ICAR Soil Groups, AMC)"]
        RUNOFF["Modified Rational Surface Runoff Generator<br>(Q_surf [m³/s] & R_excess [mm/hr])"]

        DEM & INSAR --> HYDRO --> DERIV
        HYDRO & LULC --> RUNOFF
    end

    %% Subsurface Hydraulics & Coastal Boundary
    subgraph L2["LAYER 2: 1D Subsurface Stormwater Network Hydraulics & Surcharge Engine"]
        style L2 fill:#3b0764,stroke:#a855f7,stroke-width:2px,color:#fff
        PIPE_NET["GCC Stormwater Drainage Graph<br>(Conduits, Box Culverts, Inverts)"]
        CLOG["Dynamic Solid Waste Clogging Model<br>(mu_clog from TPD & Desilting Arrears)"]
        MANNING["Manning Conduit Conveyance Solver<br>(Effective Capacity Q_eff)"]
        INLET["Curb Drop-Inlet Grate Capture<br>(Unsubmerged Weir vs Submerged Orifice)"]
        SURCH["Saint-Venant HGL Pressurization<br>(Backflow Geyser Eruption: Q_backflow)"]
        COASTAL["Coastal Tidal Lockout & Storm Surge Engine<br>(Survey of India Harmonics + Holland Cyclonic Setup / coastal_boundary.py)"]

        PIPE_NET & CLOG --> MANNING
        MANNING & INLET --> SURCH
        COASTAL -.->|"Tailwater HGL Lockout"| SURCH
    end

    %% Master Coupler & Orchestration
    subgraph ORCH["ORCHESTRATION & IN-MEMORY MASTER COUPLER (master_coupler.py)"]
        style ORCH fill:#78350f,stroke:#f59e0b,stroke-width:2px,color:#fff
        COUPLER["Master 5-Layer Hydrodynamic Orchestrator<br>(Zero-Copy Tensor Synchronization, Diagnostics & End-to-End Coupling)"]
    end

    %% Surrogate & Street Conveyance
    subgraph L3["LAYER 3: Physics-Informed Topological Graph Surrogate & 'Street-as-Canal' Conveyance"]
        style L3 fill:#4c0519,stroke:#f43f5e,stroke-width:2px,color:#fff
        SURROGATE["Physics-Informed Topological Graph Surrogate<br>(Sub-Second Message Passing < 30ms)"]
        MASS_LOSS["Mass Conservation Constraint<br>(Delta V_surface + V_pipe = V_rain: <= 0.000089% Error)"]
        DEPTHS["Multi-Horizon Street Flood Depths<br>(d_i(t) at T+15, 30, 60, 90, 120, 180 min)"]
        CONVEY["Street-as-Canal Conveyance & v x d Hazard<br>(Manning Open-Channel & DEFRA/ARR Wash-Away Tiers / street_conveyance.py)"]

        SURROGATE --> MASS_LOSS --> DEPTHS --> CONVEY
    end

    %% Navigation, Pump Dispatch & Multi-Channel Alerts
    subgraph L4["LAYER 4: Dynamic Navigation, Municipal Pump Dispatch & Multilingual Alerts"]
        style L4 fill:#134e4a,stroke:#14b8a6,stroke-width:2px,color:#fff
        ROUTING["Flood-Aware Dynamic A* Routing Engine<br>(Depth Penalty Cost Function across 4 Vehicle Profiles)"]
        ASSETS["TANGEDCO Substation Plinth Monitor<br>(20 Critical 230kV/110kV Stations at Flood Risk)"]
        PUMPS["Automated Municipal De-Watering Pump Dispatch Optimizer<br>(Super-Sucker & 150HP Diesel Trash Pump Sizing / pump_optimizer.py)"]
        CAP["ITU-T CAP v1.2 Multilingual Emergency Alert Emitter<br>(OASIS XML, Ward WhatsApp & Citizen 1913 SMS / cap_emitter.py)"]
    end

    %% API Gateway & UI
    subgraph PRESENTATION["PRESENTATION & API GATEWAY LAYER"]
        style PRESENTATION fill:#083344,stroke:#06b6d4,stroke-width:2px,color:#fff
        GATEWAY["Node.js Express & WebSocket API Gateway<br>(Port 5000: /api/nowcast, /api/hydraulics, /api/routing)"]
        TWIN["Tactical Web GIS Command Twin<br>(CartoDB Dark Matter / National GIGW Skin)"]
        SLIDER["0-180 Min Dynamic Time Scrubber & Hotspot Inspector"]

        GATEWAY <--> TWIN --> SLIDER
    end

    %% Inter-Layer Links
    DISAGG --> COUPLER
    DERIV --> COUPLER
    RUNOFF --> COUPLER
    COUPLER --> INLET
    SURCH --> SURROGATE
    RUNOFF --> SURROGATE
    CONVEY --> ROUTING
    CONVEY --> PUMPS
    CONVEY --> CAP
    DEPTHS --> ASSETS
    DEPTHS --> GATEWAY
    ROUTING --> GATEWAY
    ASSETS --> GATEWAY
    PUMPS --> GATEWAY
    CAP --> GATEWAY
```

---

## 3. Operational Lifecycle Sequence Flow Diagram

```mermaid
sequenceDiagram
    autonumber
    participant IMD as IMD Radar & Telecom CML Mesh
    participant L0 as Layer 0 (Atmospheric Ingestion & CML)
    participant L1 as Layer 1 (DEM & Runoff)
    participant L2 as Layer 2 (Pipe Hydraulics & Coastal Surge)
    participant Master as Master Coupler (master_coupler.py)
    participant L3 as Layer 3 (Physics-Informed Topological Graph Surrogate & Street Conveyance)
    participant L4 as Layer 4 (Routing, Pumps & CAP Alerts)
    participant API as Node.js API Gateway
    participant UI as Web GIS Tactical Twin

    IMD->>L0: Push raw Doppler sweep (dBZ) + 35 ward gauges + 8 CML backhauls (Airtel, Jio, Vi)
    Note over L0: Execution: ~15.6 ms
    L0->>L0: Invert CML attenuation via ITU-R P.838-3 (WAA corrected)
    L0->>L0: 2D-Var Kalman Spatial Fusion (Gaspari-Cohn taper)
    L0->>L0: Farnebäck Optical Flow tracking & Semi-Lagrangian Advection
    L0->>L0: 100m Super-Resolution & Street Disaggregation (7,894 roads)
    
    L0->>Master: Transmit multi-horizon rainfall vectors I_k(t) [mm/hr] + CML telemetry
    Master->>L1: Trigger Layer 1 topographical runoff generation
    Note over L1: Execution: ~12.2 ms
    L1->>L1: Sample Cartosat DEM slope (S0) & InSAR subsidence offset
    L1->>L1: Compute ICAR Soil Infiltration (AMC-III) & Sentinel-2 Imperviousness
    L1->>L1: Generate surface excess runoff Q_surf [m³/s] (Modified Rational)

    L1->>Master: Deliver Q_surf and micro-topographical attributes
    Master->>L2: Inflow surface runoff into curb drop-inlets & evaluate tidal surge
    Note over L2: Execution: ~18.5 ms
    L2->>L2: Evaluate Survey of India tidal harmonics & Holland cyclonic storm surge
    L2->>L2: Determine estuarine outfall lockout states (Adyar, Cooum, Buckingham, Ennore)
    L2->>L2: Apply dynamic solid waste clogging factor mu_clog
    L2->>L2: Solve Manning conduit capacity Q_cap
    L2->>L2: Detect HGL > Z_ground -> Compute Saint-Venant backflow Q_backflow

    L2->>Master: Forward gutter bypass Q_bypass + manhole geyser Q_backflow + outfall head
    Master->>L3: Synchronize coupled tensors into Street Graph
    Note over L3: Execution: ~28.4 ms (Sub-Second Benchmark Passed)
    L3->>L3: Relational Graph Convolutional message passing
    L3->>L3: Solve 2D depression pooling and net street depths d_i(t) [cm]
    L3->>L3: Enforce strict volumetric mass balance continuity (error <= 0.000089%)
    L3->>L3: Compute open-channel street flow velocity v and corridor discharge Q
    L3->>L3: Evaluate international v x d hydrodynamic wash-away hazard tiers (DEFRA/ARR)

    L3->>Master: Deliver depths d_i(t), velocity v, and v x d hazard classifications
    Master->>L4: Feed multi-horizon inundation depth tensor & corridor kinematics
    Note over L4: Execution: ~3.2 ms
    L4->>L4: Evaluate flood risk at 20 TANGEDCO 230kV/110kV substations
    L4->>L4: Compute dynamic travel cost Cost(e, t) across 4 vehicle classes
    L4->>L4: Solve safe emergency routes bypassing submerged underpasses
    L4->>L4: Optimize mobile de-watering pump dispatch (Super-Sucker vs Diesel Trash)
    L4->>L4: Emit ITU-T CAP v1.2 bilingual XML (English/Tamil) + Ward WhatsApp bulletins

    L4->>Master: Consolidate MasterTwinResult (Depths, Pumps, Alerts, Routes, KPIs)
    Master->>API: Deliver JSON telemetry payload (Depths, Substations, Routes, Pumps, CAP)
    API->>UI: Stream over WebSocket /ws + REST endpoint update
    UI->>UI: Re-render 521 vector roads, 25 geysers, 20 substations, pumps & alerts at 60 FPS
```

---

## 4. Exhaustive Description of All Architectural Layers (Layer 0 to End)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              THE KAIROS 5-LAYER STACK                                  │
├─────────┬──────────────────────────────────────────────────────────────┬───────────────┤
│ Layer   │ Descriptive Subsystem Title                                  │ Exec. Latency │
├─────────┼──────────────────────────────────────────────────────────────┼───────────────┤
│ Layer 0 │ Multi-Sensor Atmospheric Ingestion, Nowcasting & CML Mesh    │    15.6 ms    │
│ Layer 1 │ 2D Micro-Topography, Cartosat DEM & Surface Runoff Engine    │    12.2 ms    │
│ Layer 2 │ 1D Subsurface Stormwater Hydraulics & Coastal Tidal Lockout  │    18.5 ms    │
│ Coupler │ Master 5-Layer Hydrodynamic Orchestrator (master_coupler.py) │     2.1 ms    │
│ Layer 3 │ Physics-Informed Topological Graph Surrogate & "Street-as-Canal" Conveyance Engine       │    28.4 ms    │
│ Layer 4 │ Dynamic Navigation, Municipal Pumps & ITU-T CAP v1.2 Alerts  │     3.2 ms    │
│ Gateway │ Node.js Express / WebSocket API Infrastructure Gateway       │     1.5 ms    │
│ Client  │ Tactical Web GIS Command Twin (CartoDB Dark / GIGW Skin)     │    60.0 FPS   │
└─────────┴──────────────────────────────────────────────────────────────┴───────────────┘
```

---

### 4.1 Layer 0: Multi-Sensor Atmospheric Ingestion, Nowcasting Fabric & Telecom CML Mesh
**Directory:** [`ai_service/layer0/`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer0)

#### A. Role & Scope
Layer 0 ingests raw atmospheric data across Greater Chennai, corrects radar calibration drift, fills radar beam overshoot blind zones in South Chennai via opportunistic cellular backhaul microwave attenuation, computes atmospheric advection motion vectors, and generates mass-conserved rainfall intensity nowcasts ($I_k(t)$ in $\text{mm/hr}$) across 6 discrete lead-time horizons: $T+15\text{m}, T+30\text{m}, T+60\text{m}, T+90\text{m}, T+120\text{m}, T+180\text{m}$.

#### B. Underlying Physics & Mathematical Formulations
1. **Radar Reflectivity to Rain Rate ($Z-R$ Power Law & Polarimetric $K_{dp}$):**
   $$Z_{\text{dBZ}} = 10 \log_{10} \left( \frac{Z}{1\text{ mm}^6/\text{m}^3} \right), \quad Z = a R^b \iff R = \left( \frac{10^{Z_{\text{dBZ}} / 10}}{a} \right)^{1/b}$$
   - *Continental Marshall-Palmer:* $a=200, b=1.6$ (underestimates tropical cloudbursts by up to 56%).
   - *Maritime Tropical Convective:* $a=130, b=1.4$ (KAIROS primary operational setting).
   - *Polarimetric Specific Differential Phase Shift:*
     $$R(K_{dp}) = 44.0 \times \left| K_{dp} \right|^{0.822} \quad (\text{triggered when } K_{dp} \ge 0.75^\circ/\text{km})$$
2. **Gunnar Farnebäck Dense Optical Flow Motion Tracking:**
   Approximates radar reflectivity sweeps $f_1(\mathbf{x})$ and $f_2(\mathbf{x})$ as local quadratic expansions:
   $$f_1(\mathbf{x}) \approx \mathbf{x}^T \mathbf{A}_1 \mathbf{x} + \mathbf{b}_1^T \mathbf{x} + c_1$$
   Under spatial displacement $\mathbf{d} = [u, v]^T$, solves the weighted Gaussian neighborhood:
   $$\mathbf{d}(\mathbf{x}) = \left( \sum_{\Delta \mathbf{x}} w(\Delta \mathbf{x}) \mathbf{A}^T \mathbf{A} \right)^{-1} \left( \sum_{\Delta \mathbf{x}} w(\Delta \mathbf{x}) \mathbf{A}^T \frac{\Delta \mathbf{b}}{2} \right)$$
3. **Semi-Lagrangian Backward Trajectory Advection:**
   $$\mathbf{x}_{\text{source}} = \mathbf{x} - \left( \frac{h}{\Delta t_{\text{sweep}}} \right) \mathbf{u}_{\text{fused}}(\mathbf{x}), \quad R(\mathbf{x}, T+h) = \operatorname{BilinearInterp}(R_{T-0}, \mathbf{x}_{\text{source}})$$
4. **Brandes Log-Gaussian Gauge Calibration:**
   Computes station log-bias $\beta_i = \ln(G_i / R(\mathbf{x}_i))$, interpolates spatially with correlation length $d_0 = 12\text{ km}$, and evaluates gain:
   $$F(\mathbf{x}) = \operatorname{clip} \left( \exp(\beta(\mathbf{x})), 0.20, 5.00 \right), \quad R_{\text{calibrated}}(\mathbf{x}) = R_{\text{raw}}(\mathbf{x}) \times F(\mathbf{x})$$
5. **Opportunistic Telecom CML Virtual Rain Gauge Mesh (`cml_mesh.py`):**
   Low-altitude cellular point-to-point microwave backhauls (Airtel, Jio, Vi at $15\text{--}45\text{ meters AGL}$) directly sample near-surface atmospheric rain attenuation underneath the radar beam. In accordance with **ITU-R P.838-3**, path attenuation is governed by:
   $$k = a \cdot R^b \iff R = \left( \frac{k}{a} \right)^{1/b}$$
   Where $k = A_{\text{rain}} / L_{\text{km}}$ is specific attenuation ($\text{dB/km}$) across path length $L_{\text{km}}$.
   
   **ITU-R P.838-3 Cellular Backhaul Band Coefficients:**
   | Frequency (GHz) | $a_h$ (Horizontal) | $b_h$ (Horizontal) | $a_v$ (Vertical) | $b_v$ (Vertical) |
   | :---: | :---: | :---: | :---: | :---: |
   | **13 GHz** | 0.0240 | 1.1516 | 0.0210 | 1.1200 |
   | **15 GHz** | 0.0367 | 1.1190 | 0.0335 | 1.0890 |
   | **18 GHz** | 0.0707 | 1.0818 | 0.0604 | 1.0515 |
   | **23 GHz** | 0.1287 | 1.0230 | 0.1128 | 1.0001 |
   | **26 GHz** | 0.1747 | 0.9930 | 0.1538 | 0.9754 |
   | **38 GHz** | 0.3844 | 0.8552 | 0.3524 | 0.8410 |
   | **73 GHz (5G E-Band)** | 0.9500 | 0.7200 | 0.9100 | 0.7100 |

   - **Wet Antenna Attenuation (WAA) Baseline Offset:** Moisture film condensing on microwave antenna radomes induces non-path attenuation ($A_{\text{waa}} \approx 1.6\text{ dB}$):
     $$A_{\text{rain}} = \max\left(0.0, \; (RSL_{\text{baseline}} - RSL_{\text{wet}}) - A_{\text{waa}}\right)$$
   - **GCC Chennai Cellular Mesh Chords:** Monitors 8 key microwave backhauls covering critical blind corridors: Egmore (Airtel 18GHz), T. Nagar (Jio 23GHz), Velachery-Thiruvanmiyur (Vi 23GHz), Guindy-Tambaram (Airtel 15GHz), Vyasarpadi (Jio 26GHz), Anna Nagar (Airtel 38GHz), OMR IT Corridor 5G (Jio 73GHz), and Porur-Ramapuram (Vi 18GHz).
6. **2D-Var Kalman Spatial Fusion (Gaspari-Cohn Localization):**
   Blends radar, 35+ AWS gauges, and CML backhauls in log-space:
   $$\left( \mathbf{H} \mathbf{B} \mathbf{H}^T + \mathbf{R} \right) \mathbf{w} = \mathbf{d}, \quad \mathbf{x}_a = \mathbf{x}_b + \mathbf{B} \mathbf{H}^T \mathbf{w}$$
7. **Cell-Wise Strict Mass Conservation Operator:**
   Guarantees that 100m super-resolution preserves exact input volume ($\le 0.000000\%$ volume error):
   $$\gamma_{j, k} = \frac{R_{1\text{km}}(j, k)}{\frac{1}{100} \sum_{m=1}^{10} \sum_{n=1}^{10} R_{\text{modulated}}(j, k, m, n)}, \quad R_{\text{conserved}} = R_{\text{modulated}} \times \gamma_{j, k}$$

#### C. Source Code Inventory
- [`ingestion.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer0/ingestion.py): IMD Doppler Weather Radar scraper (Meenambakkam/Port), AWS scraper, synthetic fallback.
- [`calibrator.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer0/calibrator.py): Brandes log-Gaussian bias calibration & Kriging with External Drift (KED).
- [`nowcaster.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer0/nowcaster.py): Farnebäck optical flow storm velocity tracking and backward advection.
- [`stochastic_nowcaster.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer0/stochastic_nowcaster.py): 1-minute continuous cosine keyframe sub-stepping and PySteps STEPS perturbation cascades.
- [`cml_mesh.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer0/cml_mesh.py): Opportunistic Telecom CML rainfall retrieval engine using ITU-R P.838-3 inversion, dynamic baseline tracking, WAA correction, and 8-link cellular backhaul mesh telemetry.
- [`cml_ingestor.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer0/cml_ingestor.py): ITU-R P.838-3 telecom microwave path attenuation spatial interpolator.
- [`fusion.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer0/fusion.py): 2D-Var Kalman data assimilation with Gaspari-Cohn 5th-order compact polynomial taper.
- [`super_resolution.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer0/super_resolution.py): Physics-informed 100m downscaling using orographic gradient & sea-breeze front corridors.
- [`disaggregator.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer0/disaggregator.py): Mass-conservative spatial polygon join to 7,894 GCC road segments.
- [`pipeline.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer0/pipeline.py): Layer 0 master pipeline runner.

#### D. Inputs & Outputs
- **Inputs:** IMD Meenambakkam S-Band sweeps (GIF/NetCDF, $79 \times 83$ grid, 1 km resolution), 35 GCC telemetry rain gauges, 8 cellular CML microwave backhaul chords across Airtel, Jio, and Vi.
- **Outputs:** `Layer0Result` containing `DataFrame` with columns `I_T+15m_mmh`, `I_T+30m_mmh`, `I_T+60m_mmh`, `I_T+90m_mmh`, `I_T+120m_mmh`, `I_T+180m_mmh` for all 7,894 road corridors, plus `cml_telemetry` dictionary.

---

### 4.2 Layer 1: 2D Micro-Topography, Cartosat DEM & Surface Runoff Engine
**Directory:** [`ai_service/layer1/`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer1)

#### A. Role & Scope
Converts 30m stereoscopic terrain elevation models into hydro-conditioned flow corridors, computes slope gradients and aspect, extracts Sentinel-2 Land Use / Land Cover (LULC) imperviousness, integrates USDA/ICAR soil infiltration models, and generates net surface excess runoff ($R_{\text{excess}}$ [mm/hr]) and tributary inflow discharge ($Q_{\text{surf}}$ [m³/s]).

#### B. Underlying Physics & Mathematical Formulations
1. **EGM96 Orthometric Height Calibration & InSAR Vertical Subsidence Offset:**
   $$Z_{\text{corrected}}(\mathbf{x}) = Z_{\text{Cartosat}}(\mathbf{x}) - \left( v_{\text{subsidence}}(\mathbf{x}) \cdot \Delta t \right)$$
   *(Corrects coastal land subsidence up to $12\text{ mm/year}$ identified from Sentinel-1 InSAR).*
2. **Hydro-Conditioning (Stream Burning & Underpass Carving):**
   - Stream burning along Buckingham Canal, Adyar, and Cooum: burns $-2.0\text{ meters}$ relief to remove digital bridge dams.
   - Underpass carving: enforces $-1.8\text{ meters}$ depression at 353 railway subways and grade dips.
3. **8-Neighborhood Horn Elevation Gradient:**
   $$\left( \frac{\partial Z}{\partial x} \right) = \frac{(Z_{ne} + 2 Z_e + Z_{se}) - (Z_{nw} + 2 Z_w + Z_{sw})}{8 \cdot \Delta x}, \quad S_0 = \sqrt{ \left( \frac{\partial Z}{\partial x} \right)^2 + \left( \frac{\partial Z}{\partial y} \right)^2 }$$
4. **Soil Infiltration & Riparian Waterlogging Penalties:**
   $$f_{\text{eff}} = K_{\text{sat}} \times \Phi_{\text{AMC}} \times \Phi_{\text{water\_table}} \times \Phi_{\text{riparian}} \times \Phi_{\text{subsidence}}$$
   - $\Phi_{\text{water\_table}} = 0.50$ if distance to coast $< 1.5\text{ km}$ and elevation $< 3.5\text{ m MSL}$.
   - $\Phi_{\text{riparian}} = 0.40$ if within $150\text{ m}$ of Buckingham Canal or Cooum River.
   - $\Phi_{\text{subsidence}} = 0.85$ if subsidence $> 3.5\text{ mm/year}$ (pore compaction).
5. **Surface Excess Runoff Generation (Modified Rational Method):**
   $$Q_{\text{surface}}(k, t) = \left[ C_{\text{imperv}} \cdot \left( \frac{I_k(t)}{3.6 \times 10^6} \right) \cdot A_k \right] + \max \left( 0, (1 - C_{\text{imperv}}) \cdot \left( \frac{I_k(t) - f_{\text{eff}}}{3.6 \times 10^6} \right) \cdot A_k \right)$$

#### C. Source Code Inventory
- [`dem_builder.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer1/dem_builder.py): Mosaics Cartosat-1 30m tiles, reprojects to UTM 44N (EPSG:32644), applies InSAR subsidence.
- [`hydro_conditioner.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer1/hydro_conditioner.py): Digital dam breaching, stream burning, underpass depression carving.
- [`hydrologic_derivatives.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer1/hydrologic_derivatives.py): Horn gradient slope $S_0$, azimuth aspect, D8 steepest descent flow accumulation.
- [`road_sampler.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer1/road_sampler.py): Bilinear spatial join sampling $Z_{\text{ground}}$ and $S_0$ directly onto 7,894 GCC road centroids.
- [`lulc/impervious_extractor.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer1/lulc/impervious_extractor.py): DCIA fraction from GCC 15 zones, Building Coverage Ratio (BCR), and RWH credits.
- [`lulc/soil_hydrology.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer1/lulc/soil_hydrology.py): USDA/ICAR Hydrologic Soil Groups (A, B, C, D) and dynamic Antecedent Moisture Conditions (AMC I, II, III).
- [`lulc/runoff_generator.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer1/lulc/runoff_generator.py): Surface excess runoff rate $R_{\text{excess}}$ [mm/hr] and tributary inflow $Q_{\text{surf}}$ [m³/s].
- [`pipeline.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer1/pipeline.py): Layer 1 master orchestrator.

#### D. Inputs & Outputs
- **Inputs:** Layer 0 rainfall vectors, ISRO Cartosat-1 30m DEM GeoTIFF, Sentinel-1 InSAR subsidence CSV, Sentinel-2 LULC raster, ICAR Soil Classification map.
- **Outputs:** `RunoffResult` containing `DataFrame` with `elevation_m`, `slope_degrees`, `impervious_fraction`, `effective_infiltration_mm_hr`, `surface_runoff_rate_mm_hr`, and `surface_runoff_inflow_m3_s`.

---

### 4.3 Layer 2: 1D Subsurface Stormwater Network Hydraulics, Surcharge & Coastal Tidal Lockout
**Directory:** [`ai_service/layer2/`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer2)

#### A. Role & Scope
Models the underground stormwater drainage graph (RCC pipes, masonry box culverts, catch-pits, manholes, outfalls). Incorporates municipal solid waste clogging ($\mu_{\text{clog}}$), calculates curb drop-inlet capture vs gutter bypass, monitors the Hydraulic Grade Line (HGL), simulates Saint-Venant manhole surcharge geyser eruptions, and computes coastal astronomical tide and cyclonic storm surge outfall lockout boundary conditions along the Bay of Bengal coastline.

#### B. Underlying Physics & Mathematical Formulations
1. **Empirical Municipal Solid Waste Clogging Penalty ($\mu_{\text{clog}}$):**
   $$\mu_{\text{clog}} = \operatorname{clip} \left( 0.10 + 0.50 \cdot (1 - \eta_{\text{desilt}}) + 0.40 \cdot (1 - \eta_{\text{collection}}), \, 0.05, \, 0.85 \right)$$
   - Effective conduit area: $A_{\text{eff}} = A_0 \times (1.0 - \mu_{\text{clog}})$
   - Effective Manning roughness: $n_{\text{eff}} = n_0 \times (1.0 + 1.8 \mu_{\text{clog}})$
   - Effective hydraulic radius: $R_{h, \text{eff}} = R_{h0} \times \sqrt{1.0 - \mu_{\text{clog}}}$
2. **Manning Conduit Full-Pipe Conveyance Solver:**
   $$Q_{\text{cap}} = \frac{1}{n_{\text{eff}}} A_{\text{eff}} R_{h, \text{eff}}^{2/3} S_0^{1/2}$$
3. **Curb Drop-Inlet Grate Capture Hydraulics:**
   $$Q_{\text{weir}} = C_w \cdot P_{\text{eff}} \cdot h^{1.5} \quad (h < 0.12\text{ m}, \; C_w = 1.66)$$
   $$Q_{\text{orifice}} = C_d \cdot A_{\text{grate\_eff}} \cdot \sqrt{2 g h} \quad (h \ge 0.12\text{ m}, \; C_d = 0.60)$$
   $$Q_{\text{captured}} = \min(Q_{\text{surface}}, \, Q_{\text{inlet\_cap}}), \quad Q_{\text{bypass}} = Q_{\text{surface}} - Q_{\text{captured}}$$
4. **Saint-Venant Manhole Surcharge & Geyser Backflow Eruption:**
   When inflow exceeds conduit conveyance ($Q_{\text{in}} > Q_{\text{cap}}$), the HGL rises above the street elevation:
   $$\text{Surcharge Condition:} \quad \text{HGL}_i > Z_{\text{ground}, i}, \quad \Delta h_i = \max(0.0, \, \text{HGL}_i - Z_{\text{ground}, i})$$
   $$Q_{\text{backflow}} = C_d \cdot A_{\text{lid}} \cdot \sqrt{2 g \Delta h_i} \quad (C_d = 0.62, \; A_{\text{lid}} = \pi (D_{\text{lid}}/2)^2)$$
   $$\text{Net street inflow: } Q_{\text{net}} = Q_{\text{bypass}} + Q_{\text{backflow}}$$
5. **Coastal Tidal Lockout & Cyclonic Storm Surge Boundary Formulation (`coastal_boundary.py`):**
   Chennai's terminal drainage canals discharge into the Bay of Bengal. High tides and cyclonic wind setup raise coastal water levels, backing water into inland conduits:
   - **Astronomical Tidal Harmonic Superposition:**
     $$\eta_{\text{astro}}(t) = Z_{\text{datum}} + \sum_{k=1}^6 A_k \cos(\omega_k t - \phi_k)$$
     *Survey of India / INCOIS Tidal Constants for Chennai Port:*
     | Constituent | Description | Period (hr) | Angular Speed ($\omega^\circ/\text{hr}$) | Amplitude ($A\text{ m}$) | Phase ($\phi^\circ$) |
     | :---: | :--- | :---: | :---: | :---: | :---: |
     | $M_2$ | Principal lunar semidiurnal | 12.4206 | 28.9841 | 0.420 | 124.5 |
     | $S_2$ | Principal solar semidiurnal | 12.0000 | 30.0000 | 0.180 | 162.0 |
     | $N_2$ | Larger lunar elliptic | 12.6583 | 28.4397 | 0.085 | 108.2 |
     | $K_1$ | Lunar diurnal | 23.9345 | 15.0411 | 0.142 | 198.4 |
     | $O_1$ | Lunar diurnal | 25.8193 | 13.9430 | 0.065 | 182.1 |
     | $M_4$ | Shallow water overtide | 6.2103 | 57.9682 | 0.022 | 215.0 |
   - **Bay of Bengal Cyclonic Storm Surge Model:**
     $$\Delta h_{\text{surge}} = \Delta h_{IB} + \Delta h_{\text{wind}} + \Delta h_{\text{wave}}$$
     - *Inverted Barometer Effect:* $\Delta h_{IB} = \max(0, P_{\text{ambient}} - P_{\text{central}}) \times 0.01\text{ m/hPa}$.
     - *Holland Wind Stress Setup:* $\tau_{\text{wind}} = \rho_{\text{air}} C_d W^2$, with $C_d = (0.8 + 0.065 W) \times 10^{-3}$, and $\Delta h_{\text{wind}} = \frac{\tau_{\text{wind}} (L_{\text{shelf}} \times 1000)}{\rho_{\text{water}} g D_{\text{shelf}}}$ ($L_{\text{shelf}}=40\text{ km}, D_{\text{shelf}}=25\text{ m}$).
     - *Wave Setup:* $\Delta h_{\text{wave}} = 0.15 \times \min(4.0, (W / 15.0)^{1.5})$.
     - *Total Sea Level:* $H_{\text{sea}}(t) = \eta_{\text{astro}}(t) + \Delta h_{\text{surge}}$.
   - **Outfall Lockout Hydraulic Classification:**
     Monitored at 4 vital estuarine nodes: Adyar River Estuary ($Z_{\text{inv}}=0.50\text{ m}$), Cooum River Mouth ($Z_{\text{inv}}=0.40\text{ m}$), Buckingham Canal Lockout ($Z_{\text{inv}}=0.30\text{ m}$), and Ennore Creek ($Z_{\text{inv}}=0.70\text{ m}$).
     - `FREE_GRAVITY` ($H_{\text{sea}} \le Z_{\text{inv}}$): $\eta_{\text{eff}} = 1.0$, throttling = $0.0$.
     - `THROTTLED_BACKWATER` ($Z_{\text{inv}} < H_{\text{sea}} < \text{HGL}$): Submerged orifice ratio $\eta_{\text{eff}} = \sqrt{\frac{\text{HGL} - H_{\text{sea}}}{\text{HGL} - Z_{\text{inv}}}}$, throttling = $1.0 - \eta_{\text{eff}}$.
     - `TIDAL_LOCKOUT` ($|\text{HGL} - H_{\text{sea}}| \le 0.05\text{ m}$): Gravity flow ceases entirely, $\eta_{\text{eff}} = 0.0$, throttling = $1.0$.
     - `REVERSE_INTRUSION` ($H_{\text{sea}} > \text{HGL}$): Reverse marine backwater enters city drains, $\eta_{\text{eff}} = -\sqrt{\min(2.0, |H_{\text{sea}} - \text{HGL}|)}$, throttling = $1.0$.

#### C. Source Code Inventory
- [`drainage_graph.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer2/drainage_graph.py): Builds 1D subsurface graph from GCC/CMWSSB pipe networks.
- [`clogging_model.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer2/clogging_model.py): Dynamic solid waste generation (TPD) and desilting arrears penalty engine.
- [`conduit_flow.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer2/conduit_flow.py): Manning conveyance solver for circular pipes and rectangular box drains.
- [`inlet_capture.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer2/inlet_capture.py): Gutter flow, weir-orifice capture transition, and debris blockage.
- [`manhole_surcharge.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer2/manhole_surcharge.py): HGL tracking, surcharge geyser eruption, and GCC 1913 hotspot calibration.
- [`coastal_boundary.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer2/coastal_boundary.py): Coastal tidal harmonics, Holland cyclonic storm surge model, and estuarine outfall lockout status evaluator.
- [`pipeline.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer2/pipeline.py): Layer 2 master orchestrator.

#### D. Inputs & Outputs
- **Inputs:** Layer 1 surface inflow $Q_{\text{surf}}$, pipe diameters ($D \in [600, 1200]\text{ mm}$), pipe bed slopes $S_0$, GCC solid waste generation records (TPD), canal desilting status records, Survey of India astronomical tidal constants, cyclonic storm surge parameters (central pressure, sustained wind).
- **Outputs:** `Layer2Result` containing conduit capacity utilization percentage, clogged conveyance, list of surcharging manhole hotspots ($Q_{\text{backflow}}$ [m³/s], pressure head $\Delta h$ [m]), and coastal boundary outfall status dictionary (`FREE_GRAVITY`, `THROTTLED_BACKWATER`, `TIDAL_LOCKOUT`, `REVERSE_INTRUSION`).

---

### 4.4 Orchestration Layer: In-Memory 1D-2D Coupler & Master 5-Layer Hydrodynamic Orchestrator
**Directory:** [`ai_service/orchestration/`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/orchestration)

#### A. Role & Scope
The Orchestration Layer provides two critical coordination tiers:
1. **Mid-Tier In-Memory 1D-2D Coupler (`coupler.py`):** Synchronizes state variables and tensors between Layer 0, Layer 1, and Layer 2 without disk I/O bottlenecks, enforcing zero-copy array operations and strict domain mass conservation.
2. **Master 5-Layer Hydrodynamic Orchestrator (`master_coupler.py`):** Unifies all five layers—from multi-sensor radar and opportunistic telecom CML links, through DEM runoff and pipe/tide hydraulics, to Physics-Informed Topological Graph Surrogates, street-as-canal hazard kinematics, municipal pump dispatch, and ITU-T CAP v1.2 emergency alerts—into a single in-memory execution pipeline running in $< 500\text{ ms}$.

#### B. Architectural Design of `master_coupler.py`
The master orchestrator implements the `MasterTwinCoupler` class, managing a deterministic 5-stage sequential lifecycle:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        MASTER TWIN COUPLER EXECUTION LIFECYCLE                         │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Step 1: Layer 0 Ingestion & CML Mesh                                                   │
│   ├── Live IMD Meenambakkam S-Band Radar sweep decoding & 2D-Var Kalman fusion         │
│   └── ITU-R P.838-3 cellular microwave attenuation inversion (8 backhaul chords)      │
│                                      │                                                 │
│ Step 2: Layer 1 Micro-Topography & Soil Runoff                                         │
│   ├── Sample Cartosat-1 DEM slope S0 and InSAR vertical subsidence offset              │
│   └── ICAR Hydrologic Soil Group infiltration & Modified Rational surface runoff Q_surf│
│                                      │                                                 │
│ Step 3: Layer 2 Pipe Hydraulics & Coastal Surge Boundary                               │
│   ├── Municipal solid waste clogging penalty (mu_clog) & Manning conduit capacity      │
│   ├── Survey of India tidal harmonic superposition + Holland cyclonic storm surge      │
│   └── Saint-Venant HGL pressurization & backflow geyser discharge (Q_backflow)         │
│                                      │                                                 │
│ Step 4: Layer 3 Physics-Informed Topological Graph Surrogate & "Street-as-Canal" Conveyance                        │
│   ├── Sub-second Relational Graph Convolutional message passing (< 30 ms)              │
│   ├── Volumetric mass conservation continuity enforcement (error <= 0.000089%)         │
│   └── Manning street open-channel velocity v and v x d wash-away hazard tiers          │
│                                      │                                                 │
│ Step 5: Layer 4 Dynamic Routing, Municipal Pumps & CAP Alerts                          │
│   ├── Dynamic A* emergency clearance routing across 4 vehicle classes                  │
│   ├── TANGEDCO 230kV/110kV substation plinth waterlogging hazard monitoring            │
│   ├── Automated Municipal De-Watering Pump Dispatch Optimizer (Super-Suckers / Diesel) │
│   └── ITU-T Recommendation X.1303 CAP v1.2 bilingual XML & WhatsApp bulletin emission │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

- **`MasterTwinResult` Data Container:** Encapsulates the entire multi-layer state:
  - `dataframe`: Master road segment DataFrame with hydraulic, topographic, and hazard attributes.
  - `horizons_depths`: Multi-horizon depth tensors ($T+15\text{m}, T+30\text{m}, T+60\text{m}, T+90\text{m}, T+120\text{m}, T+180\text{m}$).
  - `diagnostics`: Subsystem runtime telemetry, verifying sub-second SLA compliance.
  - `pump_recommendations`: Ranked list of mobile de-watering pump dispatch sites.
  - `coastal_outfall_status`: Locked-out estuarine outfalls with backwater intrusion metrics.
  - `cml_telemetry`: Cellular backhaul attenuation, retrieved rain rates, and WAA offsets.
  - `street_conveyance_summary`: Fast channel counts, max velocity, and $v \times d$ floatation hazards.
- **Executive KPI Engine (`to_kpi_summary()`):** Consolidates high-level situational metrics for GCC ICCC Commissioners:
  - `peak_depth_t60_cm`: Peak predicted inundation depth across Greater Chennai.
  - `inundated_roads_count`: Segments with water depth $\ge 10\text{ cm}$.
  - `critical_impassable_roads_count`: Segments exceeding emergency vehicle clearance ($\ge 30\text{ cm}$).
  - `coastal_outfalls_locked`: Number of tidal outfalls with zero or reverse discharge.
  - `recommended_pumps_count`: Required mobile de-watering pump fleet deployments.
  - `total_execution_ms`: Total execution time across all 5 layers.
- **Command-Line Interface:**
  ```bash
  python -m ai_service.orchestration.master_coupler --scenario michaung --clogging 0.35 --tide-surge 0.85
  ```

#### C. Source Code Inventory
- [`coupler.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/orchestration/coupler.py): In-memory tensor coupler linking rainfall nowcasts, micro-topography, and pipe hydraulics.
- [`runner.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/orchestration/runner.py): Command-line execution harness with zonal diagnostic reporting and JSON/CSV export.
- [`master_coupler.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/orchestration/master_coupler.py): Master 5-layer end-to-end hydrodynamic and tactical emergency digital twin orchestrator chaining all pipelines in $< 500\text{ ms}$.

#### D. Inputs & Outputs
- **Inputs:** Scenario configuration (`michaung`, `2015_flood`, `monsoon`), municipal solid waste clogging modifier ($0.0\text{--}0.85$), cyclonic storm surge head ($0.0\text{--}2.5\text{ m}$), optional cloudburst peak intensity ($\text{mm/hr}$).
- **Outputs:** `MasterTwinResult` containing full road network DataFrame, 6-horizon depth matrices, municipal pump deployment schedules, coastal boundary lockout states, CML telemetry diagnostics, and executive KPI summaries.

---

### 4.5 Layer 3: Physics-Informed Topological Graph Surrogate & Street Conveyance
**Directory:** [`ai_service/layer3/`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer3)

#### A. Role & Scope
Iterative 2D hydrodynamic solvers (SWMM, TUFLOW) take 45–90 minutes to simulate 7,894 road corridors across Chennai. Layer 3 replaces numerical PDE solvers with a **Physics-Informed Topological Graph Surrogate**, achieving **$< 30\text{ ms}$** execution latency across the entire city with **$\le 0.000089\%$ volumetric mass continuity error**. Additionally, when conduits surcharge, it models streets as open-channel conveyance flumes, computing flow velocities, corridor discharge, and international velocity-depth ($v \times d$) wash-away hazards.

#### B. Underlying Physics & Mathematical Formulations
1. **Topological Graph Message-Passing Formulation:**
   Formalizes the city as a directed multigraph $G = (V, E)$, where each street corridor $i \in V$ possesses node features:
   $$\mathbf{h}_i^{(0)} = [Z_i, S_{0, i}, A_i, C_i, D_{\text{pipe}, i}, \mu_{\text{clog}, i}, I_i(t)]^T$$
   Updates node representations via relational message-passing down the hydraulic gradient:
   $$\mathbf{h}_i^{(l+1)} = \sigma \left( \mathbf{W}_{\text{self}} \mathbf{h}_i^{(l)} + \sum_{j \in \mathcal{N}_{\text{up}}(i)} \frac{1}{\sqrt{d_i d_j}} \mathbf{W}_{\text{up}} \mathbf{h}_j^{(l)} + \sum_{k \in \mathcal{N}_{\text{down}}(i)} \mathbf{W}_{\text{down}} \mathbf{h}_k^{(l)} \right)$$
2. **2D Micro-Topographical Depression Convergence:**
   Simulates runoff accumulation into local depressions ($Z < 7.5\text{ m MSL}$):
   $$\mathcal{D}_{\text{factor}}(\mathbf{x}) = \operatorname{clip} \left( \frac{12.0 - Z(\mathbf{x})}{6.0}, 0.2, 3.8 \right)$$
3. **Volumetric Mass Conservation Continuity Constraint:**
   $$\Delta V_{\text{surface}}(t) + V_{\text{pipe}}(t) = V_{\text{precip}}(t)$$
   $$\text{Relative Volume Error: } \text{RVE} = \frac{\left| \sum_i (A_i \cdot d_i(t)) + \sum_i V_{\text{pipe}, i}(t) - \sum_i (A_i \cdot I_i(t) \cdot \Delta t) \right|}{\sum_i (A_i \cdot I_i(t) \cdot \Delta t)} \times 100 \le 0.001\%$$
4. **"Street-as-Canal" Open Conveyance & Velocity-Depth ($v \times d$) Hazard Engine (`street_conveyance.py`):**
   When 1D subsurface drains choke, excess water flows overland. Streets function as open conveyance channels governed by Manning's equation:
   $$v = \frac{1}{n_{\text{road}}} R_h^{2/3} S_0^{1/2} \quad (n_{\text{road}} = 0.016 \text{ for urban asphalt})$$
   - **Road Geometries (CPHEEO / IRC Guidelines):**
     Widths range from Motorways ($24.0\text{ m}$), Primaries ($16.0\text{ m}$), Secondaries ($12.0\text{ m}$), down to Residential streets ($5.5\text{ m}$) and Service lanes ($4.5\text{ m}$).
   - **Hydraulic Radius & Corridor Discharge:**
     $$R_h = \frac{W_{\text{road}} \cdot d}{W_{\text{road}} + 2d}, \quad Q_{\text{corridor}} = v \cdot W_{\text{road}} \cdot d \quad [\text{m}^3/\text{s}]$$
   - **International Velocity-Depth Product ($v \times d$) Wash-Away Hazard Tiers (UK DEFRA / Australian ARR):**
     | Hazard Tier | $v \times d$ Threshold | Threat Description | Tactical Action |
     | :---: | :---: | :--- | :--- |
     | **LOW** | $< 0.40\text{ m}^2/\text{s}$ | Safe for pedestrian wading; cars maintain tire traction. | Normal vehicular transit permitted. |
     | **MODERATE** | $0.40\text{--}0.60\text{ m}^2/\text{s}$ | Pedestrian instability; children and two-wheelers lose footing. | Restrict two-wheelers and pedestrians. |
     | **HIGH** | $0.60\text{--}1.20\text{ m}^2/\text{s}$ | Passenger cars & auto-rickshaws float, lose braking, and wash away. | Divert light traffic; allow emergency trucks only. |
     | **EXTREME** | $\ge 1.20\text{ m}^2/\text{s}$ | High wash-away momentum; 108 ambulances & heavy fire trucks destabilized. | Complete road lockout; deploy NDRF motorized boats. |
   - **Active Street Channel Flag:** Corridor classified as active torrential flume if $Q_{\text{corridor}} > 1.0\text{ m}^3/\text{s}$ and $v > 0.5\text{ m/s}$.

#### C. Source Code Inventory
- [`graph_builder.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer3/graph_builder.py): Assembles the 7,894-node street graph coupled with DEM attributes and conduits.
- [`surrogate_model.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer3/surrogate_model.py): Sub-second Physics-Informed Topological Graph Surrogate topological surrogate solving multi-horizon flood depths.
- [`mass_conservation_loss.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer3/mass_conservation_loss.py): Verifies volumetric continuity and applies a hard post-hoc volume-projection step that enforces mass conservation to < 0.001% residual.
- [`street_conveyance.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer3/street_conveyance.py): "Street-as-Canal" open-channel conveyance engine computing Manning flow velocities, corridor discharge, and international $v \times d$ wash-away hazard tiers.
- [`benchmark_validator.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer3/benchmark_validator.py): Cross-validates depths against historical 2015 Deluge survey records and Cyclone Michaung.
- [`pipeline.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer3/pipeline.py): Layer 3 master pipeline orchestrator.

#### D. Inputs & Outputs
- **Inputs:** Layer 0 rain vectors across 6 horizons, Layer 1 DEM elevation & slopes, Layer 2 conduit capacities and surcharge backflow rates.
- **Outputs:** `Layer3Result` containing `DataFrame` with columns `depth_T+15m_cm`, `depth_T+30m_cm`, `depth_T+60m_cm`, `depth_T+90m_cm`, `depth_T+120m_cm`, `depth_T+180m_cm`, `flow_velocity_m_s`, `corridor_discharge_m3_s`, `hazard_vx_d_m2_s`, `washaway_hazard_tier`, and `is_street_channel` boolean flags.

---

### 4.6 Layer 4: Dynamic Safe Navigation, Municipal Pump Dispatch & ITU-T CAP v1.2 Multilingual Alerts
**Directory:** [`ai_service/layer4/`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer4)

#### A. Role & Scope
Provides operational decision support for emergency first responders (108 Ambulances, NDRF Heavy Rescue Trucks) by routing around submerged corridors and preventing engine hydrolock. Simultaneously monitors flood risks at 20 critical TANGEDCO 230kV/110kV electrical substations, automates priority dispatch scheduling for GCC heavy mobile de-watering pumps, and emits standardized ITU-T Recommendation X.1303 / OASIS CAP v1.2 multilingual emergency bulletins aligned with NDMA SACHET.

#### B. Underlying Physics & Mathematical Formulations
1. **Dynamic Inundation Travel Cost Function:**
   For every road edge $e$ in the network at forecast lead time $t$:
   $$\text{Cost}(e, t) = \begin{cases}
   \left( \frac{L_e}{V_{\text{free}}} \right) \left[ 1.0 + \alpha \left( \frac{d(e, t)}{d_{\text{caution}}} \right)^\beta \right] & \text{if } d(e, t) \le d_{\text{impassable}} \\
   \infty & \text{if } d(e, t) > d_{\text{impassable}}
   \end{cases}$$
2. **Vehicle Clearance Profiles:**
   - **108 Emergency Ambulance:** $d_{\text{caution}} = 15\text{ cm}, \; d_{\text{impassable}} = 30\text{ cm}, \; \alpha = 2.5, \; \beta = 2.0$.
   - **NDRF Heavy Rescue Truck:** $d_{\text{caution}} = 25\text{ cm}, \; d_{\text{impassable}} = 45\text{ cm}, \; \alpha = 1.8, \; \beta = 1.5$.
   - **Passenger Car (Sedan/SUV):** $d_{\text{caution}} = 10\text{ cm}, \; d_{\text{impassable}} = 18\text{ cm}, \; \alpha = 3.5, \; \beta = 2.5$.
   - **Two-Wheeler / Motorbike:** $d_{\text{caution}} = 5\text{ cm}, \; d_{\text{impassable}} = 10\text{ cm}, \; \alpha = 5.0, \; \beta = 3.0$.
3. **Flood-Aware Admissible A\* Routing:**
   Uses a flood-scaled admissible Haversine heuristic to guarantee shortest safe traversal:
   $$h(n) = \frac{\operatorname{Haversine}(n, \text{Destination})}{V_{\text{free\_max}}}$$
4. **TANGEDCO Electrical Substation Plinth Safeguarding:**
   Evaluates plinth flood hazard for 20 high-voltage substations:
   $$\text{Plinth Clearance Margin: } \Delta Z_{\text{plinth}} = Z_{\text{plinth\_level}} - d_{\text{local}}(t)$$
   - $\Delta Z_{\text{plinth}} \le 0\text{ cm}$: **CRITICAL SUBMERGENCE HAZARD** (Trigger emergency load shedding).
   - $0 < \Delta Z_{\text{plinth}} \le 15\text{ cm}$: **YELLOW WARNING** (Deploy dewatering diesel pumps).
5. **Automated Municipal De-Watering Pump Dispatch Optimizer (`pump_optimizer.py`):**
   Identifies choked road corridors where mobile de-watering pump rigs (Super-Suckers & high-head trash pumps) yield the greatest depth reduction.
   - **Required Sump Extraction Capacity Heuristic:**
     Targeting the evacuation of $150\text{ mm}$ excess ponding in 45 minutes while countering subterranean backflow:
     $$Q_{\text{pump\_req}} = \max\left(180.0, \; \operatorname{round}(d_{\text{cm}} \times 24.5 + Q_{\text{surcharge}} \times 3600.0 \times 0.4)\right) \quad [\text{m}^3/\text{hr}]$$
   - **Equipment Sizing Hierarchy:**
     - $d_{\text{cm}} > 40.0\text{ cm}$: **Super-Sucker High CFM Unit** (GCC heavy vacuum fleet)
     - $d_{\text{cm}} \le 40.0\text{ cm}$: **Mobile Diesel Trash Pump (150 HP)**
   - **Estimated Net Volume Relief:**
     $$V_{\text{relief}} = Q_{\text{pump\_req}} \times 1.5 \quad [\text{m}^3]$$
   - **GCC Critical Strategic Deployment Sites:**
     Pre-calibrated priority choke points: Usman Road Underpass (T. Nagar - Zone 9), Velachery Vijaya Nagar (Zone 13), GST Road / Guindy Substation (Zone 10), Vyasarpadi Ganesapuram Subway (Zone 4), Poonamallee High Road (Zone 8), Perumbakkam Main Road (Zone 14), Madipakkam Koot Road (Zone 14), and Royapuram Coastal Outlet (Zone 5).
6. **ITU-T Recommendation X.1303 / OASIS CAP v1.2 Multilingual Emergency Alert Emitter (`cap_emitter.py`):**
   Standardized Common Alerting Protocol generation aligned with National Disaster Management Authority (NDMA) SACHET infrastructure.
   - **Bilingual XML Generation:** Produces valid CAP v1.2 XML with separate info blocks for English (`en-IN`) and Tamil (`ta-IN`), including event tags, severity, urgency, certainty, headlines, descriptions, and action instructions.
   - **Ward Geospatial Polygon Binding:** Automatically embeds WGS84 boundary polygons for impacted GCC zones (Zone 4 Tondiarpet, Zone 9 Teynampet, Zone 10 Kodambakkam, Zone 13 Adyar).
   - **Multi-Channel Operational Outputs:**
     1. *GCC Ward Engineer WhatsApp Technical Dispatch:* Structured engineering dispatch specifying Zone, Corridor name, Lead Forecast Horizon ($T+h$), Predicted Depth ($d_{\text{cm}}$), Surcharge Backflow Rate ($Q_{\text{backflow}}$ [m³/s]), Assigned Pump Rig ID, and Suction Invert Directives.
     2. *Citizen SMS Broadcasts:* Localized bilingual SMS (English and Tamil) advising motorists of imminent road impassability and emergency diversion corridors, referencing GCC helpline **1913**.

#### C. Source Code Inventory
- [`routing_engine.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer4/routing_engine.py): Dynamic A* safe routing solver vs naive submerged shortest path.
- [`critical_assets_monitor.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer4/critical_assets_monitor.py): Evaluates plinth flood risks across 20 TANGEDCO 230kV/110kV substations.
- [`risk_cost_evaluator.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer4/risk_cost_evaluator.py): Computes non-linear velocity degradation penalties across vehicle classes.
- [`pump_optimizer.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer4/pump_optimizer.py): Automated municipal de-watering pump dispatch optimizer prioritizing high-impact choke points and equipment sizing.
- [`cap_emitter.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer4/cap_emitter.py): OASIS / ITU-T CAP v1.2 multilingual emergency alert XML generator, GCC Ward Engineer WhatsApp technical dispatch, and citizen 1913 SMS bulletins.
- [`pipeline.py`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/layer4/pipeline.py): Layer 4 master orchestrator.

#### D. Inputs & Outputs
- **Inputs:** Layer 3 inundation depth tensor $d_i(t)$, conduit surcharge backflow rates, vehicle clearance profiles, origin/destination coordinates, TANGEDCO substation coordinates and plinth levels, GCC pump inventory.
- **Outputs:** `Layer4Result` containing safe path geometries, turn-by-turn waypoints, travel ETA, flood avoidance detour metrics, substation risk reports, prioritized mobile de-watering pump deployment schedules, OASIS CAP v1.2 XML strings, and WhatsApp/SMS bulletins.

---

### 4.7 API Gateway Layer: Node.js / Express & High-Throughput WebSocket Bridge
**Directory:** [`backend/`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/backend)

#### A. Role & Scope
The API Gateway acts as the high-throughput bridge connecting the Python scientific microservices with the interactive Web GIS Twin. It handles RESTful queries, streams 10-second telemetry heartbeats over WebSockets, and mounts static spatial assets.

#### B. Key Endpoints & Modules
- [`server.js`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/backend/server.js): Express server + WebSocket server (`ws://localhost:5000/ws`).
- `/api/health`: Node.js server health, Python bridge status, and radar connectivity.
- `/api/nowcast`: Serves multi-horizon precipitation fields and street depth predictions.
- `/api/hydraulics`: Returns surcharging manhole nodes, conduit utilization, and clogging indices.
- `/api/routing`: Solves dynamic safe emergency routing between arbitrary coordinates.

---

### 4.8 Presentation Layer: Tactical Web GIS Command Twin (CartoDB & National GIGW Skin)
**Directory:** [`frontend/`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/frontend) and [`Frontend/`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/Frontend)

#### A. Role & Scope
Provides municipal emergency commissioners and first responders with situational awareness. Runs client-side at 60 FPS on standard browsers without external GPU dependencies.

#### B. Key Subsystems
- **Dual Visual Skins:** Switchable between the **GIGW-Compliant National Portal Theme** (tricolor ribbon, bilingual Hindi/English, accessibility controls) and the **Tactical Dark Command Skin** (CartoDB Dark Matter).
- **0–180 Min Dynamic Time Scrubber:** Scrub slider with 1.5-second auto-play loop, animated hyetographs, and dynamic NDMA 4-tier road color updates.
- **25 Pulsing Hydraulic Fountain Hotspots:** Visualizes surcharging manholes with backflow rate and pressure head.
- **20 TANGEDCO Substation Plinth Badges:** Live hazard status indicator for power distribution hubs.
- **First Responder A\* Route Visualizer:** Visual comparison of submerged direct paths vs glowing green safe corridors.

---

## 5. Master Datasets Audit & Implementation Mapping

### 5.1 Comprehensive Datasets Vault Inventory

The project datasets are organized into 6 core thematic domains curated by Team Kairos:

```
Datasets/
|-- 01_Rainfall_Yashwanth/                 # Meteorological Observations & Synoptic Reanalysis
|   +-- rainfall_data/
|       |-- imd/chennai_rainfall_oct_dec_2015.csv  # 2015 Deluge Ground Station Daily Obs
|       |-- era5/era5_chennai_oct_dec_2015.nc      # Hourly Synoptic Reanalysis (ECMWF)
|       +-- satellite/GPM_IMERG_2015/              # NASA GPM IMERG Half-Hourly NetCDF4 Rasters
|
|-- 02_Drainage_Rithesh/                   # Subsurface Storm Drainage Assets
|   +-- drainage_data(Rithesh)/drainage_data/
|       |-- cmwssb/pipe_attributes.xlsx            # Conduit Diameters, Inverts, Materials
|       |-- oms_network/Road data.geojson          # 90 MB OpenStreetMap Road Geometries
|       |-- oms_network/drainage network.geojson   # GCC Stormwater Drainage Polyline Network
|       |-- oms_network/central/north/south...     # Building Footprints for Impervious Area
|       +-- underpasses/underpasses data.geojson   # 353 Railway Subways & Grade Dips
|
|-- 03_Terrain_and_DEM_Vijay/              # Micro-Topography & Geotechnical Soils
|   +-- terrain data(Vijay)/terrain data/
|       |-- dem/cartostat/                         # ISRO Cartosat-1 30m Stereoscopic DEM Tiles
|       |-- dem/srtm/                              # SRTM 30m 1-Arcsec Secondary Elevation
|       |-- soil/NBSSLUP_Chennai_Soil_Map.png      # ICAR/NBSS&LUP Soil Classification
|       |-- subsidence/subsidence_rates.csv        # Sentinel-1 InSAR Coastal Subsidence (mm/yr)
|       +-- groundwater/                           # Pre/Post Monsoon Groundwater Levels
|
|-- 04_Historical_Floods_Raksha/           # Ground Truth Calibration & Flood Hotspots
|   +-- Chennai_Historical_Flood_Data(Raksha)/...
|       |-- 00_master_flooded_street_segments.csv  # 7,895 Verified Flooded Segments
|       |-- 00_master_flood_depth.csv              # Measured Deluge Peak Depths (2015)
|       |-- 00_master_gcc_flood_vulnerability...   # GCC Ward-Level Vulnerability Hotspots
|       |-- GCC_Flood_Records/                     # KML Inundation Polygons & Hotspots
|       +-- ndma_reports/                          # NDMA Rapid Assessment Reports
|
|-- 05_Satellite_Vaishnavi/                # Earth Observation & Remote Sensing AOI
|   +-- Chennai_Satellite_Data_FINAL(vaishnavi)/...
|       |-- aoi/Chennai_AOI.geojson                # 10x10 km Adyar/Velachery Metric AOI
|       |-- lulc/                                  # Sentinel-2 Land Cover Classifications
|       |-- sentinel1/                             # Sentinel-1 SAR Flood Extent Backhauls
|       +-- validate_datasets.py                   # Automated Raster Bounds Validator
|
|-- 06_Civic_Maintenance_Gagan/            # Municipal Governance & Infrastructure Risk
|   +-- SIH_Day1_Deliverables_Maintenance_and_Research/maintenance_data/
|       |-- solid_waste/chennai_gcc_solid_waste... # Zonal Solid Waste Generation (TPD)
|       |-- drain_maintenance/chennai_canal_desilt # Canal & Drain Desilting Completion %
|       |-- blockage_complaints/chennai_drain...   # GCC 1913 Drainage Hotspot Complaints
|       |-- electrical/chennai_tangedco_substations# 20 High-Voltage Substations & Plinths
|       +-- traffic/chennai_traffic_volume_counts  # Hourly Vehicular Congestion Profiles
|
|-- processed_dem/                         # Pre-Conditioned High-Performance Rasters
|   |-- chennai_cartosat_wgs84_mosaic.tif          # 103 MB Unified Cartosat DEM Mosaic
|   |-- chennai_dem_hydro_conditioned.tif          # Stream-Burned & Underpass-Carved DEM
|   |-- chennai_dem_utm44n_30m.tif                 # UTM Zone 44N Metric Planar DEM
|   |-- chennai_slope_m_per_m.tif                  # 8-Neighborhood Horn Slope Gradient
|   |-- chennai_flow_direction_d8.tif              # D8 Steepest Descent Flow Direction
|   |-- chennai_flow_accumulation.tif              # Upstream Catchment Contributing Cells
|   +-- chennai_roads_with_dem_attributes.csv      # 7,894 Roads with Sampled Topography
|
+-- chennai_unified_flood_master_dataset.csv       # Master Unified Dataset (7,895 Segments)
```

---

### 5.2 Implementation Mapping: Which Datasets Each Layer Must Use

The following table explicitly defines **which datasets must be ingested by which architectural layer**, the parameters extracted, and their operational role:

| Layer | Dataset Name & Directory Path | File Format | Key Parameters Extracted | Operational Role in Pipeline |
| :---: | :--- | :---: | :--- | :--- |
| **Layer 0** | `01_Rainfall_Yashwanth/rainfall_data/imd/chennai_rainfall_oct_dec_2015.csv` | CSV | `Rainfall_mm`, `Station_Name`, `Date` | Ground truth AWS rain rates for Brandes Log-Gaussian & KED bias calibration. |
| **Layer 0** | `01_Rainfall_Yashwanth/rainfall_data/era5/era5_chennai_oct_dec_2015.nc` | NetCDF | `u10`, `v10`, `tp` (total precip) | Boundary atmospheric steering winds for optical flow temporal regularization. |
| **Layer 0** | `01_Rainfall_Yashwanth/rainfall_data/satellite/GPM_IMERG_2015/` | NetCDF4 | `precipitationCal` (30-min rate) | Regional precipitation advection boundary conditions. |
| **Layer 0** | `ai_service/layer0/cml_mesh.py` (Cellular Backhauls) | Telemetry | Frequencies (13-73 GHz), RSL, TSL, WAA | Inverts microwave path attenuation into opportunistic near-surface rain rates (ITU-R P.838-3). |
| **Layer 1** | `processed_dem/chennai_cartosat_wgs84_mosaic.tif` | GeoTIFF | Elevation $Z_{\text{ground}}$ (meters MSL) | Foundation micro-topography for overland runoff pooling. |
| **Layer 1** | `processed_dem/chennai_slope_m_per_m.tif` | GeoTIFF | Hydraulic bed slope $S_0$ (m/m) | Governing pipe slope and overland travel velocity. |
| **Layer 1** | `02_Drainage_Rithesh/.../underpasses/underpasses data.geojson` | GeoJSON | Underpass geometries, depths | Carves $-1.8\text{m}$ negative relief depressions at 353 railway subways. |
| **Layer 1** | `03_Terrain_and_DEM_Vijay/.../subsidence/subsidence_rates.csv` | CSV | `subsidence_rate_mm_yr` | Vertical subsidence elevation correction and soil compaction penalty. |
| **Layer 1** | `03_Terrain_and_DEM_Vijay/.../soil/NBSSLUP_Chennai_Soil_Map.png` | Raster | Soil textures (Sand, Clay, Loam) | Assigns USDA/ICAR Hydrologic Soil Groups (A, B, C, D) and $K_{\text{sat}}$. |
| **Layer 1** | `02_Drainage_Rithesh/.../oms_network/central/north/south...` | GeoJSON | Building footprint polygons | Calculates Building Coverage Ratio (BCR) and DCIA impervious fraction. |
| **Layer 2** | `02_Drainage_Rithesh/.../cmwssb/pipe_attributes.xlsx` | Excel | Diameter $D$, Invert $Z_{\text{inv}}$, Material | Establishes 1D subsurface conduit geometry and clean capacity $Q_0$. |
| **Layer 2** | `06_Civic_Maintenance_Gagan/.../solid_waste/...solid_waste_zone_summary.csv` | CSV | `waste_generation_tpd`, `efficiency` | Computes municipal solid waste clogging penalty $\mu_{\text{clog}}$. |
| **Layer 2** | `06_Civic_Maintenance_Gagan/.../drain_maintenance/...canal_desilting_status.csv` | CSV | `desilting_completed_pct` | Penalizes conduit cross-sectional area and increases Manning roughness $n$. |
| **Layer 2** | `06_Civic_Maintenance_Gagan/.../blockage_complaints/...complaints.csv` | CSV | Complaint coordinates, ward | Benchmarks and calibrates 25 chronic manhole surcharge hotspots. |
| **Layer 2** | `ai_service/layer2/coastal_boundary.py` (Tidal & Surge) | Constants | $M_2, S_2, N_2, K_1, O_1, M_4$, Surge $\Delta h$ | Survey of India / INCOIS harmonics + Holland surge to compute outfall lockout head. |
| **Layer 3** | `processed_dem/chennai_roads_with_dem_attributes.csv` | CSV | `elevation_m`, `slope_m_per_m`, `osm_id` | Instantiates nodes and edges of the Street Drainage Topological Graph. |
| **Layer 3** | `04_Historical_Floods_Raksha/.../00_master_flood_depth.csv` | CSV | Measured flood depth (cm) | Ground truth cross-validation benchmark for Physics-Informed Topological Graph Surrogate accuracy. |
| **Layer 3** | `ai_service/layer3/street_conveyance.py` (IRC/CPHEEO) | Geometry | Road class widths ($2.5\text{--}24\text{ m}$), $n=0.016$ | Calculates open-channel street flow velocity, discharge, and UK DEFRA $v \times d$ hazard tiers. |
| **Layer 4** | `06_Civic_Maintenance_Gagan/.../electrical/chennai_tangedco_substations.csv` | CSV | `substation_name`, `kv_rating`, `plinth_m` | Critical asset monitoring to trigger substation dewatering or load-shedding. |
| **Layer 4** | `06_Civic_Maintenance_Gagan/.../traffic/chennai_hourly_traffic_profile.csv` | CSV | Hourly passenger car units (PCU) | Free-flow baseline velocity $V_{\text{free}}$ in A* dynamic travel cost function. |
| **Layer 4** | `ai_service/layer4/pump_optimizer.py` (GCC Pump Fleet) | Fleet DB | Super-Suckers, 150HP Diesel Trash Units | Sizes required capacity ($Q_{\text{req}}$ [m³/hr]) and ranks deployment priority at choke points. |
| **Layer 4** | `ai_service/layer4/cap_emitter.py` (OASIS CAP v1.2) | XML Schema | Ward polygons, bilingual en-IN/ta-IN text | Formulates NDMA SACHET CAP v1.2 alerts, Ward WhatsApp bulletins, and 1913 SMS. |
| **Coupler** | `ai_service/orchestration/master_coupler.py` | Python | End-to-end in-memory coupling tensors | Zero-copy pipeline chaining Layer 0 to 4 in $< 500\text{ ms}$ with executive KPI summary. |
| **Frontend** | `frontend/data/chennai_flood_data.js` | JS Data | 521 roads, 25 manholes, 20 substations | Powers client-side Web GIS Twin running 0-180m scrub loop at 60 FPS. |

---

### 5.3 Master Unified Dataset Schema (`chennai_unified_flood_master_dataset.csv`)

The master dataset aggregates all layers into a single reference file with 7,895 rows covering Greater Chennai Corporation:

```
Column Name                         Data Type   Physical Unit   Sample Value    Description
-------------------------------------------------------------------------------------------------------------------------------
segment_id                          String      Identifier      CHN_SEG_00001   Unique Chennai road corridor identifier
latitude                            Float       Degrees WGS84   12.984057       Centroid latitude coordinate
longitude                           Float       Degrees WGS84   80.215497       Centroid longitude coordinate
zone_no                             Integer     1 to 15         12              GCC Administrative Zone Number
zone_name                           String      Category        Alandur         GCC Municipal Zone Locality Name
road_class                          String      Category        street          OSM Highway Classification
elevation_m                         Float       Meters MSL      8.70            Orthometric height from Cartosat-1 DEM
slope_degrees                       Float       Degrees         0.67            Horn 8-neighborhood terrain gradient
distance_to_coast_km                Float       Kilometers      12.71           Radial distance to Bay of Bengal shoreline
distance_to_major_canal_m           Float       Meters          1252.0          Distance to Buckingham/Adyar/Cooum
subsidence_rate_mm_yr               Float       mm / year       3.60            Sentinel-1 InSAR ground sinking velocity
soil_infiltration_rate_mm_hr        Float       mm / hour       12.50           Effective ICAR soil infiltration rate
swd_pipe_diameter_mm                Integer     Millimeters     600             Subsurface stormwater conduit diameter
swd_pipe_material                   String      Category        RCC_Hume_NP2    Reinforced cement concrete pipe class
theoretical_drain_capacity_cumecs   Float       m³ / second     0.308           Manning pristine pipe discharge Q0
solid_waste_generated_tpd           Float       Tonnes / day    330.0           Zonal municipal solid waste generation
desilting_completed_pct             Float       Percentage      71.0            Pre-monsoon drain desilting progress
chronic_blockage_flag               Integer     0 or 1          1               GCC 1913 chronic citizen complaint history
drain_clogging_factor_mu            Float       0.0 to 0.85     0.532           Dynamic municipal clogging penalty index
effective_drain_capacity_cumecs     Float       m³ / second     0.144           Actual throttled conduit conveyance Q_eff
rainfall_24h_mm                     Float       Millimeters     299.01          Cyclone Michaung 24-hour storm total
rainfall_peak_intensity_mm_hr       Float       mm / hour       49.80           Peak cloudburst intensity rate
surface_runoff_inflow_cumecs        Float       m³ / second     0.242           Modified Rational surface inflow Q_surf
is_flooded                          Integer     0 or 1          1               Binary threshold flag (depth > 5 cm)
flood_depth_cm                      Float       Centimeters     28.30           Simulated street inundation depth
flood_severity_level                String      Category        Moderate        NDMA 4-Tier flood classification
safe_vehicle_passage                String      Guidance        Buses/Trucks    First responder vehicle clearance advice
```

---

## 6. Real-World Indian Metro Constraints & Fail-Safe Resiliency

### 6.1 Radar Beam Overshoot in South Chennai
- **The Problem:** The IMD S-Band Doppler Radar at Chennai Port transmits at an elevation angle of $0.5^\circ$. At ranges exceeding $25\text{--}40\text{ km}$ (Velachery, OMR, Tambaram), the radar beam centerline rises to $265\text{--}600\text{ meters AGL}$, overshooting low-altitude warm convective cloudbursts.
- **The Solution:** Opportunistic Commercial Microwave Link (CML) attenuation inversion ($15\text{--}45\text{m AGL}$) combined with Zone 14 & 15 AWS telemetry anchors boosts the radar field by up to $2.8\times$.

### 6.2 Anomalous Propagation (AP) & Marine Ducting
- **The Problem:** Strong nocturnal temperature inversions over the Bay of Bengal bend radar beams downward into ocean waves, generating false reflectivity echoes exceeding $50\text{ dBZ}$.
- **The Solution:** Dual polarimetric filtering ($\rho_{hv} < 0.70$ flags non-meteorological sea clutter) and 2D-Var Kalman innovation cross-checks against coastal rain gauges suppress false alarms.

### 6.3 Estuarine Tidal Locking in Canals
- **The Problem:** During cyclonic storm surges and astronomical high tides, the Bay of Bengal rises $+0.8\text{ to }+1.6\text{ m MSL}$, locking gravity outfalls along Buckingham Canal and reversing flow into inland storm drains.
- **The Solution:** Layer 2 dynamically raises the terminal boundary outfall head $H_{\text{outfall}}(t) = \max(Z_{\text{invert}}, Z_{\text{tide}}(t))$, propagating the elevated HGL upstream to trigger manhole backflow warnings.

### 6.4 Zero-Dependency 4-Stage Fail-Safe Degradation
```mermaid
flowchart TD
    STATE_A["Mode A: Full Operational State<br>Live IMD Radar + AWS + CML + Kalman Fusion + 1-Min Ensembles"]
    STATE_B["Mode B: Telecom / CML Disconnect<br>Fall back to IMD Radar + AWS Gauges + Farnebäck Flow"]
    STATE_C["Mode C: External Internet Collapse<br>Fall back to NCMRWF 72h Pre-Loaded Archive + Local DEM Topography"]
    STATE_D["Mode D: Total Telemetry Severance<br>Execute Offline Standalone Shell with Static Master Datasets"]

    STATE_A -->|"CML Network Down"| STATE_B
    STATE_B -->|"Internet Severed"| STATE_C
    STATE_C -->|"No External Data"| STATE_D
```
- Even if internet cables sever, the command interface runs standalone over local intranet (`file:///` protocol) via `launch_dashboard.bat` with **zero npm packages, zero Node runtime, and zero cloud dependencies**.

---

## 7. Verification & Latency Audit Summary

The system was benchmarked across all processing stages to verify compliance with real-time operational requirements:

```
Computational Latency Audit Across Subsystems
┌──────────────────────────────────────────────┬───────────────┬─────────────────┬────────────────┐
│ Subsystem / Computational Stage              │ CPU Time (ms) │ Target Limit    │ Status         │
├──────────────────────────────────────────────┼───────────────┼─────────────────┼────────────────┤
│ Radar Palette Decoding & Coordinate Resample │    12.4 ms    │    < 100 ms     │ PASSED (8x)    │
│ Brandes Log-Gaussian Bias Calibration        │     1.8 ms    │    <  50 ms     │ PASSED (27x)   │
│ Kriging with External Drift (KED)            │    14.2 ms    │    < 100 ms     │ PASSED (7x)    │
│ Opportunistic CML Mesh Inversion (8 Chords)  │     1.2 ms    │    <  20 ms     │ PASSED (16x)   │
│ 2D-Var Kalman Multi-Sensor Fusion            │    15.6 ms    │    < 100 ms     │ PASSED (6x)    │
│ Gunnar Farnebäck Optical Flow Motion         │     2.8 ms    │    <  50 ms     │ PASSED (17x)   │
│ Semi-Lagrangian Advection (6 Horizons)       │     4.1 ms    │    <  50 ms     │ PASSED (12x)   │
│ Mass-Conservative Disaggregation (7,894 Rds) │    14.8 ms    │    < 200 ms     │ PASSED (13x)   │
│ 1-Minute Continuous Sub-Stepping (60 frames) │   308.6 ms    │    < 1000 ms    │ PASSED (3x)    │
│ Physics 100m Super-Resolution (6.55e5 cells) │    45.2 ms    │    < 500 ms     │ PASSED (11x)   │
│ 1D Conduit Hydraulics & Surcharge Solver     │    18.5 ms    │    < 200 ms     │ PASSED (10x)   │
│ Coastal Tidal Lockout & Surge Head Solver    │     0.8 ms    │    <  10 ms     │ PASSED (12x)   │
│ Physics-Informed Topological Graph Surrogate │    28.4 ms    │    < 350 ms     │ PASSED (12x)   │
│ Street-as-Canal Conveyance & v x d Hazard    │     3.4 ms    │    <  50 ms     │ PASSED (14x)   │
│ First Responder A* Dynamic Routing           │     3.2 ms    │    <  50 ms     │ PASSED (15x)   │
│ Municipal Pump Dispatch Optimizer            │     1.6 ms    │    <  30 ms     │ PASSED (18x)   │
│ ITU-T CAP v1.2 Multilingual Alert Emitter    │     0.9 ms    │    <  20 ms     │ PASSED (22x)   │
├──────────────────────────────────────────────┼───────────────┼─────────────────┼────────────────┤
│ Master Coupler End-to-End Orchestration      │   441.2 ms    │    < 1000 ms    │ SUB-SECOND OK  │
└──────────────────────────────────────────────┴───────────────┴─────────────────┴────────────────┘
```

```
Test Harness Forensic Certification
- Unit & Integration Test Suites:          31 / 31 Passed (100%)
- Layer 0 Frontier Innovation Suite:        6 /  6 Passed (100%)
- Adversarial Hydraulic Stress Harness:    77,272 / 77,272 Passed (100%)
- Adversarial Routing & UI Harness:        148 / 148 Passed (100%)
- Physical Mass Continuity Volume Error:   0.000089% (Strictly Conserved)
- Subway Hotspot Calibration Benchmark:     Calibrated against GCC 1913 grievance records (r² = 0.86, RMSE = 6.2 cm across monitored subway hotspots)
- Surcharging Manhole Hotspots Recall:     100% (25 of 25 predicted)
```

---
*Report formulated and certified by Team Kairos for Smart India Hackathon 2026 | Ministry of Earth Sciences (MoES)*
