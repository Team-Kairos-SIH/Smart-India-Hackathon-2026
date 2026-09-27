# KAIROS Frontend: Web GIS Tactical Command Twin & Interactive Viewers

**Smart India Hackathon 2026 | Problem Statement #26085**  
*Ministry of Earth Sciences (MoES) & National Centre for Medium Range Weather Forecasting (NCMRWF)*  
*Pilot Study: Greater Chennai Corporation (GCC) Disaster Management Command & Control Centre (Ripon Building)*

---

## 1. Overview & Dual-Frontend Architecture

KAIROS provides a multi-tier Web GIS visualization suite designed for urban flood nowcasting, municipal drainage orchestration, and emergency response dispatch. The repository features two complementary frontend implementations:

```
Smart-India-Hackathon-2026/
├── Frontend/                      # Modern React 19 + TypeScript + Vite Enterprise Command Twin
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/            # DashboardLayout (3-column HUD, status bars, header)
│   │   │   ├── widgets/           # MapWidget, CloggingWidget, TidalWidget, AlertsWidget,
│   │   │   │                      # PredictionsWidget, EmergencyRoutingDrawer, TwinLayerControl
│   │   │   └── twin3d/            # 3D Digital Elevation & Terrain Mesh Controls
│   │   ├── types/                 # TypeScript schemas & baseline flood models
│   │   ├── app.html               # Dedicated Command Twin entrypoint
│   │   └── index.html             # Main application entrypoint
│   └── radar_viewer.html          # Standalone Doppler Radar & CML telemetry visualizer
│
└── frontend/                      # Standalone, Zero-Build Vanilla Web GIS Tactical Viewers
    ├── index.html                 # Unified Tactical GIS Command Twin (Leaflet, 4D Scrubber, SITREP)
    ├── dem_viewer.html            # Cartosat-1 DEM & Micro-Depression Storage Basin Viewer
    ├── hydraulics_viewer.html     # SWD 1D Saint-Venant Conduit & Surcharge Network Viewer
    ├── inundation_viewer.html     # 2D Overland Diffusion Wave Flood Depth Viewer
    ├── routing_viewer.html        # Emergency 108 Ambulance A* Clearance Routing Engine
    └── data/                      # GeoJSON layers, DEM elevation grids, and flood polygons
```

### Architectural Distinctions

| Feature / Metric | Modern React Twin (`Frontend/`) | Standalone Viewers (`frontend/`) |
| :--- | :--- | :--- |
| **Framework** | React 19, TypeScript ~6.0, Vite 8 | Pure Vanilla JS (ES6+), Leaflet v1.9.4 |
| **Styling** | TailwindCSS v4 with `@tailwindcss/vite` | TailwindCSS CDN + Custom Glassmorphism CSS |
| **Target User** | GCC ICCC Incident Commanders & Municipal Chief Engineers | First Responders, Ward Engineers, Offline / Air-Gapped EOCs |
| **Build Requirement** | Node.js & Vite bundle pipeline (`npm run dev`) | Zero build; runs in any browser or static server |
| **Telemetry & State** | Reactive state, Lucide icons, Recharts SVG analytics | Direct DOM mutation, Leaflet GeoJSON layer groups, SVG sparklines |

---

## 2. REST API Integration Matrix

Both frontends communicate seamlessly with the **KAIROS AI Service Engine** (FastAPI backend running on `http://127.0.0.1:8000`) and the **Node.js Gateway Hub** (Express/WebSocket running on `http://127.0.0.1:5000`).

The tactical Web GIS Command Twin consumes the following core endpoints:

```
                            ┌─────────────────────────────────────────┐
                            │    KAIROS AI Engine (FastAPI:8000)      │
                            └────────────────────┬────────────────────┘
                                                 │
      ┌──────────────────┬───────────────────────┼───────────────────────┬──────────────────┐
      │                  │                       │                       │                  │
┌─────▼─────┐     ┌──────▼──────┐         ┌──────▼──────┐         ┌──────▼──────┐    ┌──────▼──────┐
│ What-If   │     │ Street Flow │         │ Municipal   │         │ CML Mesh    │    │ Coastal     │
│ Sandbox   │     │ Conveyance  │         │ Pump Recs   │         │ Telemetry   │    │ Outfalls    │
│ POST      │     │ GET         │         │ GET         │         │ GET         │    │ GET         │
│ /simulate/│     │ /street-flow│         │ /recommenda-│         │ /cml/       │    │ /coastal/   │
│ what-if   │     │             │         │ tions/pumps │         │ telemetry   │    │ outfalls    │
└───────────┘     └─────────────┘         └─────────────┘         └─────────────┘    └─────────────┘
      │                  │                       │                       │                  │
      └──────────────────┼───────────────────────┴───────────────────────┼──────────────────┘
                         │                                               │
                  ┌──────▼──────┐                                 ┌──────▼──────┐
                  │ Cross-Sect. │                                 │ CAP Alerts  │
                  │ Profile     │                                 │ (OASIS/ITU) │
                  │ GET         │                                 │ GET         │
                  │ /cross-     │                                 │ /alerts/    │
                  │ section     │                                 │ cap         │
                  └─────────────┘                                 └─────────────┘
```

### Tactical Endpoints Reference

#### 1. Incident Commander What-If Sandbox (`POST /api/simulate/what-if`)
- **Purpose**: Runs sub-50ms coupled physical simulations assessing storm intensity, tidal lockout, solid waste clogging, and de-watering pump deployment.
- **Request Body (JSON)**:
  ```json
  {
    "scenario": "michaung",
    "cloudburst_intensity_mm_hr": 85.0,
    "tidal_surge_m": 1.2,
    "clogging_factor": 0.45,
    "deployed_pumps_count": 8
  }
  ```
- **Response Payload**:
  ```json
  {
    "status": "success",
    "simulation_mode": "INCIDENT_COMMANDER_WHAT_IF",
    "latency_ms": 32.4,
    "parameters": {
      "scenario": "michaung",
      "cloudburst_intensity_mm_hr": 85.0,
      "tidal_surge_m": 1.2,
      "clogging_factor": 0.45,
      "deployed_pumps": 8
    },
    "impact_deltas": {
      "baseline_peak_depth_cm": 64.2,
      "mitigated_peak_depth_cm": 36.0,
      "depth_reduction_cm": 28.2,
      "flooded_corridors_relieved": 144,
      "outfalls_locked_out": 4
    },
    "coastal_outfall_status": [...],
    "recommended_pumps": [...]
  }
  ```
- **Frontend Usage**: Bound to the Incident Commander sandbox drawer. Changes to sliders immediately re-render inundation contours and display the net flood depth reduction $\Delta d$ in real time.

---

#### 2. Street-as-Canal Conveyance (`GET /api/street-flow`)
- **Query Parameters**:
  - `scenario` (*string*, default: `"michaung"`): Storm scenario identifier (`michaung`, `monsoon`, `2015_flood`).
  - `horizon` (*integer*, range: `15` to `180`, default: `60`): Prediction time step in minutes ($T+15\text{m}$ to $T+180\text{m}$).
- **Response Structure**:
  ```json
  {
    "status": "success",
    "scenario": "michaung",
    "horizon_min": 60,
    "summary": {
      "total_corridors_assessed": 6,
      "critical_washaway_hazards": 2,
      "max_flow_velocity_m_s": 2.14,
      "max_water_depth_cm": 95.0
    },
    "corridors": [
      {
        "segment_id": "SEG-5902",
        "road_name": "Vyasarpadi Ganesapuram Subway",
        "road_class": "secondary",
        "depth_cm": 95.0,
        "velocity_m_s": 2.14,
        "hazard_product_vd": 2.03,
        "hazard_rating": "EXTREME_WASH_AWAY"
      },
      {
        "segment_id": "SEG-1184",
        "road_name": "Velachery 100 Feet Road",
        "road_class": "primary",
        "depth_cm": 68.5,
        "velocity_m_s": 1.45,
        "hazard_product_vd": 0.99,
        "hazard_rating": "HIGH_HAZARD"
      }
    ]
  }
  ```
- **Frontend Usage**: Feeds the hydrodynamic vector glow layer on `MapWidget.tsx`, encoding corridor lines with animated dash-arrays and color-coding by Velocity $\times$ Depth ($v \times d$) human/vehicle wash-away hazard thresholds.

---

#### 3. Municipal Pump Dispatch Recommendations (`GET /api/recommendations/pumps`)
- **Query Parameters**:
  - `limit` (*integer*, range: `1` to `10`, default: `5`): Maximum number of pump deployment sites.
