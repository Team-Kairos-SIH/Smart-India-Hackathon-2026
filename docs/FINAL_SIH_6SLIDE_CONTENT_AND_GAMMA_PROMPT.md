# KAIROS — SIH 2026 IDEA PRESENTATION: FINAL VERIFIED SLIDE CONTENT & GAMMA PROMPT
## Problem Statement 26085: Urban Flood Nowcasting System (Drainage and Rainfall Coupling)
### Ministry of Earth Sciences (MoES) / NCMRWF | Theme: Disaster Management | Category: Software
**Team ID:** JSS011 | **Team Name:** Team KAIROS | **Idea Title:** KAIROS - Street-Level Urban Flood Digital Twin

---

## PART 1: EXACT SLIDE-BY-SLIDE CONTENT (PAGES 1 TO 6)

### SLIDE 1: Title Page
**Layout:** Official SIH title layout. Left: bulleted project identity. Right: SIH brain-bulb graphic & system badge. Header: KAIROS logo (top-left), SIH 2026 logo (top-right). Footer: `@SIH Idea submission`.

- **Event:** SMART INDIA HACKATHON 2026
- **Idea Title:** KAIROS - Street-Level Urban Flood Digital Twin
- **Problem Statement ID:** 26085
- **Problem Statement Title:** Urban Flood Nowcasting System (Drainage and Rainfall Coupling)
- **Theme:** Disaster Management
- **Category:** Software
- **Team ID:** JSS011
- **Team Name:** Team KAIROS
- **Operational One-Liner:** From passive regional rainfall alerts to street-level flood depth and emergency routing within 30 minutes.

---

### SLIDE 2: Proposed Solution
**Header:** Proposed Solution | **Sub-header:** KAIROS - Street-Level Urban Flood Digital Twin
**Layout:** Left card: Problem (3 bullets). Center: 5-step horizontal coupled workflow. Right: What Makes KAIROS Unique (5 cards). Bottom banner: From -> To operational contrast. Footer: `@SIH Idea submission`.

#### [Card 1: Problem — Why Current Systems Fall Short]
- Rain forecasts report gross volume, not which street floods.
- Micro-terrain and underpasses alter depth for identical rainfall.
- Storm drains are silted and plastic-clogged; models assume clean pipes.
- District-wide warnings lack street-level depth in centimeters.

#### [Card 2: Solution — Coupled Hydrodynamic Twin (5-Step Flow)]
- `01` **Radar Nowcast:** IMD Chennai S-band DWR reflectivity, 0–3 hour lead.
- `02` **Terrain Runoff:** CartoDEM 30 m with hydro-enforced underpass burning.
- `03` **Drain Network:** Directed graph, capacity check, clogging $\mu$, surcharge geysers.
- `04` **Street Depth:** Depth in cm for 7,894 Chennai road segments.
- `05` **Actionable Dispatch:** Flood-safe routes, critical asset alerts, navigation API export.

#### [Card 3: From -> To Paradigm Shift]
- **From (Passive Forecast):** *"Chennai will receive 85 mm rain today."*
- **To (Actionable Twin):** *"Gengu Reddy Subway floods to 48 cm in 35 min. Divert via EVR Salai."*

#### [Card 4: What Makes KAIROS Unique (5 Differentiators)]
- **Dynamic Clogging Factor ($\mu$):** Models real-world silt and solid waste ($\mu \in [0.05, 0.85]$).
- **Arrival-Time Routing:** Evaluates water depth at projected vehicle arrival time.
- **Critical Asset Safeguards:** Monitors 20 substations and 5 oxygen depots ($15\text{ cm}$ plinth rule).
- **Explainable Depth Ranges:** Predicts street flood depth with low/mid/high uncertainty bands.
- **Navigation-Ready REST API:** Serves 4 vehicle clearance classes (two-wheeler to NDRF truck).

#### [Bottom Positioning Banner]
- C-FLOWS and IFLOWS give city-scale alerts up to 72 h; KAIROS delivers street-level, drain-coupled 0–3 h operational command.

---

