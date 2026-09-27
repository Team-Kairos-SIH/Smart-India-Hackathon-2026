# KAIROS Urban Flood Nowcasting System: REST API Reference Manual

**Smart India Hackathon 2026 — Problem Statement #26085**  
**Lead Organizations**: Ministry of Earth Sciences (MoES) / NCMRWF & Greater Chennai Corporation (GCC)  
**Microservice Engine**: Python AI Microservice (`ai_service/api.py`)  
**Specification Version**: 1.0.0  
**Base URL**: `http://127.0.0.1:8000` (Local) / `http://<kairos-host>:8000` (Production Cluster)

---

## 1. System Overview & Architecture

The **KAIROS** REST API provides a low-latency bridge connecting physical sensor meshes (Doppler Radar, Telecom Microwave Links, AWS stations), hydrodynamic simulation engines (Manning-Saint-Venant 1D/2D solvers), and operational frontends (Incident Commander War Room, GCC ICCC Ripon Building, Citizen Mobile Alerting).

```
                      +---------------------------------------+
                      |   Incident Commander Dashboard / GIS  |
                      | (Web Map, Deck.gl, Tactical Controls) |
                      +-------------------+-------------------+
                                          |
                                          | REST (HTTP / JSON)
                                          v
+-----------------------------------------------------------------------------------+
|                           KAIROS FastAPI Microservice                             |
|                               (ai_service/api.py)                                 |
+---------------------+-------------------+-------------------+---------------------+
| Layer 0: Radar &    | Layer 2: Coastal  | Layer 3: Street   | Layer 4: Tactical   |
| Disaggregation      | Boundary Surge    | Conveyance & v*d  | Dispatch & Routing  |
| - /api/nowcast      | - /coastal/outfalls- /api/street-flow | - /route            |
| - /api/cml/telemetry|                   | - /cross-section  | - /assets/status    |
| - /api/health       |                   |                   | - /recommendations  |
|                     |                   |                   | - /alerts/cap       |
+---------------------+-------------------+-------------------+---------------------+
                                          |
                                          | Coupled Execution
                                          v
                      +---------------------------------------+
                      |     /api/simulate/what-if Sandbox     |
                      |   (Real-Time Sub-50ms Hydrodynamic    |
                      |        Multi-Parametric Engine)       |
                      +---------------------------------------+
```

### Key Technical Characteristics
- **Framework**: FastAPI (ASGI) running on Uvicorn.
- **Data Serialization**: Pydantic v2 validation models.
- **Execution Performance**: Sub-50ms response for parametric what-if simulations; under 150ms for spatial disaggregation across all 7,894 GCC road segments.
- **CORS Support**: Permissive (`*`) with credentials, allowing direct integration from browser web apps, Electron desktop apps, and micro-frontends.

---

## 2. Global Standards & Status Codes

All responses are returned as `application/json` (with the exception of raw XML fields embedded in alert payloads or static frontend assets).

| HTTP Status Code | Meaning | Usage Scenario |
| :--- | :--- | :--- |
| `200 OK` | Standard success | Successful execution and data retrieval. |
| `400 Bad Request` | Invalid input or coordinate mapping | Coordinates outside the GCC Chennai road bounding box or unrecognized routing graph nodes. |
| `404 Not Found` | Resource or safe corridor not found | No passable road route found for the requested vehicle clearance tier. |
| `422 Unprocessable Entity` | Schema validation failure | Missing required fields, out-of-range floats (e.g., `clogging > 0.85`), or invalid types. |
| `500 Internal Server Error` | Pipeline processing exception | Unhandled exception in underlying hydrodynamics or routing solvers. |

---

## 3. Comprehensive Endpoint Reference

### Summary Matrix