- **Response Structure**:
  ```json
  {
    "status": "success",
    "beneficiary": "Greater Chennai Corporation (GCC ICCC Ripon Building)",
    "recommended_pumps": [
      {
        "priority_rank": 1,
        "location": "Velachery 100 Feet Rd / Vijaya Nagar Junction",
        "recommended_capacity_hp": 100,
        "discharge_rate_m3_hr": 1200,
        "deployment_urgency": "CRITICAL",
        "target_relief_area_sqm": 45000,
        "expected_depth_drop_cm_per_hr": 14.5
      }
    ]
  }
  ```
- **Frontend Usage**: Displayed within the Emergency Dispatch Drawer and Inspection Modal, allowing the Incident Commander to confirm and route municipal mobile high-discharge dewatering pump units.

---

#### 4. CML Virtual Rain Gauge Telemetry (`GET /api/cml/telemetry`)
- **Query Parameters**:
  - `scenario` (*string*, default: `"michaung"`): Base meteorological event.
- **Response Structure**:
  ```json
  {
    "status": "success",
    "mesh_provider": "Opportunistic Cellular Tower Backhaul (Airtel / Jio 15-23 GHz)",
    "active_links_count": 28,
    "telemetry": [
      {
        "link_id": "CML-CHN-014",
        "tx_site": "Guindy Industrial Estate",
        "rx_site": "Velachery MRTS",
        "carrier_freq_ghz": 18.5,
        "baseline_rsl_dbm": -42.1,
        "current_rsl_dbm": -68.4,
        "attenuation_db_km": 5.26,
        "derived_rain_rate_mm_hr": 78.4,
        "confidence_score": 0.94
      }
    ]
  }
  ```
- **Frontend Usage**: Visualized in `radar_viewer.html` and the CML toggle layer in `MapWidget.tsx`, drawing wireless attenuation vectors between cell towers as opportunistic virtual rain gauges.

---

#### 5. Coastal Outfall Harmonics & Lockout (`GET /api/coastal/outfalls`)
- **Query Parameters**:
  - `tide_surge_m` (*float*, range: `0.0` to `3.0`, default: `0.85`): Bay of Bengal cyclonic storm surge above Mean High Water Spring (MHWS).
- **Response Structure**:
  ```json
  {
    "status": "success",
    "tidal_surge_applied_m": 0.85,
    "outfalls_total": 5,
    "outfalls_locked_out": 3,
    "outfalls": [
      {
        "name": "Cooum River Napier Bridge Mouth",
        "invert_elevation_m": 0.45,
        "sea_tide_level_m": 1.25,
        "status": "LOCKED_OUT",
        "backflow_danger": true,
        "discharge_efficiency_pct": 0.0
      },
      {
        "name": "Adyar Estuary (Pattinapakkam)",
        "invert_elevation_m": 0.75,
        "sea_tide_level_m": 1.25,
        "status": "LOCKED_OUT",
        "backflow_danger": true,
        "discharge_efficiency_pct": 12.0
      },
      {
        "name": "Buckingham Canal Sholinganallur Exit",
        "invert_elevation_m": 1.40,
        "sea_tide_level_m": 1.25,
        "status": "OPERATIONAL",
        "backflow_danger": false,
        "discharge_efficiency_pct": 74.0
      }
    ]
  }
  ```
- **Frontend Usage**: Renders pulsed outfall status icons on the Bay of Bengal coastline in both `TidalWidget.tsx` and the tactical Leaflet maps, alerting controllers of downstream drainage hydraulic locks.

---

#### 6. Public Safety CAP Alerts (`GET /api/alerts/cap`)
- **Query Parameters**:
  - `zone` (*integer*, range: `1` to `15`, default: `9`): Greater Chennai Corporation administrative zone number.
- **Response Structure**: Returns OASIS Common Alerting Protocol (CAP v1.2 / ITU-T X.1303) standardized XML alongside parsed bilingual English and Tamil alerts:
  ```json
  {
    "status": "success",
    "standard": "OASIS CAP v1.2 / ITU-T X.1303",
    "cap_xml": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<alert xmlns=\"urn:oasis:names:tc:emergency:cap:1.2\">...",
    "bulletins": {
      "zone_no": 9,
      "severity": "Severe",
      "urgency": "Immediate",
      "headline_en": "FLASH FLOOD & SUBWAY SURCHARGE WARNING",
      "headline_ta": "தீவிர திடீர் வெள்ளம் மற்றும் வடிகால் எச்சரிக்கை",
      "instructions_en": "Avoid flooded subways. Diversion in effect. Helpline: 1913.",
      "instructions_ta": "சுரங்கப்பாதைகளை தவிர்க்கவும். உதவிக்கு: 1913."
    }
  }
  ```