### SLIDE 3: Technical Approach
**Header:** Technical Approach | **Sub-header:** 5-Layer Coupled Hydrodynamic Architecture
**Layout:** 5 stacked full-width layer cards (IN / PROCESS / OUT), bottom tech-stack strip, right-side prototype proof card. Footer: `@SIH Idea submission`.

#### [Layer Flow: Input -> Process -> Output]
- **L0 Nowcast Engine:**
  - **IN:** IMD Chennai S-band DWR (plus Pallikaranai X-band), AWS rain gauges.
  - **PROCESS:** Marshall-Palmer $Z\text{–}R$ conversion, gauge bias calibration, optical-flow advection.
  - **OUT:** 1 km gridded rainfall across 6 horizons ($15, 30, 60, 90, 120, 180\text{ min}$).
- **L1 Terrain & Runoff:**
  - **IN:** CartoDEM 30 m, Sentinel-2 land cover, soil hydrologic group.
  - **PROCESS:** Culvert trench burning ($-2.5\text{ m}$), dynamic SCS-CN surface runoff generation.
  - **OUT:** Overland runoff inflow volume per street catchment.
- **L2 Drain Hydraulics:**
  - **IN:** GCC storm drain network graph, zonal clogging factor $\mu \in [0.05, 0.85]$.
  - **PROCESS:** Manning pipe capacity, hydraulic grade line, Torricelli manhole surcharge.
  - **OUT:** Manhole backflow geyser discharge onto street corridors.
- **L3 Street Depth Surrogate:**
  - **IN:** Surface overland runoff plus manhole surcharge overflow volume.
  - **PROCESS:** Physics-informed graph surrogate with analytical convex mass balance projection.
  - **OUT:** Street-level flood depth (cm) across 7,894 segments ($\mu$ low/mid/high).
- **L4 Emergency Routing:**
  - **IN:** Predicted flood depth tensor, road graph, asset coordinates.
  - **PROCESS:** Dynamic arrival-time A* clearance routing across 4 vehicle classes.
  - **OUT:** Safe route polyline, underpass hazard alerts, REST API JSON payload.

#### [Planned Agency Integrations]
- REST API live endpoints: `/api/nowcast`, `/api/route`, `/api/health`.
- Road-closure feed for navigation apps (Waze CIFS format) — *planned*.
- GTFS-Realtime service alerts for MTC buses and Chennai Metro — *planned*.
- NDMA SACHET / CAP protocol emergency broadcast alerts — *planned*.

#### [Tech Stack & Prototype Proof]
- **Stack:** Python, FastAPI, NetworkX, PyTorch, EPA SWMM (benchmark), Leaflet, PostGIS, OpenData.
- **Verification:** 200/200 automated PyTest tests passing cleanly in test suite.
- **Performance:** Surrogate inference in < 30 ms on CPU, versus minutes for 2D solvers.
- **Source Code:** `https://github.com/Team-Kairos-SIH/Smart-India-Hackathon-2026`

---

### SLIDE 4: Feasibility and Viability
**Header:** Feasibility and Viability | **Sub-header:** Deployment Readiness, Risk Mitigations & Phased Rollout
**Layout:** Top row: 4 feasibility chips. Center: 6-row Risk-to-Mitigation table. Bottom: 3-phase rollout roadmap. Footer: `@SIH Idea submission`.

#### [Four Feasibility Pillars]
- **Technical Viability:** Runs on standard CPU server; no new physical sensors required.
- **Data Viability:** Open baseline (IMD DWR, ISRO Bhuvan CartoDEM, OSM, GCC open drains).
- **Operational Viability:** 24x7 automated ingestion loop with offline mode and SMS fallbacks.
- **Economic Viability:** Zero commercial software license fees; fully portable open-source core.

#### [Risk-to-Mitigation Table (6 Rows)]
| Identified Risk | Engineering Mitigation Strategy |
|---|---|
| **Radar or telecom gateway outage** | Automatic fallback to local AWS rain gauge interpolation (tested). |
| **Missing drain invert records** | Topological graph healing from DEM/OSM; updated as GCC records arrive. |
| **Drain siltation and solid waste** | Dynamic clogging factor $\mu(t)$ calibrated against municipal desilting logs. |
| **Coastal backwater at outfalls** | Tidal boundary coupling (static head currently; INCOIS feed planned). |
| **Power or cellular network failure** | Standalone offline runtime cache; low-bandwidth SMS/CAP alerts. |
| **Hydrodynamic model uncertainty** | Depth uncertainty bands ($\mu$ low/mid/high) with human dispatcher in loop. |