| Method | Endpoint | Primary Layer | Summary |
| :--- | :--- | :--- | :--- |
| `GET` | [`/api/health`](#1-get-apihealth) | System Core | Microservice & Doppler radar health telemetry |
| `GET` | [`/api/nowcast`](#2-get-apinowcast) | Layer 0 | Road network flood depth nowcasting (0–180 min) |
| `POST` | [`/route`](#3-post-route) | Layer 4 | Dynamic safe emergency routing (A* algorithm) |
| `GET` | [`/assets/status`](#4-get-assetsstatus) | Layer 4 | Critical infrastructure risk (TANGEDCO substations) |
| `POST` | [`/api/simulate/what-if`](#5-post-apisimulatewhat-if) | Multi-Layer | Incident Commander real-time sandbox |
| `GET` | [`/api/street-flow`](#6-get-apistreet-flow) | Layer 3 | Open-channel velocity and $v \times d$ wash-away hazard |
| `GET` | [`/api/recommendations/pumps`](#7-get-apirecommendationspumps) | Layer 4 | Automated de-watering pump dispatch optimization |
| `GET` | [`/api/cml/telemetry`](#8-get-apicmltelemetry) | Layer 0 | Cellular microwave link virtual rain gauge mesh |
| `GET` | [`/api/coastal/outfalls`](#9-get-apicoastaloutfalls) | Layer 2 | Bay of Bengal tidal surge & outfall lockout states |
| `GET` | [`/api/alerts/cap`](#10-get-apialertscap) | Layer 4 | OASIS CAP v1.2 XML & bilingual ward bulletins |
| `GET` | [`/api/cross-section`](#11-get-apicross-section) | Web GIS | IRC:SP:50 street cross-section & geyser plume |

---

### 1. `GET /api/health`

#### Description
Reports operational health, calibration telemetry, radar station connectivity, and active hydrodynamic configuration for the KAIROS microservice.

- **Source Code**: [`ai_service/api.py:70-82`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/api.py#L70-L82)
- **Tags**: `System Core`, `Layer 0`
- **Authentication**: None

#### Request Parameters
*None.*

#### Status Codes
- `200 OK`: System operational.

#### JSON Response Schema
```json
{
  "status": "string (operational)",
  "service": "string",
  "organization": "string",
  "pilot_region": "string",
  "calibrated_road_segments": "integer",
  "radar_station": "string",
  "equations": "string",
  "timestamp": "string (ISO 8601 UTC)"
}
```

#### Example Response Body
```json
{
  "status": "operational",
  "service": "KAIROS Layer 0 Rainfall Nowcasting Engine (Python AI Microservice)",
  "organization": "Ministry of Earth Sciences (MoES) / NCMRWF",
  "pilot_region": "Greater Chennai Corporation (GCC CMA Core)",
  "calibrated_road_segments": 7894,
  "radar_station": "IMD Meenambakkam (Dual-Pol Doppler, 10-min scan)",
  "equations": "Manning-Saint-Venant coupled hydrodynamic routing",
  "timestamp": "2026-09-27T11:15:30.124589+00:00"
}
```

#### cURL Command
```bash
curl -X GET "http://127.0.0.1:8000/api/health" \
     -H "Accept: application/json"
```

---

### 2. `GET /api/nowcast`

#### Description
Executes the Layer 0 pipeline: ingests radar sweeps, executes Brandes gauge-radar bias correction, calculates Farnebäck optical flow storm advection, and performs mass-conservative spatial disaggregation across all calibrated road segments. Returns flood depths (in cm) across lead horizons: $T+0\text{m}$, $T+30\text{m}$, $T+60\text{m}$, $T+90\text{m}$, $T+120\text{m}$, and $T+180\text{m}$.

- **Source Code**: [`ai_service/api.py:85-160`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/api.py#L85-L160)
- **Tags**: `Layer 0: Rainfall Nowcasting`

#### Query Parameters

| Parameter | Type | Required | Default | Validation / Constraints | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `scenario` | `string` | No | `"michaung"` | `"michaung"`, `"monsoon"`, `"moderate"`, `"2015_flood"` | Storm event scenario. |
| `mode` | `string` | No | `"auto"` | `"auto"`, `"live"`, `"archive"` | Ingestion pipeline mode. |
| `clogging` | `float` | No | `0.35` | $\ge 0.0, \le 0.85$ | Municipal solid waste drain choking factor. |

#### Status Codes
- `200 OK`: Nowcast computed successfully.
- `422 Unprocessable Entity`: Validation error (e.g., `clogging` out of $[0.0, 0.85]$ range).

#### JSON Response Schema
```json
{
  "status": "string (success)",
  "scenario": "string",
  "mode": "string",
  "clogging_factor": "number (float)",
  "timestamp": "string (ISO 8601 UTC)",
  "latency_ms": "number (float)",
  "g_r_ratio": "number (float)",
  "served_by": "string",
  "kpis": {
    "inundated_segments": "string",
    "max_depth_cm": "string",
    "active_segments": "integer",
    "radar_status": "string"
  },
  "segments": {
    "<segment_id>": {
      "t0": "number (depth in cm)",
      "t30": "number (depth in cm)",
      "t60": "number (depth in cm)",
      "t90": "number (depth in cm)",
      "t120": "number (depth in cm)",
      "t180": "number (depth in cm)"
    }
  }
}
```

#### Example Response Body
```json
{
  "status": "success",
  "scenario": "monsoon",
  "mode": "auto",
  "clogging_factor": 0.35,
  "timestamp": "2026-09-27T11:15:32.412000+00:00",
  "latency_ms": 78.4,
  "g_r_ratio": 1.082,
  "served_by": "python_ai_service_microservice",
  "kpis": {
    "inundated_segments": "142 Segments",
    "max_depth_cm": "42.5 cm",
    "active_segments": 600,
    "radar_status": "IMD Meenambakkam 10-Min Live (Dual-Pol)"
  },
  "confidence": {
    "t15": 0.949,
    "t30": 0.900,
    "t60": 0.811,
    "t90": 0.730,
    "t120": 0.657,
    "t180": 0.533
  },
  "segments": {
    "SEG-0042": {
      "t0": 4.5,
      "t30": 12.2,
      "t60": 21.0,
      "t90": 18.0,
      "t120": 12.5,
      "t180": 5.2
    },
    "SEG-1184": {
      "t0": 8.2,
      "t30": 22.8,
      "t60": 42.5,
      "t90": 39.0,
      "t120": 31.4,
      "t180": 18.0
    }
  }
}
```

#### cURL Command
```bash
curl -X GET "http://127.0.0.1:8000/api/nowcast?scenario=michaung&mode=auto&clogging=0.45" \
     -H "Accept: application/json"
```

---

### 3. `POST /route`

#### Description
Computes a Time-Dependent A* ($TD\text{-}A^*$) emergency route across Chennai. Avoids dynamic flood depth hazards, impassable underpasses, and dangerous water velocity hotspots based on vehicle-specific clearance thresholds.

- **Source Code**: [`ai_service/api.py:164-190`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/api.py#L164-L190)
- **Tags**: `Layer 4: Routing`

#### Pydantic Models
```python
class Coordinate(BaseModel):
    latitude: float = Field(..., description="Latitude in decimal degrees")
    longitude: float = Field(..., description="Longitude in decimal degrees")

class RouteRequest(BaseModel):
    vehicle_type: str = Field(..., description="Vehicle type (e.g. ambulance, passenger_car, fire_truck, two_wheeler)")
    origin: Coordinate
    destination: Coordinate
    departure_time: float = Field(0.0, description="Departure time in minutes from now")
```

#### Vehicle Clearance Profiles Reference
- `two_wheeler`: Maximum wading clearance = $15\text{ cm}$
- `passenger_car`: Maximum wading clearance = $25\text{ cm}$
- `ambulance`: Maximum wading clearance = $45\text{ cm}$
- `fire_truck`: Maximum wading clearance = $70\text{ cm}$

#### Status Codes
- `200 OK`: Safe route found and calculated.
- `400 Bad Request`: Invalid coordinates (origin or destination not mappable to road graph).
- `404 Not Found`: No safe route available; flood depths exceed vehicle clearance along all viable paths.
- `422 Unprocessable Entity`: Missing fields or coordinate validation failure.
- `500 Internal Server Error`: Routing engine solver failure.

#### Example Request Body
```json
{
  "vehicle_type": "ambulance",
  "origin": {
    "latitude": 13.0402,
    "longitude": 80.2337
  },
  "destination": {
    "latitude": 13.0827,
    "longitude": 80.2755
  },
  "departure_time": 10.0
}
```

#### Example Response Body (200 OK)
```json
{
  "status": "SUCCESS",
  "route_geometry": [
    [13.0402, 80.2337],
    [13.0450, 80.2395],
    [13.0582, 80.2480],
    [13.0720, 80.2610],
    [13.0827, 80.2755]
  ],
  "ordered_segment_ids": [
    "SEG-0042",
    "SEG-0089",
    "SEG-0112",
    "SEG-0450"
  ],
  "ordered_node_ids": [
    1042,
    1089,
    1150,
    1240
  ],
  "total_distance_m": 6420.5,
  "physical_travel_time_min": 14.8,
  "eta_min": 24.8,
  "hazard_cost": 182.4,
  "maximum_effective_depth": 18.5,
  "maximum_hazard_ratio": 0.41,
  "minimum_clearance": 26.5,
  "hazard_category": "MODERATE_WATERLOGGING_PASSABLE",
  "underpasses_used": [],
  "underpasses_avoided": [
    "Duraisamy Subway",
    "Madley Subway"
  ],
  "nodes_explored": 348,
  "blocked_edges": 19,
  "failure_reason": null
}
```

#### Example Error Response (404 Not Found)
```json
{
  "detail": {
    "status": "FAILED",
    "failure_reason": "No safe route found: All viable corridors impassable due to water depth exceeding 45.0 cm clearance.",
    "blocked_edges": 84,
    "nodes_explored": 512
  }
}
```

#### cURL Command
```bash
curl -X POST "http://127.0.0.1:8000/route" \
     -H "Content-Type: application/json" \
     -d '{
       "vehicle_type": "ambulance",
       "origin": {"latitude": 13.0402, "longitude": 80.2337},
       "destination": {"latitude": 13.0827, "longitude": 80.2755},
       "departure_time": 5.0
     }'
```

---

### 4. `GET /assets/status`

#### Description
Monitors flood hazard levels at critical high-voltage substations (TANGEDCO 230kV / 110kV / 33kV) across Chennai to inform preventative de-energization and safeguard civic power distribution.

- **Source Code**: [`ai_service/api.py:192-208`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/api.py#L192-L208)
- **Tags**: `Layer 4: Critical Assets`

#### Request Parameters
*None.*

#### Status Codes
- `200 OK`: Asset statuses retrieved successfully.
- `500 Internal Server Error`: Asset monitor initialization or interpolation error.

#### JSON Response Schema
```json
{
  "status": "string (SUCCESS / FAILED)",
  "total_monitored": "integer",
  "assets": [
    {
      "substation_id": "string",
      "name": "string",
      "voltage_kv": "number",
      "latitude": "number (float)",
      "longitude": "number (float)",
      "status": "string (SAFE | WATCH | WARNING | CRITICAL_ISOLATION)",
      "maximum_site_depth_cm": "number (float)",
      "supporting_road_segment_ids": ["string"],
      "uncertainty": "boolean",
      "explanation": "string"
    }
  ]
}
```

#### Example Response Body
```json
{
  "status": "SUCCESS",
  "total_monitored": 8,
  "assets": [
    {
      "substation_id": "SUB-TND-01",
      "name": "Guindy 230kV GIS Substation",
      "voltage_kv": 230,
      "latitude": 13.0067,
      "longitude": 80.2026,
      "status": "WATCH",
      "maximum_site_depth_cm": 14.5,
      "supporting_road_segment_ids": ["SEG-3419"],
      "uncertainty": false,
      "explanation": "Perimeter drainage near capacity; switchyard baseline remains 20cm above predicted peak."
    },
    {
      "substation_id": "SUB-TND-04",
      "name": "Velachery 110kV Substation",
      "voltage_kv": 110,
      "latitude": 12.9815,
      "longitude": 80.2180,
      "status": "CRITICAL_ISOLATION",
      "maximum_site_depth_cm": 52.0,
      "supporting_road_segment_ids": ["SEG-1184"],
      "uncertainty": false,
      "explanation": "Predicted water depth exceeds plinth protection threshold (40cm). Controlled power cut recommended."
    }
  ]
}
```

#### cURL Command
```bash
curl -X GET "http://127.0.0.1:8000/assets/status" \
     -H "Accept: application/json"
```

---

### 5. `POST /api/simulate/what-if`

#### Description
Incident Commander interactive tactical simulation sandbox. Executes in **sub-50ms** by coupling cloudburst rain intensity, coastal tidal lockouts, solid waste clogging penalties, and emergency pump relief factors.

- **Source Code**: [`ai_service/api.py:222-279`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/api.py#L222-L279)
- **Tags**: `Tactical Simulation: What-If Sandbox`

#### Pydantic Model
```python
class WhatIfSimulationRequest(BaseModel):
    scenario: str = Field("michaung", description="Baseline storm scenario: michaung, monsoon, 2015_flood")
    cloudburst_intensity_mm_hr: Optional[float] = Field(None, ge=0.0, le=200.0, description="Cloudburst rainfall intensity slider")
    tidal_surge_m: float = Field(0.85, ge=0.0, le=3.0, description="Bay of Bengal coastal surge (0.0 to 3.0 m)")
    clogging_factor: float = Field(0.35, ge=0.0, le=0.85, description="Dynamic municipal solid waste clogging factor")
    deployed_pumps_count: int = Field(0, ge=0, le=20, description="Number of mobile de-watering pump units deployed")
```

#### Status Codes
- `200 OK`: Simulation executed successfully.
- `422 Unprocessable Entity`: Input constraint violations.

#### Example Request Body
```json
{
  "scenario": "michaung",
  "cloudburst_intensity_mm_hr": 110.0,
  "tidal_surge_m": 1.25,
  "clogging_factor": 0.50,
  "deployed_pumps_count": 8
}
```

#### Example Response Body
```json
{
  "status": "success",
  "simulation_mode": "INCIDENT_COMMANDER_WHAT_IF",
  "latency_ms": 38.45,
  "parameters": {
    "scenario": "michaung",
    "cloudburst_intensity_mm_hr": 110.0,
    "tidal_surge_m": 1.25,
    "clogging_factor": 0.5,
    "deployed_pumps": 8
  },
  "impact_deltas": {
    "baseline_peak_depth_cm": 89.2,
    "mitigated_peak_depth_cm": 50.0,
    "depth_reduction_cm": 39.2,
    "flooded_corridors_relieved": 144,
    "outfalls_locked_out": 2
  },
  "coastal_outfall_status": [
    {
      "outfall_name": "Adyar River Estuary (Besant Nagar)",
      "bed_invert_m_msl": 0.5,
      "sea_water_level_m_msl": 1.67,
      "upstream_hgl_m_msl": 1.4,
      "head_difference_m": -0.27,
      "discharge_status": "REVERSE_INTRUSION",
      "throttling_factor": 1.0,
      "effective_discharge_ratio": -0.52
    },
    {
      "outfall_name": "Cooum River Mouth (Napier Bridge)",
      "bed_invert_m_msl": 0.4,
      "sea_water_level_m_msl": 1.67,
      "upstream_hgl_m_msl": 1.25,
      "head_difference_m": -0.42,
      "discharge_status": "REVERSE_INTRUSION",
      "throttling_factor": 1.0,
      "effective_discharge_ratio": -0.648
    }
  ],
  "recommended_pumps": [
    {
      "priority_rank": 1,
      "segment_id": "HOTSPOT-09-1",
      "road_name": "Usman Road Underpass (T. Nagar)",
      "zone_no": 9,
      "zone_name": "Teynampet",
      "latitude": 13.0402,
      "longitude": 80.2337,
      "predicted_depth_cm": 44.3,
      "surcharge_rate_m3_s": 0.6,
      "recommended_pump_type": "Super-Sucker 150HP High-Discharge Unit",
      "required_capacity_m3_hr": 450.0,
      "estimated_volume_relief_m3": 900.0,
      "critical_proximity": "Commercial Hub & Hospital Access",
      "action_directive": "Pre-stage mobile pump at Usman Road Underpass (T. Nagar) prior to cloudburst peak."
    }
  ]
}
```

#### cURL Command
```bash
curl -X POST "http://127.0.0.1:8000/api/simulate/what-if" \
     -H "Content-Type: application/json" \
     -d '{
       "scenario": "michaung",
       "cloudburst_intensity_mm_hr": 95.0,
       "tidal_surge_m": 1.10,
       "clogging_factor": 0.45,
       "deployed_pumps_count": 6
     }'
```

---

### 6. `GET /api/street-flow`

#### Description
Evaluates "Street-as-Canal" open-channel conveyance when underground storm conduits surcharge. Applies Manning's equation:
$$v = \frac{1}{n} R_h^{2/3} S_0^{1/2}$$
Evaluates the international Velocity-Depth product ($v \times d$) wash-away hazard tiers (Australian Rainfall & Runoff / UK DEFRA).

- **Source Code**: [`ai_service/api.py:281-312`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/api.py#L281-L312)
- **Tags**: `Layer 3: Street-as-Canal Conveyance`

#### Query Parameters

| Parameter | Type | Required | Default | Validation / Constraints | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `scenario` | `string` | No | `"michaung"` | Any recognized scenario string | Storm scenario. |
| `horizon` | `integer` | No | `60` | $\ge 15, \le 180$ | Forecast horizon in minutes. |

#### Hazard Classification Criteria ($v \times d$)
- $< 0.4\text{ m}^2/\text{s}$: `LOW (Pedestrian Safe)`
- $0.4 \le v \times d < 0.6\text{ m}^2/\text{s}$: `MODERATE (Pedestrian Hazard)`
- $0.6 \le v \times d < 1.2\text{ m}^2/\text{s}$: `HIGH (Vehicle Floatation & Wash-Away)`
- $\ge 1.2\text{ m}^2/\text{s}$: `EXTREME (Heavy Emergency Transport Hazard)`

#### Status Codes
- `200 OK`: Hydrodynamic flow and hazard tiers computed.
- `422 Unprocessable Entity`: Validation failure on horizon bounds.

#### Example Response Body
```json
{
  "status": "success",
  "scenario": "michaung",
  "horizon_min": 60,
  "summary": {
    "evaluated_segments": 6,
    "horizon_min": 60,
    "active_street_channels_count": 5,
    "mean_velocity_m_s": 1.84,
    "max_velocity_m_s": 3.12,
    "max_discharge_m3_s": 24.8,
    "vehicle_floatation_hazard_segments": 4,
    "extreme_washaway_hazard_segments": 2
  },
  "corridors": [
    {
      "segment_id": "SEG-5902",
      "road_name": "Vyasarpadi Ganesapuram Subway",
      "depth_cm": 95.0,
      "velocity_m_s": 3.12,
      "discharge_m3_s": 24.8,
      "hazard_vx_d": 2.964,
      "washaway_hazard_tier": "EXTREME (Heavy Emergency Transport Hazard)"
    },
    {
      "segment_id": "SEG-1184",
      "road_name": "Velachery 100 Feet Road",
      "depth_cm": 68.5,
      "velocity_m_s": 1.45,
      "discharge_m3_s": 15.89,
      "hazard_vx_d": 0.993,
      "washaway_hazard_tier": "HIGH (Vehicle Floatation & Wash-Away)"
    }
  ]
}
```

#### cURL Command
```bash
curl -X GET "http://127.0.0.1:8000/api/street-flow?scenario=michaung&horizon=60" \
     -H "Accept: application/json"
```

---

### 7. `GET /api/recommendations/pumps`

#### Description
Generates prioritized municipal de-watering pump dispatch recommendations for the Greater Chennai Corporation (GCC) Integrated Command and Control Centre (ICCC) at Ripon Building.

- **Source Code**: [`ai_service/api.py:314-327`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/api.py#L314-L327)
- **Tags**: `Layer 4: Municipal Dispatch`

#### Query Parameters

| Parameter | Type | Required | Default | Validation / Constraints | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `limit` | `integer` | No | `5` | $\ge 1, \le 10$ | Maximum number of ranked recommendations. |

#### Status Codes
- `200 OK`: Recommendations generated.
- `422 Unprocessable Entity`: `limit` not within $[1, 10]$.

#### Example Response Body
```json
{
  "status": "success",
  "beneficiary": "Greater Chennai Corporation (GCC ICCC Ripon Building)",
  "recommended_pumps": [
    {
      "priority_rank": 1,
      "segment_id": "HOTSPOT-09-1",
      "road_name": "Usman Road Underpass (T. Nagar)",
      "zone_no": 9,
      "zone_name": "Teynampet",
      "latitude": 13.0402,
      "longitude": 80.2337,
      "predicted_depth_cm": 44.3,
      "surcharge_rate_m3_s": 0.6,
      "recommended_pump_type": "Super-Sucker 150HP High-Discharge Unit",
      "required_capacity_m3_hr": 450.0,
      "estimated_volume_relief_m3": 900.0,
      "critical_proximity": "Commercial Hub & Hospital Access",
      "action_directive": "Pre-stage mobile pump at Usman Road Underpass (T. Nagar) prior to cloudburst peak."
    },
    {
      "priority_rank": 2,
      "segment_id": "HOTSPOT-13-2",
      "road_name": "Velachery Vijaya Nagar Junction",
      "zone_no": 13,
      "zone_name": "Adyar",
      "latitude": 12.9815,
      "longitude": 80.218,
      "predicted_depth_cm": 40.1,
      "surcharge_rate_m3_s": 0.48,
      "recommended_pump_type": "Super-Sucker 150HP High-Discharge Unit",
      "required_capacity_m3_hr": 400.0,
      "estimated_volume_relief_m3": 800.0,
      "critical_proximity": "Clay Depression & Bus Terminus",
      "action_directive": "Pre-stage mobile pump at Velachery Vijaya Nagar Junction prior to cloudburst peak."
    }
  ]
}
```

#### cURL Command
```bash
curl -X GET "http://127.0.0.1:8000/api/recommendations/pumps?limit=3" \
     -H "Accept: application/json"
```

---

### 8. `GET /api/cml/telemetry`

#### Description
Retrieves telemetry from opportunistic telecom Commercial Microwave Links (CML) operated by Bharti Airtel, Reliance Jio, and Vodafone Idea across Chennai (13–73 GHz). Converts attenuation to rain rate using the ITU-R P.838-3 power law:
$$R = \left(\frac{k}{a}\right)^{1/b}$$
Accounts for Wet Antenna Attenuation (WAA) and baseline drift.

- **Source Code**: [`ai_service/api.py:329-337`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/api.py#L329-L337)
- **Tags**: `Layer 0: CML Sensor Mesh`

#### Query Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `scenario` | `string` | No | `"michaung"` | Storm scenario: `"michaung"`, `"2015_flood"`, `"monsoon"` |

#### Status Codes
- `200 OK`: Telemetry and inverted rain rates returned.

#### Example Response Body
```json
{
  "status": "success",
  "active_cml_links": 8,
  "telecom_operators": [
    "Bharti Airtel",
    "Reliance Jio",
    "Vodafone Idea"
  ],
  "mesh_mean_rain_rate_mm_hr": 64.82,
  "itu_recommendation": "ITU-R P.838-3 Power Law",
  "links": [
    {
      "link_id": "CML-CHN-01",
      "operator": "Airtel",
      "locality": "Central / Egmore",
      "frequency_ghz": 18,
      "polarization": "H",
      "path_length_km": 4.2,
      "tx_coordinates": [13.0827, 80.2755],
      "rx_coordinates": [13.05, 80.25],
      "tsl_dbm": 15.0,
      "rsl_dbm": -71.4,
      "baseline_dbm": -45.0,
      "specific_attenuation_db_km": 5.905,
      "retrieved_rain_rate_mm_hr": 60.15,
      "status": "WET"
    },
    {
      "link_id": "CML-CHN-07",
      "operator": "Jio",
      "locality": "OMR IT Corridor (5G Link)",
      "frequency_ghz": 73,
      "polarization": "H",
      "path_length_km": 0.8,
      "tx_coordinates": [12.9056, 80.2275],
      "rx_coordinates": [12.9, 80.232],
      "tsl_dbm": 15.0,
      "rsl_dbm": -64.2,
      "baseline_dbm": -45.0,
      "specific_attenuation_db_km": 22.0,
      "retrieved_rain_rate_mm_hr": 78.4,
      "status": "WET"
    }
  ]
}
```

#### cURL Command
```bash
curl -X GET "http://127.0.0.1:8000/api/cml/telemetry?scenario=michaung" \
     -H "Accept: application/json"
```

---

### 9. `GET /api/coastal/outfalls`

#### Description
Evaluates coastal boundary conditions along the Bay of Bengal coastline. Uses harmonic superposition of Survey of India tidal constituents ($M_2, S_2, N_2, K_1, O_1, M_4$) coupled with Holland cyclonic wind setup and inverted barometer surge. Determines outfall tailwater head, throttling, and reverse seawater intrusion at major drainage estuaries.

- **Source Code**: [`ai_service/api.py:339-347`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/api.py#L339-L347)
- **Tags**: `Layer 2: Coastal Boundary`

#### Query Parameters

| Parameter | Type | Required | Default | Validation / Constraints | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `tide_surge_m` | `float` | No | `0.85` | $\ge 0.0, \le 3.0$ | Cyclonic storm surge elevation above mean sea level. |

#### Outfall Discharge Status Glossary
- `FREE_GRAVITY`: Sea level below invert; outfall discharges at full capacity.
- `THROTTLED_BACKWATER`: Sea level between invert and upstream HGL; partial gravity discharge.
- `TIDAL_LOCKOUT`: Sea level equals upstream HGL; gravity discharge drops to zero.
- `REVERSE_INTRUSION`: Sea level exceeds upstream HGL; seawater enters the urban storm drain network.

#### Status Codes
- `200 OK`: Outfall boundary states computed.
- `422 Unprocessable Entity`: `tide_surge_m` out of valid bounds.

#### Example Response Body
```json
{
  "timestamp_offset_hours": 0.0,
  "astronomical_tide_m_msl": 0.42,
  "cyclonic_surge_m": 0.85,
  "total_coastal_head_m_msl": 1.27,
  "tidal_regime": "Semi-diurnal (Spring/Neap active)",
  "outfalls_monitored": 4,
  "outfalls_locked_out": 2,
  "outfalls": [
    {
      "outfall_name": "Adyar River Estuary (Besant Nagar)",
      "bed_invert_m_msl": 0.5,
      "sea_water_level_m_msl": 1.27,
      "upstream_hgl_m_msl": 1.4,
      "head_difference_m": 0.13,
      "discharge_status": "THROTTLED_BACKWATER",
      "throttling_factor": 0.62,
      "effective_discharge_ratio": 0.38
    },
    {
      "outfall_name": "Cooum River Mouth (Napier Bridge)",
      "bed_invert_m_msl": 0.4,
      "sea_water_level_m_msl": 1.27,
      "upstream_hgl_m_msl": 1.25,
      "head_difference_m": -0.02,
      "discharge_status": "TIDAL_LOCKOUT",
      "throttling_factor": 1.0,
      "effective_discharge_ratio": 0.0
    },
    {
      "outfall_name": "Buckingham Canal Lockout (Mylapore/Adyar)",
      "bed_invert_m_msl": 0.3,
      "sea_water_level_m_msl": 1.27,
      "upstream_hgl_m_msl": 1.1,
      "head_difference_m": -0.17,
      "discharge_status": "REVERSE_INTRUSION",
      "throttling_factor": 1.0,
      "effective_discharge_ratio": -0.412
    },
    {
      "outfall_name": "Ennore Creek (Kosasthalaiyar Outlet)",
      "bed_invert_m_msl": 0.7,
      "sea_water_level_m_msl": 1.27,
      "upstream_hgl_m_msl": 1.65,
      "head_difference_m": 0.38,
      "discharge_status": "THROTTLED_BACKWATER",
      "throttling_factor": 0.368,
      "effective_discharge_ratio": 0.632
    }
  ]
}
```

#### cURL Command
```bash
curl -X GET "http://127.0.0.1:8000/api/coastal/outfalls?tide_surge_m=1.15" \
     -H "Accept: application/json"
```

---

### 10. `GET /api/alerts/cap`

#### Description
Generates standards-compliant **OASIS CAP v1.2 / ITU-T X.1303** Common Alerting Protocol XML emergency messages with bilingual payloads (English `en-IN` and Tamil `ta-IN`), alongside formatted mobile bulletins for GCC Ward Engineers and Citizen SMS (Helpline 1913).

- **Source Code**: [`ai_service/api.py:349-376`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/api.py#L349-L376)
- **Tags**: `Layer 4: Public Alerts`

#### Query Parameters

| Parameter | Type | Required | Default | Validation / Constraints | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `zone` | `integer` | No | `9` | $\ge 1, \le 15$ | GCC Administrative Zone (1 to 15). |

#### Status Codes
- `200 OK`: CAP alert and bulletins generated.
- `422 Unprocessable Entity`: Zone number out of range ($< 1$ or $> 15$).

#### Example Response Body
```json
{
  "status": "success",
  "standard": "OASIS CAP v1.2 / ITU-T X.1303",
  "cap_xml": "<?xml version='1.0' encoding='utf-8'?>\n<alert xmlns=\"urn:oasis:names:tc:emergency:cap:1.2\">\n  <identifier>GCC-KAIROS-B892FA10</identifier>\n  <sender>iccc.chennaicorporation.gov.in</sender>\n  <sent>2026-09-27T11:15:35.912000+00:00</sent>\n  <status>Actual</status>\n  <msgType>Alert</msgType>\n  <scope>Public</scope>\n  <info>\n    <language>en-IN</language>\n    <category>Safety</category>\n    <event>Urban Pluvial Inundation &amp; Surcharge Alert</event>\n    <urgency>Immediate</urgency>\n    <severity>Severe</severity>\n    <certainty>Observed</certainty>\n    <headline>FLASH FLOOD &amp; SUBWAY SURCHARGE WARNING</headline>\n    <description>Severe pluvial inundation and manhole surcharge exceeding drain capacity.</description>\n    <instruction>Avoid flooded subways. Diversion in effect. Helpline: 1913.</instruction>\n    <area>\n      <areaDesc>Zone 9 (Teynampet), Greater Chennai Corporation</areaDesc>\n      <polygon>13.0380,80.2290 13.0450,80.2295 13.0440,80.2390 13.0370,80.2380 13.0380,80.2290</polygon>\n    </area>\n  </info>\n  <info>\n    <language>ta-IN</language>\n    <category>Safety</category>\n    <event>நகர்ப்புற திடீர் வெள்ளம் மற்றும் வடிகால் எச்சரிக்கை</event>\n    <urgency>Immediate</urgency>\n    <severity>Severe</severity>\n    <certainty>Observed</certainty>\n    <headline>தீவிர திடீர் வெள்ளம் மற்றும் வடிகால் எச்சரிக்கை</headline>\n    <description>மழைநீர் வடிகால் அதிகப்படியான நீரினால் நிரம்பி வழிகிறது.</description>\n    <instruction>சுரங்கப்பாதைகளை தவிர்க்கவும். உதவிக்கு: 1913.</instruction>\n    <area>\n      <areaDesc>பெருநகர சென்னை மாநகராட்சி - Zone 9 (Teynampet)</areaDesc>\n      <polygon>13.0380,80.2290 13.0450,80.2295 13.0440,80.2390 13.0370,80.2380 13.0380,80.2290</polygon>\n    </area>\n  </info>\n</alert>",
  "bulletins": {
    "whatsapp_technical_bulletin": "🚨 [GCC ICCC TACTICAL DISPATCH - DURAISAMY SUBWAY & USMAN ROAD]\n📍 Zone: 09 | Corridor: Duraisamy Subway & Usman Road\n⏱ Lead Horizon: T+60m Forecast\n🌊 Predicted Water Depth: 58.5 cm\n⚡ Conduit Surcharge Rate: 2.45 m³/s (Reverse Backflow)\n🚜 Dispatched Unit: Pump Rig #04 (100HP Diesel)\n🔘 Immediate Directive: Deploy suction hose at downstream manhole invert; clear drop-inlet grating debris. Emergency Helpline: 1913.",
    "citizen_sms_en": "GCC Alert: Waterlogging (58cm) expected at Duraisamy Subway & Usman Road within 60 mins. Use diversion routes. For water removal assistance call 1913.",
    "citizen_sms_ta": "சென்னை மாநகராட்சி எச்சரிக்கை: Duraisamy Subway & Usman Road பகுதியில் 60 நிமிடங்களில் 58செ.மீ நீர் தேங்க வாய்ப்புள்ளது. மாற்றுப் பாதையை பயன்படுத்தவும். உதவிக்கு: 1913."
  }
}
```

#### cURL Command
```bash
curl -X GET "http://127.0.0.1:8000/api/alerts/cap?zone=9" \
     -H "Accept: application/json"
```

---

### 11. `GET /api/cross-section`

#### Description
Generates real-time geometric and hydrodynamic cross-section profiles adhering to **IRC:SP:50** (Guidelines on Urban Drainage) and **CPHEEO** standards. Evaluates roadway camber, sidewalk curb overtopping, storm pipe surcharging, manhole geyser plume eruption heights, and vehicle passability.

- **Source Code**: [`ai_service/api.py:379-406`](file:///home/yashwanth-n17/Documents/Workspace%20Linux/Smart-India-Hackathon-2026/ai_service/api.py#L379-L406)
- **Tags**: `Tactical Web GIS: Cross-Section Profile`

#### Query Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `road_name` | `string` | No | `"Duraisamy Subway / Usman Road"` | Road corridor identifier. |
| `water_depth_cm` | `float` | No | `45.0` | Flood water depth at pavement crown in centimeters. |

#### Physical Formulas
- **Sidewalk Overtopping**: $\text{sidewalk\_water\_depth} = \max(0.0, \text{water\_depth\_cm} - \text{curb\_height\_cm})$
- **Curb Standard**: $15.0\text{ cm}$
- **Geyser Plume Height**: $\text{water\_depth\_cm} \times 0.42$ (triggered if $\text{water\_depth\_cm} > 30.0\text{ cm}$)
- **Impassability Rules**:
  - $> 30.0\text{ cm}$: `two_wheeler`, `passenger_car`, `ambulance`
  - $> 18.0\text{ cm}$: `two_wheeler`, `passenger_car`
  - $\le 18.0\text{ cm}$: `two_wheeler`

#### Status Codes
- `200 OK`: Street cross-section metrics computed.

#### Example Response Body
```json
{
  "road_name": "Duraisamy Subway / Usman Road",
  "road_width_m": 14.0,
  "curb_height_cm": 15.0,
  "pavement_camber_pct": 2.5,
  "water_depth_cm": 45.0,
  "sidewalk_overtopped": true,
  "sidewalk_water_depth_cm": 30.0,
  "subsurface_pipe_dia_m": 0.9,
  "is_manhole_surcharging": true,
  "geyser_plume_height_cm": 18.9,
  "impassable_for": [
    "two_wheeler",
    "passenger_car",
    "ambulance"
  ]
}
```

#### cURL Command
```bash
curl -X GET "http://127.0.0.1:8000/api/cross-section?road_name=Usman+Road&water_depth_cm=45.0" \
     -H "Accept: application/json"
```

---

## 4. Frontend & Static File Mounts

In addition to the REST API endpoints, `ai_service/api.py` mounts the Web GIS tactical user interface and geospatial data artifacts:

| Mount Point | Type | Source Directory | Purpose |
| :--- | :--- | :--- | :--- |
| `GET /` | FileResponse | `frontend/index.html` | Incident Commander tactical dashboard |
| `GET /data/*` | StaticFiles | `frontend/data/` | GeoJSON layers, shapefiles, road graphs |
| `GET /static/*`| StaticFiles | `frontend/` | Web GIS JavaScript, CSS, Leaflet/Deck.gl bundles |

---

## 5. Developer Guide: Running & Testing the API

### Starting the Server
From the workspace root directory:
```bash
uvicorn ai_service.api:app --host 0.0.0.0 --port 8000 --reload
```

### Interactive Documentation
Once started, FastAPI automatically generates interactive documentation:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`
- **OpenAPI Schema**: `http://127.0.0.1:8000/openapi.json`