- **Frontend Usage**: Displayed in `AlertsWidget.tsx` and formatted into the 1-click official SITREP modal in `frontend/index.html` for broadcast over municipal loudspeaker networks, SMS gateways, and NDMA platforms.

---

#### 7. Street Cross-Section Profile (`GET /api/cross-section`)
- **Query Parameters**:
  - `road_name` (*string*, default: `"Duraisamy Subway / Usman Road"`): Selected road corridor.
  - `water_depth_cm` (*float*, default: `45.0`): Simulated surface flood depth in centimeters.
- **Response Structure**:
  ```json
  {
    "road_name": "Duraisamy Subway / Usman Road",
    "road_width_m": 14.0,
    "curb_height_cm": 15.0,
    "pavement_camber_pct": 2.5,
    "water_depth_cm": 45.0,
    "sidewalk_overtopped": true,
    "sidewalk_water_depth_cm": 30.0,
    "subsurface_pipe_dia_m": 0.90,
    "is_manhole_surcharging": true,
    "geyser_plume_height_cm": 18.9,
    "impassable_for": [
      "two_wheeler",
      "passenger_car",
      "ambulance"
    ]
  }
  ```
- **Frontend Usage**: Powers the interactive transversal elevation SVG canvas in the corridor inspection modal, detailing hydraulic curb overtopping and pressurized manhole geysers.

---

## 3. Deep Dive: Tactical Command Features

### 3.1 Incident Commander What-If Sandbox Controls

Disaster managers can simulate hypothetical interventions and evaluate immediate downstream effects without restarting the simulation kernel:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   INCIDENT COMMANDER WHAT-IF SANDBOX                   │
├────────────────────────────────────────────────────────────────────────┤
│  [ Scenario Preset ] : [ Michaung (2023) ▼ ]                           │
│                                                                        │
│  Cloudburst Rainfall Intensity                                         │
│  [============================●===========] 125 mm/h                   │
│                                                                        │
│  Bay of Bengal Tidal Surge                                             │
│  [===================●====================] 1.45 m (MHWS Lockout)      │
│                                                                        │
│  Municipal Solid Waste Drain Choking                                   │
│  [===============●========================] 48% Clogged                │
│                                                                        │
│  High-Discharge Mobile Dewatering Pumps                                │
│  [========================●===============] 12 Units Deployed          │
│                                                                        │
│  ----------------- REAL-TIME HYDRAULIC FEEDBACK ---------------------  │
│  Simulation Latency: 28.4 ms (Sub-50ms Edge Inference)                 │
│  Baseline Peak Depth: 74.8 cm  ──►  Mitigated Peak Depth: 39.2 cm     │
│  Net Inundation Relief: -35.6 cm (-47.6%)                              │
│  Relieved Road Corridors: 216 arterial segments                        │
│  Coastal Outfalls Locked: 4 / 5 outfalls impeded                       │
└────────────────────────────────────────────────────────────────────────┘
```

1. **Sub-50ms Simulation Engine**: Triggered on slider drag using throttled asynchronous POST calls to `/api/simulate/what-if`.
2. **Coupled Hydraulic Penalty Formulation**:
   $$\text{Depth}_{\text{mitigated}} = \text{Depth}_{\text{baseline}} \times \left(1.0 + (\text{Surge} - 0.5) \times 0.25\right) \times \left(1.0 + (\mu_{\text{clog}} - 0.35) \times 0.90\right) \times \max\left(0.40, 1.0 - N_{\text{pumps}} \times 0.055\right)$$
3. **Automated Pump Allocation**: Suggests exact ward locations (e.g. Duraisamy Subway, Usman Road, Madipakkam Lake Outlet) for 100 HP mobile pump sets to maximize flood reduction.

---

### 3.2 4D Continuous Temporal Scrubber ($0 - 180\text{m}$)

The command twin features a continuous temporal timeline located at the bottom-center HUD:

- **Time Horizon**: Seamless scrub from $T+0$ (Present Nowcast) to $T+180\text{m}$ (3-hour predictive outlook) in 1-minute increments with preset snap buttons ($T+0$, $T+30\text{m}$, $T+60\text{m}$, $T+90\text{m}$, $T+120\text{m}$, $T+180\text{m}$).
- **Dynamic Hyetograph Sparkline**: Embedded SVG hyetograph directly beneath the slider track, rendering real-time radar rainfall intensity curves ($0 - 120\text{ mm/h}$) with an amber vertical cursor synchronized to the current scrub position.
- **Client-Side Linear & Spline Interpolation**: Smooth 60 FPS transitions between discrete 15-minute hydraulic solver timesteps, dynamically recalculating:
  - Road segment glow intensities and surcharge percentages.
  - Manhole geyser status markers.
  - TANGEDCO power substation flood isolation warnings.
  - Impassable road networks for emergency vehicle routing.

---

### 3.3 Street Cross-Section Profile View (IRC:SP:50 & CPHEEO Compliant)

Clicking any corridor segment or subway node opens the **Street Transversal Cross-Section Profile**:

```
                       STREET CROSS-SECTION & DRAIN SURCHARGE
                         Corridor: Usman Road (T. Nagar)

     Sidewalk (Overtopped)      Carriageway (Camber: 2.5%)     Sidewalk (Overtopped)
          +0.15m                        0.00m                        +0.15m
     |░░░░░░░░░░░░░|                                            |░░░░░░░░░░░░░|
     |░░░░░░░░░░░░░|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|░░░░░░░░░░░░░|  ◄ Water: 45 cm
     |             |                 ▲                          |             |
     |             |                 │ Geyser Plume: 18.9 cm    |             |
     +-------------+                 │                          +-------------+
     ###################             │                      ###################
     ###################      ┌──────┴──────┐               ###################
     ###################      │ Surcharging │               ###################
     ###################      │   Manhole   │               ###################
                              └──────┬──────┘
                                     │
                             ( Subsurface SWD )
                             ( Pipe Dia: 0.9m )
                             (   Q > Q_cap    )
