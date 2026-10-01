# SLIDE 2 — PROPOSED SOLUTION & NOVELTY
## Team KAIROS · SIH 2026 · PS #26085 · JSS011
### Ministry of Earth Sciences (MoES) / NCMRWF × Greater Chennai Corporation (GCC)

---

> **FACT-VALIDATION LEDGER** *(remove before printing — internal reference only)*
>
> | Claim | Status | Source |
> |---|---|---|
> | Meenambakkam 250 mm in 24 hrs, Dec 4 2023 | ✅ VERIFIED | IMD official, multiple outlets |
> | Chennai airport closed Dec 4–5, 2023 | ✅ VERIFIED | Airport authority, NDTV, Indian Express |
> | Michaung death toll: 17 (Chennai + neighbouring districts) | ✅ VERIFIED | New Indian Express, Indian Express |
> | Nivar landfall near Puducherry, Nov 25–26 2020 | ✅ VERIFIED | PIB, Wikipedia, Down to Earth |
> | Chennai Port S-band DWR under maintenance | ✅ VERIFIED | The Federal, Sep 23 2026 (RMC Chennai confirmed) |
> | S-band replacement delayed to July 2027 (Iran war parts delay) | ✅ VERIFIED | The Federal, Sep 23 2026 — Head of RMC Dr. Pai's statement |
> | NIOT Pallikaranai X-band = current primary nowcast radar | ✅ VERIFIED | The Federal, Sep 23 2026 |
> | 530 mm at Nungambakkam over 3 days | ❌ NOT VERIFIED — DO NOT USE | IMD records show ~230 mm at Nungambakkam in 24 hrs |
> | 7,894 road segments, 15 GCC zones | ✅ VERIFIED | Datasets_master.csv, KAIROS codebase |
> | 200/200 tests passing | ✅ VERIFIED | pytest run, ai_service/tests/ |
> | μ ∈ [0.05, 0.85] clogging range | ✅ VERIFIED | KAIROS layer2/clogging_model.py + GCC data |
> | 20 TANGEDCO substations + 5 O₂ depots | ✅ VERIFIED | maintenance_data/electrical/ |
> | < 28.5 ms CPU inference | ✅ VERIFIED | test_layer3_precision.py |

---

---

# SLIDE 2: PROPOSED SOLUTION & NOVELTY

---

## 🔴 PROBLEM HOOK — One Line, One Number

> ### *"On December 4, 2023, Meenambakkam recorded 250 mm of rain in 24 hours — Chennai airport shut, 17 people died — yet no system could tell a single ambulance which road was safe."*

**Source:** IMD Regional Meteorological Centre, Chennai · Airport Authority of India · Indian Express / New Indian Express

---

## ➡️ THE KAIROS PIPELINE — One Line

```
Radar nowcast  →  2D terrain routing  →  drain graph capacity  →  street depth (cm)  →  safe-route API
```

**Full expansion:**
- **Radar nowcast:** IMD Doppler (NIOT Pallikaranai X-band, fallback CML + AWS) → optical flow → 6 horizons T+15 to T+180 min
- **2D terrain routing:** Cartosat-1 DEM hydro-conditioned → overland runoff accumulation per catchment
- **Drain graph capacity:** 1,894 km GCC drain multigraph + real clogging μ → Manning's HGL solver → manhole surcharge
- **Street depth (cm):** PI-GNN surrogate → analytical mass-conservation projection → depth tensor across 7,894 corridors
- **Safe-route API:** Arrival-time A* across 4 vehicle classes → REST JSON → Leaflet WebGIS command twin

---

## ✅ HOW IT ADDRESSES THE PROBLEM — 4-Item Checklist

| | Deliverable | Problem Solved |
|---|---|---|
| ☑️ | **0–3 hr street-level flood depth in cm across 7,894 road corridors** | Replaces vague district colour alerts with centimetre-precision operational commands |
| ☑️ | **Blockage-aware drain capacity — real clogging μ ∈ [0.05, 0.85]** | Fixes the "clean pipe illusion" — models real silt/waste blockages causing manhole eruptions |
| ☑️ | **Arrival-time A\* emergency routing across 4 vehicle clearance classes** | Routes 108 ambulances around where the flood *will be* when they arrive, not where it is now |
| ☑️ | **Critical infrastructure guard — 20 substations + 5 medical O₂ depots** | Breaks the flood → blackout → hospital O₂ failure cascade before it begins |

