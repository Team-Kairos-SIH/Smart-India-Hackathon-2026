# SLIDE 3 — VISUAL SLIDE DESIGN & PRESENTATION PLAN
## Team KAIROS · SIH 2026 · PS #26085 · JSS011
### Ministry of Earth Sciences (MoES) / NCMRWF × Greater Chennai Corporation (GCC)

---

## 🎨 SLIDE CANVAS SPECIFICATIONS

* **Slide Canvas Aspect Ratio:** 16:9 Widescreen ($1920 \times 1080$ px).
* **Background Style:** Pure White (`#FFFFFF`) canvas with soft Tiranga studio ambient glare:
  * Top Edge: Soft Saffron glow (`#FF9933`, $\alpha = 0.15$)
  * Bottom Edge: Soft India Green glow (`#138808`, $\alpha = 0.12$)
  * Center Canvas: Pure white (`#FFFFFF`) for crisp reading
* **Header Bar:**
  * Title: **TECHNICAL APPROACH & SYSTEM ARCHITECTURE** (Bold, Slate 900 `#0F172A`, 24 pt)
  * Subtitle: *KAIROS: Coupled Radar Ingestion to Subsurface Hydraulics & Street Depth Nowcasting* (Italic, Slate 600 `#475569`, 11 pt)
  * Header Badges: `MoES / NCMRWF` | `SIH 2026 Grand Finale` | `PS #26085` | `Team KAIROS`

---