#### [Three-Phase National Rollout Roadmap]
- **Phase 1 (Month 1–3):** Greater Chennai Corporation (GCC) pilot across 15 zones (7,894 segments).
- **Phase 2 (Month 4–8):** Expansion to Mumbai (MCGM) and Bengaluru (BBMP) via configuration.
- **Phase 3 (Month 9–18):** Turnkey SaaS container rollout for 100 Smart Cities Mission metropolises.

---

### SLIDE 5: Impact and Benefits
**Header:** Impact and Benefits | **Sub-header:** Stakeholder Transformation & Measurable Public Value
**Layout:** Top: 6 Target Audience chips. Center: Headline Impact Card. Bottom: 4 Structured Benefit Quadrants. Footer: `@SIH Idea submission`.

#### [Target Beneficiaries (6 Stakeholder Groups)]
- Greater Chennai Corporation (GCC) & Disaster Cell
- Greater Chennai Traffic Police (GCTP)
- 108 Emergency Ambulance Services & NDRF
- TANGEDCO Power Distribution Utilities
- MTC Bus Operators & Chennai Metro Rail (CMRL)
- Urban Commuters & Vulnerable Low-Lying Neighborhoods

#### [Headline Impact Callout]
- **Core Mission:** Turns a passive weather forecast into an actionable, street-level, minute-by-minute survival command.
- **Subway Protection:** Flags high-risk underpass submergence up to 45 minutes before water reaches critical depth.
- **Infrastructure Defense:** Safeguards 20 TANGEDCO substations and 5 oxygen depots using the 15 cm plinth rule.

#### [Four Multi-Dimensional Benefits]
- **Social Impact:**
  - Bilingual early warning alerts (Tamil & English) for local ward residents.
  - Safe evacuation routes for ambulances, reducing hospital transit delays.
  - Pre-emptive protection for vulnerable informal settlements in low-lying basins.
- **Economic Value:**
  - Targeted mobile pump pre-positioning saves municipal fuel and overtime labor.
  - Avoids recurring multi-crore proprietary hydraulic modeling software licenses.
  - Prevents submerged vehicle engine write-offs and commercial corridor damage.
- **Environmental Resilience:**
  - Reduces contaminated sewage backflow by flagging conduit surcharges early.
  - Identifies natural urban depression basins suitable for rainwater recharge.
  - Guides municipal engineers on priority desilting corridors before monsoons.
- **Scalability & SDG Alignment:**
  - Identical software core deploys to any city with radar, DEM, and street vectors.
  - Directly advances UN Sustainable Development Goals: SDG 11 (Sustainable Cities) & SDG 13 (Climate Action).

---

### SLIDE 6: Research and References
**Header:** Research and References | **Sub-header:** Institutional Guidelines, Scientific Literature & Open Data Sources
**Layout:** 3 reference columns (National Codes, Scientific Basis, Data Sources), right box for Prototype Verification & Links. Footer: `@SIH Idea submission`.

#### [Column 1: National Guidelines & Institutional Frameworks]
- **NDMA (2010):** *Guidelines on Management of Urban Flooding*, National Disaster Management Authority (`ndma.gov.in`).
- **CPHEEO (2019):** *Manual on Storm Water Drainage Systems*, Ministry of Housing and Urban Affairs.
- **NDMA SACHET:** Common Alerting Protocol (CAP) national emergency alert specifications.

#### [Column 2: Scientific Foundations & Peer-Reviewed Literature]
- **Marshall & Palmer (1948):** *The Distribution of Raindrops with Size*, J. Meteor. ($Z\text{–}R$ radar conversion).
- **Rossman et al. (EPA SWMM):** *Storm Water Management Model Reference Manual Volume II – Hydraulics*.
- **Pulkkinen et al. (2019):** *Pysteps: An open-source Python library for probabilistic nowcasting*, Geosci. Model Dev.
- **Wang & Liu (2006):** *An efficient method for identifying and filling surface depressions in digital elevation models*.
- **Physics-Informed Surrogates:** Graph topological neural approximations for real-time shallow water wave equations.

