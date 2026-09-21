"""Layer 4: Critical Assets Monitor - Substation Plinth Safeguarding.

Monitors critical urban energy infrastructure by connecting geospatial assets
to Layer 3 flood predictions via the Layer 4 road network.
"""

import csv
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import math

from ai_service.layer4.temporal_flood import TemporalFloodDepthService

logger = logging.getLogger(__name__)

# Configurable thresholds
STATUS_SAFE = "SAFE"
STATUS_AT_RISK = "AT_RISK"
STATUS_CRITICAL = "CRITICAL"
STATUS_UNKNOWN = "UNKNOWN"

# We assume a default critical clearance margin of 15cm if plinth is known
CRITICAL_MARGIN_CM = 15.0

# TANGEDCO Substation Catalog (Greater Chennai Corporation Core Grid)
CHENNAI_SUBSTATIONS = [
    {"id": "SS-001", "name": "Mylapore Substation", "voltage_kv": 230, "plinth_cm": 60.0, "lat": 13.0384, "lon": 80.2612, "zone": "Zone 9 - Mylapore"},
    {"id": "SS-002", "name": "T. Nagar Substation", "voltage_kv": 110, "plinth_cm": 45.0, "lat": 13.0418, "lon": 80.2341, "zone": "Zone 10 - Kodambakkam"},
    {"id": "SS-003", "name": "Guindy Industrial Grid", "voltage_kv": 230, "plinth_cm": 55.0, "lat": 13.0067, "lon": 80.2036, "zone": "Zone 13 - Guindy"},
    {"id": "SS-004", "name": "Koyambedu Substation", "voltage_kv": 110, "plinth_cm": 50.0, "lat": 13.0694, "lon": 80.1948, "zone": "Zone 8 - Anna Nagar"},
    {"id": "SS-005", "name": "Velachery Substation", "voltage_kv": 110, "plinth_cm": 40.0, "lat": 12.9815, "lon": 80.2180, "zone": "Zone 13 - Velachery"},
    {"id": "SS-006", "name": "Alandur Substation", "voltage_kv": 110, "plinth_cm": 45.0, "lat": 13.0031, "lon": 80.1989, "zone": "Zone 12 - Alandur"},
    {"id": "SS-007", "name": "Adyar Substation", "voltage_kv": 110, "plinth_cm": 50.0, "lat": 13.0064, "lon": 80.2575, "zone": "Zone 13 - Adyar"},
    {"id": "SS-008", "name": "Kilpauk Water Works Grid", "voltage_kv": 110, "plinth_cm": 60.0, "lat": 13.0782, "lon": 80.2415, "zone": "Zone 8 - Kilpauk"},
    {"id": "SS-009", "name": "Perambur Railway Substation", "voltage_kv": 110, "plinth_cm": 45.0, "lat": 13.1075, "lon": 80.2334, "zone": "Zone 6 - Thiru Vi Ka Nagar"},
    {"id": "SS-010", "name": "Anna Nagar West Substation", "voltage_kv": 230, "plinth_cm": 65.0, "lat": 13.0878, "lon": 80.2052, "zone": "Zone 8 - Anna Nagar"},
    {"id": "SS-011", "name": "Royapettah Substation", "voltage_kv": 110, "plinth_cm": 50.0, "lat": 13.0535, "lon": 80.2608, "zone": "Zone 9 - Royapettah"},
    {"id": "SS-012", "name": "Saidapet Substation", "voltage_kv": 110, "plinth_cm": 45.0, "lat": 13.0211, "lon": 80.2229, "zone": "Zone 10 - Saidapet"},
    {"id": "SS-013", "name": "Egmore Substation", "voltage_kv": 110, "plinth_cm": 55.0, "lat": 13.0732, "lon": 80.2609, "zone": "Zone 5 - Royapuram"},
    {"id": "SS-014", "name": "Tondiarpet Grid", "voltage_kv": 230, "plinth_cm": 50.0, "lat": 13.1280, "lon": 80.2872, "zone": "Zone 4 - Tondiarpet"},
    {"id": "SS-015", "name": "Thiruvanmiyur Substation", "voltage_kv": 110, "plinth_cm": 45.0, "lat": 12.9830, "lon": 80.2594, "zone": "Zone 13 - Thiruvanmiyur"},
    {"id": "SS-016", "name": "Pallavaram Substation", "voltage_kv": 110, "plinth_cm": 45.0, "lat": 12.9675, "lon": 80.1491, "zone": "Zone 12 - Pallavaram"},
    {"id": "SS-017", "name": "Tambaram Substation", "voltage_kv": 230, "plinth_cm": 60.0, "lat": 12.9249, "lon": 80.1165, "zone": "Zone 14 - Perungudi"},
    {"id": "SS-018", "name": "Madhavaram Substation", "voltage_kv": 110, "plinth_cm": 50.0, "lat": 13.1482, "lon": 80.2314, "zone": "Zone 3 - Madhavaram"},
    {"id": "SS-019", "name": "Ambattur Industrial Substation", "voltage_kv": 230, "plinth_cm": 60.0, "lat": 13.1143, "lon": 80.1548, "zone": "Zone 7 - Ambattur"},
    {"id": "SS-020", "name": "Porur Substation", "voltage_kv": 110, "plinth_cm": 45.0, "lat": 13.0382, "lon": 80.1565, "zone": "Zone 11 - Valasaravakkam"},
]