## 📐 3-COLUMN BENTO-BOX LAYOUT BLUEPRINT

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ SLIDE HEADER: TECHNICAL APPROACH & SYSTEM ARCHITECTURE                                                 │
│ Subtitle: KAIROS: Coupled Radar Ingestion to Subsurface Hydraulics & Street Depth Nowcasting          │
├───────────────────────────────┬────────────────────────────────────────┬───────────────────────────────┤
│ COLUMN 1: DATA INGESTION      │ COLUMN 2: HYDROMETEOROLOGICAL ENGINE   │ COLUMN 3: ACTIONABLE DELIVERY │
│ (White Card / Slate Header)   │ (Tactical Dark Navy Container #0F172A) │ (White Card / Slate Header)   │
│                               │                                        │                               │
│ 📡 IMD / NIOT X-Band Radar    │ 🌀 PySTEPS Optical Flow Advection     │ 🚨 Civic Alert Webhooks       │
│    Sweep: 10-min, Z=130 R^1.4 │    Velocity fusion: u_fused, v_fused   │    JSON REST API (/api/route) │
│                               │                                        │                               │
│ 📶 Telecom CML Links          │ 🌊 Modified Rational Runoff Q_surf    │ 🚑 Dynamic Arrival-Time A*    │
│    ITU-R P.838-3 attenuation  │    C_impervious = 0.92, SCS-CN HSG A-D │    4 Vehicle Clearance Profiles│
│                               │                                        │                               │
│ 🌧️ 35 GCC AWS Rain Gauges     │ 🕳️ 1D SWMM & Dynamic Silt Clogging     │ ⚡ 15cm Plinth Protection     │
│    Brandes log-Gaussian gain  │    μ ∈ [0.05, 0.85] → Q_geyser 390L/s │    20 Substations + 5 O2 Plants│
│                               │                                        │                               │
│ 🗺️ Cartosat-1 5m DEM          │ 🧠 PI-GNN Surrogate & Mass QP          │ 🖥️ Tactical WebGIS Command    │
│    -2.5m culvert, -2.0m sag   │    < 28.5 ms CPU, Mass Error ≤0.000089%│    60 FPS Leaflet Dual-Skin   │
├───────────────────────────────┴────────────────────────────────────────┴───────────────────────────────┤
│ BOTTOM TECH STACK BAR: Python 3.13 | FastAPI | PySTEPS | NetworkX | PyTorch | PostGIS | Leaflet WebGIS   │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 DETAILED COLUMN-BY-COLUMN SLIDE CONTENT

---

### COLUMN 1: Multi-Sensor Ingestion Layer
> **Visual Box:** White container card with Slate header bar (`#0F172A`). Accent border: Sky Blue (`#0284C7`).

* **Card 1.1 — Atmospheric Radar & Gauges:**
  * Tag: `LAYER 0: ATMOSPHERIC INGESTION`
  * Text: NIOT Pallikaranai X-band radar sweeps ($10\text{-min}$ cadence) calibrated via 35 GCC Automatic Rain Gauges (AWS).
  * Formula Badge: $Z = 130 R^{1.4}$ *(Maritime downpour re-calibration)*
* **Card 1.2 — Telecom CML Attenuation Mesh:**
  * Tag: `TELECOM CML BACKHAUL`
  * Text: 15 commercial microwave links (Airtel/Jio 15–45 GHz) filling radar blind spots in coastal convective cells.
  * Formula Badge: $R = (k / a)^{1/b}$ *(ITU-R P.838-3 inversion)*
* **Card 1.3 — Micro-Topography & Surface Mesh:**
  * Tag: `LAYER 1: DEM & HYDRO-CONDITIONING`
  * Text: ISRO Cartosat-1 5m DEM with hydro-enforced culvert trenching ($-2.5\text{m}$) and underpass sag carving ($-2.0\text{m}$).

---

### COLUMN 2: Coupled Hydro-Meteorological Engine (The Core Hero Container)
> **Visual Box:** **Tactical Dark Navy (`#0F172A`)** central hero container with Neon Emerald (`#10B981`) and Amber (`#F59E0B`) text badges. This draws the evaluator's eyes directly to your core innovation.

* **Card 2.1 — Optical Flow Storm Tracking:**
  * Tag: `PYSTEPS OPTICAL FLOW NOWCAST`
  * Mechanism: Farnebäck semi-Lagrangian backward advection projecting 6 forecast horizons ($T+15\text{m}$ to $T+180\text{m}$) in **~2.8 ms advection latency**.
* **Card 2.2 — Subsurface Pipe Clogging & Geyser Surcharge:**
  * Tag: `LAYER 2: 1D SWMM CONDUIT HYDRAULICS`
  * Formula Badge: $Q_{\text{geyser}} = C_d A_{\text{lid}} \sqrt{2g(\text{HGL} - Z_{\text{ground}})}$
  * Mechanism: 1,894 km GCC SWD multigraph with dynamic waste clogging modifier $\mu \in [0.05, 0.85]$ parameterized from GCC TPD waste logs. Manholes erupt pressurized geysers at **~390 L/s**.
* **Card 2.3 — PI-GNN Neural Surrogate & Mass Conservation:**
  * Tag: `LAYER 3: PHYSICS-INFORMED NEURAL SURROGATE`
  * Formula Badge: $\min \frac{1}{2} \sum A_i (h_i^* - h_i)^2 \quad \text{s.t.} \quad \sum A_i h_i^* = V_{\text{target}}$
  * Metric Callout: **< 28.5 ms CPU Latency** ($120,000\times$ faster than 2D SWE) | **Mass Error $\le 0.000089\%$**.

---

### COLUMN 3: Actionable Tactical Delivery Layer
> **Visual Box:** White container card with Slate header bar (`#0F172A`). Accent border: India Green (`#15803D`).

* **Card 3.1 — Time-Dependent Emergency Dispatch Routing:**
  * Tag: `LAYER 4: ARRIVAL-TIME A* ROUTING`
  * Mechanism: Evaluates flood depth at predicted vehicle arrival time $t_{\text{arr}} = t_0 + \sum \Delta t_e$ using Water Hazard Penalty Function (WHPF) across 4 vehicle wading profiles (10cm Bike, 18cm Car, 30cm Ambulance, 45cm NDRF Truck). Includes **30-minute underpass lookahead**.
* **Card 3.2 — Critical Infrastructure Protection:**
  * Tag: `PLINTH MARGIN SAFEGUARD`
  * Mechanism: Protects **20 TANGEDCO 230kV/110kV substations** & **5 hospital medical O₂ depots** using the **15 cm Plinth Margin Rule** ($\Delta Z_{\text{plinth}} \le 15\text{ cm} \implies$ dewatering pump dispatch).
* **Card 3.3 — Command Center WebGIS Twin:**
  * Tag: `COMMAND CENTER WEBGIS`
  * Mechanism: Standalone 60 FPS Leaflet WebGIS Command Twin (GIGW Light & Dark modes) serving live REST API payloads (`/api/nowcast`, `/api/route`, `/api/assets`).

---

---

## 🧮 4 GOVERNING EQUATIONS TO HIGHLIGHT ON CANVAS

Ensure these 4 equations appear in clean formula badges on Slide 3 — MoES and NCMRWF scientists verify these:

1. **Maritime Radar Calibration:**
   $$Z = 130 R^{1.4} \implies R = \left(\frac{10^{\text{dBZ}/10}}{130}\right)^{0.714}$$
2. **Dynamic Drain Conveyance with Clogging ($\mu \in [0.05, 0.85]$):**
   $$Q_{\text{cap}} = \frac{1}{n_0(1 + 1.8\mu)} \cdot A_0(1 - \mu) \cdot \left[R_{h0}\sqrt{1-\mu}\right]^{2/3} \cdot S_0^{1/2}$$
3. **Torricelli Orifice Manhole Geyser Eruption:**
   $$Q_{\text{backflow}} = C_d A_{\text{lid}} \sqrt{2g(\text{HGL}_i - Z_{\text{street}, i})} \quad (C_d = 0.62, \; D_{\text{lid}} = 0.60\text{m})$$
4. **Analytical Closed-Form Convex Mass Conservation Projection:**
   $$P_{\text{mass}}: \quad \min_{\mathbf{h}^* \ge 0} \frac{1}{2} \sum_{i=1}^N A_i (h_i^* - h_i)^2 \quad \text{subject to} \quad \sum_{i=1}^N A_i h_i^* = V_{\text{target}}$$

---

---

## 🎙️ 45-SECOND PITCH SCRIPT FOR SLIDE 3

> *"Judges, Slide 3 shows our 5-Layer hydro-meteorological architecture.*
>
> *In **Layer 0**, we ingest NIOT X-band Doppler radar, 35 rain gauges, and commercial microwave links from telecom towers. Using PySTEPS optical flow, we project cloudburst trajectories across 6 time horizons in under 3 milliseconds.*
>
> *In **Layers 1 and 2**, we hydro-condition Cartosat 5m DEM topography and route runoff into Chennai’s 1,894 km drain network. Unlike competitors who assume pristine pipes, we model dynamic silt clogging ($\mu \in 0.05\text{--}0.85$) from GCC waste logs, predicting pressurized manhole geysers erupting at 390 liters per second.*
>
> *In **Layer 3**, our Physics-Informed Graph Neural Surrogate solves 7,894 street depths in **under 28.5 milliseconds on CPU** with **less than 0.000089% mass conservation error**—$120,000\times$ faster than 2D solvers.*
>
> *Finally in **Layer 4**, our arrival-time A* engine routes ambulances around future flood crests and enforces the 15 cm plinth rule to protect 20 electrical substations and 5 hospital oxygen depots from city-wide blackouts."*

---

> *Team KAIROS · JSS011 · SIH 2026 PS #26085 · Ministry of Earth Sciences / NCMRWF × Greater Chennai Corporation*