#### [Column 3: Open Data Sources & Baselines]
- **IMD Mausam:** Doppler Weather Radar (DWR) Meenambakkam S-band products (`mausam.imd.gov.in`).
- **ISRO Bhuvan:** CartoDEM 30 m Digital Elevation Model (`bhuvan-app3.nrsc.gov.in`).
- **OpenStreetMap:** Geofabrik Tamil Nadu road network and building vectors (`download.geofabrik.de`).
- **Validation Baselines:** Cyclone Michaung (Dec 2023) GCC inundation reports, C-FLOWS Chennai, IFLOWS-Mumbai.

#### [Prototype Verification & Code Access]
- **Automated Test Suite:** 200 / 200 tests passing (100% pass rate) across all 5 layers.
- **Compute Efficiency:** Surrogate inference executed in < 30 ms on CPU.
- **Hindcast Validation:** Cyclone Michaung subway inundation backtesting in progress.
- **Open Source Repository:** `https://github.com/Team-Kairos-SIH/Smart-India-Hackathon-2026`

---

## PART 2: READY-TO-PASTE PROMPT FOR GAMMA (gamma.app)

Copy the text inside the block below directly into Gamma's "Paste in text / Generate presentation" box:

```text
Create a 6-slide presentation for Smart India Hackathon 2026 based on the following exact specifications.

DESIGN SPECIFICATIONS:
- Presentation Type: Professional Government & Disaster Management Pitch Deck (SIH 2026).
- Aspect Ratio: 16:9 Widescreen.
- Visual Theme: Minimal, clean, modern government-grade command interface.
- Palette: Primary Blue (#1E5BD8), Accent Teal/Green (#12A05C), Charcoal Dark Text (#1B2733), Card Fill Light Slate (#EEF3FB), Pure White Canvas (#FFFFFF), Alert Red (#D93025) strictly for flood warnings.
- Typography: Sans-serif (Inter, Arial, or Calibri). High legibility, crisp contrast.
- Layout Rule: Points, structured cards, data tables, and flow diagrams ONLY. NO long paragraphs. Maximum 5 bullet points per card, under 12 words per bullet.
- Standard Footer on Every Slide: "@SIH Idea submission"
- Team Identity on Every Slide Header: "Team KAIROS | PS #26085 | JSS011"

SLIDE 1: Title Page
Slide Title: Title Page
Header: SMART INDIA HACKATHON 2026
Main Title: KAIROS - Street-Level Urban Flood Digital Twin
Subtitle: Operational Nowcasting & Emergency Dispatch Engine Coupling Atmospheric Radar with Subsurface Drainage Hydraulics
Content Cards:
Card 1 (Problem Context):
- Problem Statement ID: 26085
- Title: Urban Flood Nowcasting System (Drainage and Rainfall Coupling)
- Ministry: Ministry of Earth Sciences (MoES) / NCMRWF & Greater Chennai Corporation
Card 2 (Team Identity):
- Team Name: Team KAIROS
- Team ID: JSS011
- Theme: Disaster Management | Category: Software
Card 3 (Executive Hook):
- From passive city-wide rainfall warnings to street-level depth in centimeters.
- Predicts flash flood inundation across 7,894 road segments in < 30 ms on CPU.
- Generates dynamic arrival-time clearance routes for emergency response fleets.

SLIDE 2: Proposed Solution
Slide Title: Proposed Solution
Sub-title: KAIROS - Street-Level Urban Flood Digital Twin
Layout: 3-column comparative view (Problem on Left, 5-Step Solution Flow in Center, 5 Unique Differentiators on Right) plus Bottom Contrast Banner.
Column 1 (Problem: Why Current Systems Fall Short):
- Rain forecasts report total volume, not which street floods.
- Micro-terrain and underpasses change water depth drastically.
- Drainage pipes are silted and trash-choked; models assume clean pipes.
- Broad district alerts provide zero actionable depth in centimeters.
Column 2 (Coupled Hydrodynamic Solution Flow):
- 01 Radar Nowcast: IMD Chennai S-band radar rainfall, 0-3 hour lead time.
- 02 Terrain Runoff: CartoDEM 30 m with hydro-enforced underpass burning.
- 03 Drain Hydraulics: Directed graph, capacity check, clogging factor mu.
- 04 Street Depth: Real-time depth in cm for 7,894 Chennai road segments.
- 05 Emergency Dispatch: Flood-safe routes, asset alerts, navigation API export.
Column 3 (What Makes KAIROS Unique - 5 Key Differentiators):
- Real Clogging Factor (mu): Models dynamic silt and solid waste (mu in 0.05-0.85).
- Arrival-Time Routing: Depth checked when vehicle arrives; 4 clearance tiers.
- Critical Asset Defense: 20 substations and 5 oxygen depots (15 cm plinth rule).
- Explainable Uncertainty: Predicts street depth with low/mid/high uncertainty bands.
- Navigation-Ready API: Delivers live routing to ambulances, buses, and public apps.
Bottom Banner (Paradigm Shift):
- From: "Chennai will receive 85 mm rain today." (Passive Forecast)
- To: "Gengu Reddy Subway floods to 48 cm in 35 min. Divert via EVR Salai." (Actionable Twin)

SLIDE 3: Technical Approach
Slide Title: Technical Approach
Sub-title: 5-Layer Coupled Hydrodynamic Architecture
Layout: 5 structured horizontal process cards (Input -> Process -> Output) + Bottom Tech Stack & Verification Strip.
Layer 0 (L0 Nowcast Engine):
- Input: IMD Chennai S-band DWR, AWS rain gauges, telecom microwave links.
- Process: Marshall-Palmer Z-R conversion, bias calibration, optical-flow tracking.
- Output: 1 km gridded rainfall across 6 horizons (15 to 180 min).
Layer 1 (L1 Terrain & Runoff):
- Input: CartoDEM 30 m, Sentinel-2 land cover, hydrologic soil classification.
- Process: Culvert channel burning (-2.5 m), dynamic SCS-CN runoff generation.
- Output: Overland runoff discharge volume per street catchment.
Layer 2 (L2 Drain Hydraulics):
- Input: GCC storm drain network graph, zonal clogging factor mu (0.05-0.85).
- Process: Manning conduit capacity check, hydraulic grade line, surcharge calculation.
- Output: Manhole backflow geyser discharge erupting onto roadways.
Layer 3 (L3 Street Inundation Surrogate):
- Input: Overland runoff volume plus surcharged manhole backflow volume.
- Process: Physics-informed graph surrogate with convex quadratic mass balance.
- Output: Street water depth (cm) across 7,894 road corridors (mu low/mid/high).
Layer 4 (L4 Emergency Decision Routing):
- Input: Predicted street depth tensor, road network, critical asset locations.
- Process: Dynamic arrival-time A* clearance routing across 4 vehicle classes.
- Output: Safe route polyline, underpass hazard warnings, REST API JSON payload.
Bottom Bar (Tech Stack & Verification Proof):
- Core Stack: Python, FastAPI, NetworkX, PyTorch, EPA SWMM, Leaflet, PostGIS.
- Rigorous Verification: 200/200 automated PyTest tests passing (100% pass rate).
- Real-Time Speed: Surrogate inference runs in < 30 ms on standard CPU.

SLIDE 4: Feasibility and Viability
Slide Title: Feasibility and Viability
Sub-title: Operational Viability, Risk Mitigations & Rollout Roadmap
Layout: Top 4 Feasibility Cards, Middle 6-Row Risk Matrix, Bottom 3-Phase Timeline.
Top 4 Feasibility Cards:
- Technical: Runs on standard CPU server; no new physical sensors required.
- Data: Open data baseline (IMD DWR, ISRO Bhuvan CartoDEM, OpenStreetMap).
- Operational: 24x7 automated ingestion loop with offline mode and SMS fallbacks.
- Economic: Open-source stack with zero commercial software license costs.
Middle Table (Risk to Mitigation Matrix):
- Radar/Telecom Outage -> Automatic fallback to local AWS rain gauge interpolation.
- Missing Drain Invert Levels -> Topo-graph healing from DEM/OSM; updated as GCC records arrive.
- Drain Siltation & Trash -> Dynamic clogging factor mu calibrated from municipal desilting logs.
- Coastal High-Tide Lock -> Tidal boundary coupling (static head now; INCOIS feed planned).
- Power / Telecom Failure -> Standalone offline runtime cache; low-bandwidth SMS/CAP alerts.
- Model Uncertainty -> Depth uncertainty ranges (mu low/mid/high) with human in the loop.
Bottom Roadmap (Phased Deployment):
- Phase 1 (Month 1-3): GCC Chennai Pilot across 15 zones (7,894 road segments).
- Phase 2 (Month 4-8): Configuration rollout for Mumbai (MCGM) and Bengaluru (BBMP).
- Phase 3 (Month 9-18): Turnkey containerized expansion across 100 Smart Cities.

SLIDE 5: Impact and Benefits
Slide Title: Impact and Benefits
Sub-title: Quantifiable Public Value, Life Safety & Municipal Resilience
Layout: Top 6 Stakeholder Badges, Center Mission Callout, Bottom 4 Benefit Cards.
Top Stakeholder Chips:
- GCC Municipal Disaster Cell
- Greater Chennai Traffic Police
- 108 Ambulance Services & NDRF
- TANGEDCO Power Distribution
- MTC Bus & Metro Rail Operators
- Commuters & Vulnerable Settlements
Center Mission Callout:
- Turns a passive regional weather forecast into an actionable, street-level life-saving command.
- Flags high-risk underpass submergence up to 45 minutes ahead of critical water depth.
- Safeguards 20 electrical substations and 5 medical oxygen depots via 15 cm plinth rule.
Bottom 4 Benefit Cards:
- Social Benefits: Earlier warnings in Tamil and English; safer transit routes for ambulances.
- Economic Benefits: Targeted mobile pump deployment; eliminates expensive software licenses.
- Environmental Benefits: Reduces sewage backflow overflows; guides municipal desilting schedules.
- Scalability: Reusable computational core for any Indian city; advances SDG 11 & SDG 13.

SLIDE 6: Research and References
Slide Title: Research and References
Sub-title: Institutional Compliance, Scientific Literature & Open Datasets
Layout: 3 Reference Columns + Prototype Verification Box.
Column 1 (National Codes & Guidelines):
- NDMA Guidelines on Management of Urban Flooding (2010) - ndma.gov.in.
- CPHEEO Manual on Storm Water Drainage Systems (2019) - MoHUA.
- NDMA SACHET Common Alerting Protocol (CAP) national emergency alert standards.
Column 2 (Scientific Basis & Literature):
- Marshall and Palmer (1948): Z-R relationship for Doppler radar rain conversion.
- EPA SWMM (Rossman): 1D hydrodynamic drainage network reference solver.
- Pulkkinen et al. (2019): Pysteps probabilistic radar precipitation nowcasting.
- Wang and Liu (2006): Efficient depression filling for digital elevation models.
- Physics-informed graph neural surrogates for sub-second flood wave modeling.
Column 3 (Official Open Data Sources):
- IMD Doppler Weather Radar Network (Chennai S-band DWR) - mausam.imd.gov.in.
- ISRO Bhuvan CartoDEM 30 m Digital Elevation Models - bhuvan.nrsc.gov.in.
- OpenStreetMap India road corridors, buildings, and infrastructure vectors.
- Cyclone Michaung (December 2023) GCC ground reports for validation.
Prototype Verification & Code Access:
- Comprehensive Test Suite: 200/200 automated PyTest tests passing (100% pass rate).
- Computational Benchmark: Full city surrogate inference in < 30 ms on CPU.
- Hindcast Validation: Cyclone Michaung subway inundation backtesting in progress.
- Public Repository: https://github.com/Team-Kairos-SIH/Smart-India-Hackathon-2026
```