# Medical Oxygen Depots & Tertiary Healthcare Facilities
MEDICAL_OXYGEN_DEPOTS = [
    {
        "id": "O2-001",
        "name": "RGGGH Liquid Cryogenic Oxygen Depot (20 KL Tank)",
        "type": "Cryogenic Oxygen Plant",
        "plinth_cm": 75.0,
        "lat": 13.0805,
        "lon": 80.2785,
        "facility": "Rajiv Gandhi Govt General Hospital",
        "critical_capacity_kl": 20.0
    },
    {
        "id": "O2-002",
        "name": "Stanley Hospital LMO Vaporizer Yard (15 KL Tank)",
        "type": "Cryogenic Oxygen Plant",
        "plinth_cm": 65.0,
        "lat": 13.1070,
        "lon": 80.2870,
        "facility": "Government Stanley Medical College Hospital",
        "critical_capacity_kl": 15.0
    },
    {
        "id": "O2-003",
        "name": "KMC Kilpauk Oxygen Reservoir (13 KL Tank)",
        "type": "Cryogenic Oxygen Plant",
        "plinth_cm": 60.0,
        "lat": 13.0784,
        "lon": 80.2425,
        "facility": "Kilpauk Medical College Hospital",
        "critical_capacity_kl": 13.0
    },
    {
        "id": "O2-004",
        "name": "Apollo Hospitals Central Liquid Gas Farm (10 KL Tank)",
        "type": "Cryogenic Oxygen Plant",
        "plinth_cm": 70.0,
        "lat": 13.0604,
        "lon": 80.2514,
        "facility": "Apollo Hospitals Greams Road",
        "critical_capacity_kl": 10.0
    },
    {
        "id": "O2-005",
        "name": "MIOT International Medical Gas Depot (12 KL Tank)",
        "type": "Cryogenic Oxygen Plant",
        "plinth_cm": 80.0,
        "lat": 13.0185,
        "lon": 80.1856,
        "facility": "MIOT International Manapakkam",
        "critical_capacity_kl": 12.0
    }
]

@dataclass
class SubstationMonitoringResult:
    substation_id: str
    name: str
    voltage_kv: str
    latitude: str
    longitude: str
    road_segment_id: str
    ground_elevation_m: str
    plinth_height_m: str
    plinth_height_known: bool
    source_information: str
    forecast_depths: Dict[str, float]
    maximum_effective_depth: float
    maximum_forecast_horizon_affected: str
    flood_status: str
    uncertainty_flag: str
    explanation: str