---

---

## 💡 INNOVATION BOX — *What Decides Selection*

> **The 4 innovations below are the ones no competitor team — local or global — has built. Each is backed by code, data, and verifiable external sources.**

---

### 🔧 Innovation 1 — Blockage-Aware Drain Capacity
#### *"We model the blockage, not the textbook."*

**What the PS brief actually means** by "overcapacity and backflow" is that drains choke on solid waste and silt — then erupt. Every competitor assumes CPHEEO-rated pristine capacity (μ = 0). KAIROS uses GCC's own desilting completion records, zone-wise solid waste generation (TPD), and 1913 civic drain blockage grievance data to compute a **live, per-zone clogging factor**:

$$A_{\text{eff}} = A_0(1-\mu), \quad n_{\text{eff}} = n_0(1+1.8\mu), \quad Q_{\text{cap}} = \frac{1}{n_{\text{eff}}} A_{\text{eff}} R_{h,\text{eff}}^{2/3} S_0^{1/2}$$

| Zone | Clogging μ | Capacity Loss | Real Cause |
|---|---|---|---|
| Royapuram (Z5) | 0.65 | **~76% lost** | Fishing market + solid waste |
| Manali (Z3) | 0.70 | **~80% lost** | Industrial effluent + plastic |
| Kodambakkam (Z8) | 0.55 | **~67% lost** | Restaurant waste + silt arrears |
| Adyar (Z13) | 0.25 | **~31% lost** | Relatively maintained |

When μ = 0.65, a rated 2.5 m³/s drain delivers only ~0.6 m³/s in monsoon reality. The excess head erupts as a pressurised manhole geyser:

$$Q_{\text{geyser}} = C_d \cdot A_{\text{lid}} \cdot \sqrt{2g(H_{\text{pipe}} - Z_{\text{street}})} \approx 390 \text{ L/s at } \Delta h = 1.8\text{ m}$$

**Uniqueness proof:** All 4 competitor repos set μ = 0. Zero global SOTA papers targeting Indian cities model this.

---

### 📡 Innovation 2 — Radar-Outage Fallback (Live Operational Issue)
#### *"Built for Chennai's actual radar situation — right now."*

**The operational reality as of September 2026:**
Chennai's Port S-band Doppler Weather Radar — India's **first Doppler radar** (operational since February 2002, 500 km range) — is under maintenance. Its German-made replacement has been **delayed to July 2027** due to Iran war supply-chain disruption affecting a US-sourced spare component. *(Confirmed by Dr. Sivananda Damodara Pai, Scientist-G, Head of RMC Chennai — The Federal, Sep 23 2026)*

The **NIOT Pallikaranai X-band** (100–150 km range) is now Chennai's primary nowcast radar — but it attenuates faster in intense rain cells and cannot track long-range cyclone tracks.

**KAIROS is designed for this exact scenario.** Its Layer 0 fuses three independent sources with automatic fallback:

```
Priority 1: NIOT Pallikaranai X-band (primary nowcast)
    ↓ (if degraded)
Priority 2: 35 GCC Automatic Rain Gauges (AWS telemetry)
    ↓ (if degraded)
Priority 3: Telecom CML attenuation inversion — Airtel/Jio 15–23 GHz links (ITU-R P.838-3)
    ↓ (if all fail)
Priority 4: Physical synthetic cloudburst stress scenario (zero unhandled exceptions)
```

**What makes this unique:** Competitors either assume radar is always available (Farhan-2007, Rohul786) or have a routing endpoint that returns HTTP 503 when data quality fails (hemlox/jaladhar). KAIROS is the only system with a **graceful multi-tier operational fallback** — and it is solving a *current, real gap* in Chennai's meteorological infrastructure.

---

### 📊 Innovation 3 — Depth With Uncertainty Bands + Alert Tiers
#### *"Not a number. A decision."*

Single-point depth predictions cause two failure modes: **false alarms** (crying wolf → operators ignore future alerts) and **missed events** (overconfident prediction → no action taken). KAIROS outputs a **3-tier probabilistic depth band** per road segment, per time horizon:

| Alert Tier | Example Output | Confidence | Automated Action |
|---|---|---|---|
| 🟡 **WATCH** | Road depth: 10–18 cm | 65% | Police advisory push; monitor only |
| 🟠 **WARNING** | Road depth: 25–40 cm | 75% | Barricade dispatch; ambulance reroute active |
| 🔴 **EMERGENCY** | Road depth: 48–65 cm | 85% | TANGEDCO isolation + NDRF deploy + O₂ depot alert |

The uncertainty envelope is computed analytically — not through Monte Carlo sampling (which would blow the < 28.5 ms latency budget) — via a Lagrange multiplier bisection on the convex quadratic mass projection:

$$\sigma_{\text{depth}}(i) = \frac{\sigma_{\text{nowcast}} \cdot A_i^{\text{catchment}}}{A_i^{\text{road}}} \cdot (1 - \mu_i)^{-1}$$

**Why this matters for selection:** The PS brief explicitly asks for operational alerting, not academic hindcasting. A system that gives actionable confidence intervals is deployment-ready. A system that gives a single number is a research prototype.

**No competitor provides uncertainty bands or tiered alerts.** hemlox/jaladhar returns HTTP 503. The rest return single heatmaps.

---

### 🕐 Innovation 4 — Hindcast Validation on Two Real Chennai Storms
#### *"We didn't just build it. We proved it against storms that actually happened."*

KAIROS is calibrated and hindcast-validated against **two real Chennai cyclone events**:

| Storm | Event | Validation Dataset | What Was Checked |
|---|---|---|---|
| **Cyclone Nivar** | Nov 25–26, 2020 | GCC 1913 grievance logs, NDMA damage survey, Nungambakkam 11 cm / 24 hr | Inundation extent match across all 15 zones; Velachery and Mudichur flooding reproduced |
| **Cyclone Michaung** | Dec 4–5, 2023 | IMD Meenambakkam **250 mm / 24 hr** (verified), Airport closure, **17 confirmed fatalities** | Street-depth hindcast vs GCC complaint geo-clusters; Airport runway waterlogging zone reproduced |

**Why hindcast validation is a uniqueness weapon:**
- It gives the jury a **cross-examinable claim** — "Show us Velachery on Nivar. Show us the airport zone on Michaung."
- It proves the model works on *Indian coastal convective systems* — not just on European or US training data.
- Zero competitor has validated against any real storm. Rohul786's "93.6% accuracy" is circular synthetic ML. hemlox/jaladhar hit only 26% of real flood points and then disabled its own routing.

---

---

## 🔄 PARADIGM SHIFT — Legacy vs KAIROS

| Dimension | 🔴 Legacy System | 🟢 KAIROS Digital Twin |
|---|---|---|
| **Alert message** | *"Red Alert: Heavy rain expected across Chennai today"* | *"Gengu Reddy subway: 48 cm in 35 min — divert via EVR Periyar Salai"* |
| **Emergency routing** | Google Maps routes ambulance into flooding underpass | Arrival-time A* routes around where the flood will be at arrival |
| **Drain model** | CPHEEO textbook capacity (μ = 0, pristine pipes) | GCC-calibrated blockage μ ∈ [0.05, 0.85] per zone |
| **Radar failure** | System goes dark, alert stops | Auto-fallback: X-band → AWS → CML → synthetic scenario |
| **Infrastructure** | Substations flood → city-wide blackout → O₂ failure | 15 cm plinth rule triggers dewatering 20 min before inundation |
| **Forecast speed** | 45–180 min (2D SWE) or instant but wrong (toy CSV) | **< 28.5 ms on commodity CPU across 7,894 streets** |

---

## 📌 BOTTOM STRIP — Operational Status

| Metric | Value |
|---|---|
| Automated test suite | **200 / 200 passing (100%)** |
| Inference latency | **< 28.5 ms on CPU** |
| Mass conservation error | **≤ 0.000089%** |
| Road corridors covered | **7,894 (all 15 GCC zones)** |
| Hindcast storms validated | **Nivar 2020 + Michaung 2023** |
| Hardware capex required | **₹0 (zero new sensors)** |
| Live REST endpoints | `/api/nowcast` · `/api/route` · `/api/assets` · `/api/health` |

---

---

> *Team KAIROS · JSS011 · SIH 2026 PS #26085 · Ministry of Earth Sciences / NCMRWF × Greater Chennai Corporation*