```

- **Pavement Geometry**: Displays a 14-meter multi-lane carriageway with IRC-mandated 2.5% transverse camber and 15 cm pedestrian sidewalk curbs.
- **Overtopping Indicator**: Flags when water depth exceeds the 15 cm curb height, computing the active water volume on pedestrian walkways.
- **Hydraulic Geyser Eruption Plume**: Dynamically computes surface water spouting when subsurface conduits transition to pressurized pipe flow:
  $$h_{\text{geyser}} = 0.42 \times d_{\text{water}} \quad (\text{for } d_{\text{water}} > 30\text{ cm})$$
- **Vehicle Impassability Matrix**:
  - **Two-Wheelers & Auto Rickshaws**: Impassable if $d_{\text{water}} > 18\text{ cm}$.
  - **Passenger Sedans / Hatchbacks**: Impassable if $d_{\text{water}} > 30\text{ cm}$ (air intake hydrolock danger).
  - **108 Ambulances / Light Fire Tenders**: Impassable if $d_{\text{water}} > 45\text{ cm}$ (chassis ground clearance breached).

---

## 4. Runbook & Development Quickstart

### Prerequisites
- **Node.js**: v18.0.0 or higher
- **npm**: v9.0.0 or higher
- **Python**: v3.10+ (for FastAPI backend)

---

### Option A: Running the Modern React/Vite Command Twin (`Frontend/`)

1. **Navigate to directory**:
   ```bash
   cd Frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start Vite development server**:
   ```bash
   npm run dev
   ```
   The application will start on:
   - Command Twin Dashboard: **`http://localhost:5173/app.html`** or **`http://localhost:5173/`**
   - Standalone Radar Viewer: **`http://localhost:5173/radar_viewer.html`**

4. **Production Build & Preview**:
   ```bash
   npm run build
   npm run preview
   ```

5. **Linting**:
   ```bash
   npm run lint
   ```

---

### Option B: Running the Standalone Tactical Viewers (`frontend/`)

The standalone viewers require **zero npm build steps** and can be served through any of the following methods:

#### Method 1: Via the Python FastAPI Backend (Recommended)
When the FastAPI microservice runs, it automatically mounts `frontend/` as static assets and serves `index.html` at the root URL:
```bash
# From repository root
uvicorn ai_service.api:app --reload --port 8000
```
- Tactical Command Twin: **`http://127.0.0.1:8000/`**
- Inundation Viewer: **`http://127.0.0.1:8000/inundation_viewer.html`**
- Hydraulics Viewer: **`http://127.0.0.1:8000/hydraulics_viewer.html`**
- Emergency Routing Viewer: **`http://127.0.0.1:8000/routing_viewer.html`**
- DEM Elevation Viewer: **`http://127.0.0.1:8000/dem_viewer.html`**

#### Method 2: Via the Node.js Express Gateway
```bash
# From repository root
cd backend
npm install
npm start
```
- Access at: **`http://127.0.0.1:5000/`**

#### Method 3: Via Python Built-in Static Server
```bash
# From repository root
python3 -m http.server 3000 --directory frontend
```
- Access at: **`http://127.0.0.1:3000/`**

#### Method 4: Direct Browser Execution (Air-Gapped / Field Deployment)
Open any HTML viewer directly in Google Chrome, Mozilla Firefox, or Microsoft Edge:
```bash
# Linux
xdg-open frontend/index.html

# macOS
open frontend/index.html
```

---

## 5. Directory & File Reference

```
Frontend/
├── app.html                       # Dedicated Vite entrypoint for KAIROS React Command Twin
├── index.html                     # Standard Vite single-page application entrypoint
├── package.json                   # Project dependencies and Vite build scripts
├── radar_viewer.html              # Doppler Weather Radar & CML attenuation viewer
├── tsconfig.app.json              # TypeScript application compiler options
├── tsconfig.json                  # Root TypeScript configuration
├── tsconfig.node.json             # TypeScript Node environment configuration
├── vite.config.ts                 # Vite bundler configuration with TailwindCSS v4 plugin
├── public/
│   └── data/                      # Client-side cached flood and arterial vector datasets
└── src/
    ├── main.tsx                   # React root hydration entrypoint
    ├── App.tsx                    # Root application component wrapper
    ├── index.css                  # Global Tailwind imports & custom HUD glassmorphism utility classes
    ├── App.css                    # Component animations & glow filters
    ├── types/
    │   └── floodData.ts           # Arterial road networks, manhole surcharge & substation schemas
    └── components/
        ├── layout/
        │   ├── DashboardLayout.tsx# 3-column tactical mission layout with header & status indicators
        │   └── Sidebar.tsx        # Collapsible navigation drawer
        ├── twin3d/                # 3D digital elevation & terrain visualization components
        └── widgets/
            ├── MapWidget.tsx      # Leaflet 2D/3D dual-mode interactive arterial flood map
            ├── CloggingWidget.tsx # Dynamic solid waste clogging index slider & gauge
            ├── TidalWidget.tsx    # Bay of Bengal tidal stage harmonics & outfall lock indicator
            ├── AlertsWidget.tsx   # Surcharge hotspot list with CAP severity badges
            ├── PredictionsWidget.tsx # Recharts flood depth temporal trend area chart
            ├── EmergencyRoutingDrawer.tsx # 108 ambulance A* routing clearance calculator
            ├── InspectionDetailModal.tsx  # Street cross-section & manhole geyser analysis modal
            └── TwinLayerControl.tsx       # GIS layer visibility & display mode switcher
```

---

## 6. Verification & Quality Assurance

To verify that the frontend functions properly with the backend:

1. Launch the FastAPI service:
   ```bash
   uvicorn ai_service.api:app --port 8000
   ```
2. Verify API health check:
   ```bash
   curl -s http://127.0.0.1:8000/api/health | jq .
   ```
3. Test What-If tactical simulation endpoint:
   ```bash
   curl -s -X POST http://127.0.0.1:8000/api/simulate/what-if \
     -H "Content-Type: application/json" \
     -d '{"scenario":"michaung","cloudburst_intensity_mm_hr":80.0,"tidal_surge_m":1.0,"clogging_factor":0.4,"deployed_pumps_count":5}' | jq .
   ```
4. Test Street Cross-Section profile endpoint:
   ```bash
   curl -s "http://127.0.0.1:8000/api/cross-section?water_depth_cm=50.0" | jq .
   ```
5. Launch the React dev server:
   ```bash
   cd Frontend && npm run dev
   ```
   Open `http://localhost:5173/` in your browser. All tactical layers, dynamic scrubber controls, and modal cross-section views will be fully interactive.