class CriticalAssetsMonitor:
    def __init__(self, csv_path: str = "ai_service/layer4/data/substations.csv"):
        self.csv_path = csv_path
        self.substations = self._load_substations()
        self.oxygen_depots = MEDICAL_OXYGEN_DEPOTS

    def _load_substations(self) -> List[Dict[str, str]]:
        subs = []
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    subs.append(row)
        except Exception as e:
            logger.error(f"Failed to load substations from {self.csv_path}: {e}")
        return subs

    def evaluate_substations(self, temporal_service: TemporalFloodDepthService) -> List[SubstationMonitoringResult]:
        results = []
        horizons_min = [15.0, 30.0, 60.0, 90.0, 120.0, 180.0]
        horizon_labels = {
            15.0: "T+15", 30.0: "T+30", 60.0: "T+60", 
            90.0: "T+90", 120.0: "T+120", 180.0: "T+180"
        }

        for sub in self.substations:
            sub_id = sub.get("substation_id", "")
            seg_id = sub.get("road_segment_id", "")
            plinth_str = sub.get("plinth_height_m", "")
            
            plinth_known = bool(plinth_str.strip())
            
            # Defaults
            max_depth = 0.0
            max_horizon = "N/A"
            forecasts = {}
            status = STATUS_UNKNOWN
            uncertainty = ""
            explanation = ""
            
            if not seg_id:
                uncertainty = "NO_ROAD_MAPPING"
                explanation = "Substation is not mapped to a valid Layer 4 road segment. Flood forecast cannot be obtained."
            else:
                try:
                    is_data_available = True
                    for t in horizons_min:
                        try:
                            res_dict = temporal_service.get_effective_depth(seg_id, t)
                            depth = res_dict["effective_depth_cm"]
                        except ValueError:
                            is_data_available = False
                            break
                            
                        forecasts[horizon_labels[t]] = depth
                        if depth > max_depth:
                            max_depth = depth
                            max_horizon = horizon_labels[t]
                            
                    if not is_data_available:
                        status = STATUS_UNKNOWN
                        uncertainty = "DATA_UNAVAILABLE"
                        explanation = f"Substation is associated with road segment {seg_id}, but Layer 3 data is unavailable or missing."
                    else:
                        if not plinth_known:
                            status = STATUS_UNKNOWN
                            uncertainty = "PLINTH_UNKNOWN"
                            explanation = f"Substation is associated with road segment {seg_id}. The Layer 3 forecast reaches {max_depth:.1f} cm effective depth at {max_horizon}. The asset's authoritative plinth height is unavailable, so flood exposure cannot be determined with full confidence."
                        else:
                            plinth_cm = float(plinth_str) * 100.0 # Convert m to cm
                            margin = plinth_cm - max_depth
                            
                            if margin <= 0:
                                status = STATUS_CRITICAL
                                explanation = f"Substation is associated with road segment {seg_id}. The Layer 3 forecast reaches {max_depth:.1f} cm at {max_horizon}, exceeding the known plinth height by {abs(margin):.1f} cm! Flooding is imminent."
                            elif margin <= CRITICAL_MARGIN_CM:
                                status = STATUS_AT_RISK
                                explanation = f"Substation is associated with road segment {seg_id}. The Layer 3 forecast reaches {max_depth:.1f} cm at {max_horizon}. Margin ({margin:.1f} cm) is below critical threshold."
                            else:
                                status = STATUS_SAFE
                                explanation = f"Substation is associated with road segment {seg_id}. Maximum forecast depth {max_depth:.1f} cm at {max_horizon} is safely below plinth margin ({margin:.1f} cm clearance)."
                except Exception as e:
                    status = STATUS_UNKNOWN
                    uncertainty = "EVALUATION_ERROR"
                    explanation = f"Error evaluating risk: {str(e)}"

            res = SubstationMonitoringResult(
                substation_id=sub_id,
                name=sub.get("name", ""),
                voltage_kv=sub.get("voltage_kv", ""),
                latitude=sub.get("latitude", ""),
                longitude=sub.get("longitude", ""),
                road_segment_id=seg_id,
                ground_elevation_m=sub.get("ground_elevation_m", ""),
                plinth_height_m=plinth_str,
                plinth_height_known=plinth_known,
                source_information=sub.get("source_name", ""),
                forecast_depths=forecasts,
                maximum_effective_depth=round(max_depth, 2),
                maximum_forecast_horizon_affected=max_horizon,
                flood_status=status,
                uncertainty_flag=uncertainty,
                explanation=explanation
            )
            results.append(res)
            
        return results

    def compute_plinth_vulnerability(
        self,
        z_flood_cm: float,
        z_plinth_cm: float,
        margin_threshold_cm: float = 15.0
    ) -> Dict[str, Any]:
        """Calculates Plinth Vulnerability Index (PVI) and early warning action state."""
        margin_cm = z_plinth_cm - z_flood_cm
        pvi = round(z_flood_cm / max(1.0, z_plinth_cm), 3)

        if margin_cm <= 0.0:
            status = "BREAKER_TRIPPED_EMERGENCY"
            action_code = "TRIP_NOW"
            alert_text = (
                f"SUBMERGED PLINTH (Depth: {z_flood_cm:.1f} cm / Plinth: {z_plinth_cm:.0f} cm). "
                f"Negative margin ({margin_cm:.1f} cm). Breakers tripped to prevent catastrophic explosion."
            )
        elif margin_cm <= margin_threshold_cm:
            status = "CRITICAL_TRIP_RISK"
            action_code = "PREDICTIVE_TRIP_WARNING"
            alert_text = (
                f"PREDICTIVE DE-ENERGIZATION TRIGGERED! Flood depth {z_flood_cm:.1f} cm exceeds plinth margin "
                f"(Clearance: {margin_cm:.1f} cm <= {margin_threshold_cm:.0f} cm). Pre-emptive trip warning dispatched to SLDC."
            )
        elif margin_cm < 25.0:
            status = "WARNING"
            action_code = "DEPLOY_PUMPS"
            alert_text = (
                f"Elevated flood water ({z_flood_cm:.1f} cm). Margin: {margin_cm:.1f} cm. "
                f"Deploy high-capacity mobile dewatering pumps."
            )
        else:
            status = "NORMAL"
            action_code = "MONITOR"
            alert_text = f"Secure ({z_flood_cm:.1f} cm). Plinth clearance margin: {margin_cm:.1f} cm."

        return {
            "water_depth_cm": round(z_flood_cm, 1),
            "plinth_cm": z_plinth_cm,
            "margin_cm": round(margin_cm, 1),
            "pvi": pvi,
            "status": status,
            "action_code": action_code,
            "alert_text": alert_text,
            "trip_warning_active": margin_cm <= margin_threshold_cm
        }

    def evaluate_substation_risks(self, depths_cm: Any) -> Dict[str, Any]:
        """Assesses electrical substation plinth vulnerability across catalog."""
        results = []
        critical_count = 0
        warning_count = 0
        normal_count = 0

        for i, ss in enumerate(CHENNAI_SUBSTATIONS):
            water_depth = float(depths_cm[i]) if hasattr(depths_cm, '__getitem__') and i < len(depths_cm) else 0.0
            plinth = ss["plinth_cm"]
            vuln = self.compute_plinth_vulnerability(water_depth, plinth, margin_threshold_cm=15.0)

            if vuln["status"] in ("CRITICAL_TRIP_RISK", "BREAKER_TRIPPED_EMERGENCY"):
                critical_count += 1
            elif vuln["status"] == "WARNING":
                warning_count += 1
            else:
                normal_count += 1

            results.append({
                "id": ss["id"],
                "name": ss["name"],
                "voltage_kv": ss["voltage_kv"],
                "zone": ss.get("zone", "GCC"),
                "plinth_cm": plinth,
                "water_depth_cm": vuln["water_depth_cm"],
                "plinth_clearance_cm": vuln["margin_cm"],
                "pvi_ratio": vuln["pvi"],
                "status": vuln["status"],
                "action_alert": vuln["alert_text"],
                "trip_warning_active": vuln["trip_warning_active"],
                "lat": ss["lat"],
                "lon": ss["lon"]
            })

        return {
            "total_substations": len(CHENNAI_SUBSTATIONS),
            "critical_count": critical_count,
            "warning_count": warning_count,
            "normal_count": normal_count,
            "substations": results
        }

    def evaluate_medical_oxygen_depots(self, depths_cm: Any) -> Dict[str, Any]:
        """Assesses flood vulnerability for hospital liquid medical oxygen depots."""
        results = []
        critical_count = 0
        warning_count = 0
        normal_count = 0

        for i, depot in enumerate(MEDICAL_OXYGEN_DEPOTS):
            water_depth = float(depths_cm[i]) if hasattr(depths_cm, '__getitem__') and i < len(depths_cm) else 0.0
            plinth = depot["plinth_cm"]
            vuln = self.compute_plinth_vulnerability(water_depth, plinth, margin_threshold_cm=15.0)

            if vuln["status"] in ("CRITICAL_TRIP_RISK", "BREAKER_TRIPPED_EMERGENCY"):
                critical_count += 1
                depot_action = (
                    f"CRITICAL: Flood depth {water_depth:.1f} cm threatens cryogenic vaporizer. "
                    f"Switch hospital ICU to emergency secondary oxygen cylinder manifold!"
                )
            elif vuln["status"] == "WARNING":
                warning_count += 1
                depot_action = f"WARNING: Water {water_depth:.1f} cm approaching O2 pad. Deploy sandbag bunds."
            else:
                normal_count += 1
                depot_action = f"SECURE: Oxygen pad clear. Margin {vuln['margin_cm']:.1f} cm."

            results.append({
                "id": depot["id"],
                "name": depot["name"],
                "facility": depot["facility"],
                "capacity_kl": depot["critical_capacity_kl"],
                "plinth_cm": plinth,
                "water_depth_cm": vuln["water_depth_cm"],
                "margin_cm": vuln["margin_cm"],
                "pvi_ratio": vuln["pvi"],
                "status": vuln["status"],
                "action_alert": depot_action,
                "trip_warning_active": vuln["trip_warning_active"],
                "lat": depot["lat"],
                "lon": depot["lon"]
            })

        return {
            "total_depots": len(MEDICAL_OXYGEN_DEPOTS),
            "critical_count": critical_count,
            "warning_count": warning_count,
            "normal_count": normal_count,
            "oxygen_depots": results
        }
