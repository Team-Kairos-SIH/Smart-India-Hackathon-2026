"""
Layer 2 Add-on: Coastal Tidal Lockout & Cyclonic Storm Surge Boundary Engine
Smart India Hackathon 2026 (Problem Statement #26085)
Greater Chennai Corporation (GCC) & MoES / NCMRWF Pilot

Models astronomical tidal harmonics (Chennai Port Survey of India station) coupled with
Holland cyclonic wind setup and inverted barometer surge for the Bay of Bengal.
Evaluates outfall tailwater head and backwater intrusion at:
  - Adyar River Estuary
  - Cooum River Mouth
  - Buckingham Canal Outfalls
  - Ennore Creek
"""

from dataclasses import dataclass
import math
import time
from typing import Any, Dict, List, Optional


@dataclass
class CoastalOutfallStatus:
    outfall_name: str
    bed_invert_m_msl: float
    sea_water_level_m_msl: float
    upstream_hgl_m_msl: float
    head_difference_m: float
    discharge_status: str  # FREE_GRAVITY, THROTTLED_BACKWATER, TIDAL_LOCKOUT, REVERSE_INTRUSION
    throttling_factor: float
    effective_discharge_ratio: float


class CoastalBoundaryEngine:
    """
    Computes astronomical tide, cyclonic storm surge, and coastal outfall lockout states.
    """

    # Survey of India / INCOIS Tidal Constants for Chennai Port
    CONSTITUENTS = [
        {"name": "M2", "period_hr": 12.4206, "speed_deg_hr": 28.9841, "amplitude_m": 0.420, "phase_deg": 124.5},
        {"name": "S2", "period_hr": 12.0000, "speed_deg_hr": 30.0000, "amplitude_m": 0.180, "phase_deg": 162.0},
        {"name": "N2", "period_hr": 12.6583, "speed_deg_hr": 28.4397, "amplitude_m": 0.085, "phase_deg": 108.2},
        {"name": "K1", "period_hr": 23.9345, "speed_deg_hr": 15.0411, "amplitude_m": 0.142, "phase_deg": 198.4},
        {"name": "O1", "period_hr": 25.8193, "speed_deg_hr": 13.9430, "amplitude_m": 0.065, "phase_deg": 182.1},
        {"name": "M4", "period_hr": 6.2103,  "speed_deg_hr": 57.9682, "amplitude_m": 0.022, "phase_deg": 215.0},
    ]

    CHENNAI_OUTFALLS = [
        {"name": "Adyar River Estuary (Besant Nagar)", "invert_m": 0.50, "default_hgl": 1.40, "area_m2": 45.0},
        {"name": "Cooum River Mouth (Napier Bridge)", "invert_m": 0.40, "default_hgl": 1.25, "area_m2": 38.0},
        {"name": "Buckingham Canal Lockout (Mylapore/Adyar)", "invert_m": 0.30, "default_hgl": 1.10, "area_m2": 25.0},
        {"name": "Ennore Creek (Kosasthalaiyar Outlet)", "invert_m": 0.70, "default_hgl": 1.65, "area_m2": 60.0},
    ]

    def __init__(self, datum_offset_m: float = 0.0):
        self.datum_offset_m = datum_offset_m

    def compute_astronomical_tide(self, t_hours: float = 0.0) -> float:
        """
        Harmonic superposition of astronomical tidal constituents.
        """
        elev = self.datum_offset_m
        for c in self.CONSTITUENTS:
            omega = math.radians(c["speed_deg_hr"])
            phase = math.radians(c["phase_deg"])
            elev += c["amplitude_m"] * math.cos(omega * t_hours - phase)
        return round(elev, 3)

    def compute_cyclonic_surge(
        self,
        central_pressure_hpa: float = 980.0,
        ambient_pressure_hpa: float = 1013.0,
        sustained_wind_speed_kmh: float = 90.0,
        continental_shelf_width_km: float = 40.0,
        mean_shelf_depth_m: float = 25.0
    ) -> float:
        """
        Calculates storm surge using inverted barometer effect + Holland wind setup.
        """
        # 1. Inverted Barometer Effect: ~1 cm per 1 hPa pressure deficit
        delta_p = max(0.0, ambient_pressure_hpa - central_pressure_hpa)
        ib_surge_m = delta_p * 0.01

        # 2. Wind Stress Setup
        w_ms = sustained_wind_speed_kmh / 3.6
        cd = (0.8 + 0.065 * w_ms) * 1e-3
        rho_air = 1.22
        rho_water = 1025.0
        g = 9.81

        tau_wind = rho_air * cd * (w_ms ** 2)
        wind_surge_m = (tau_wind * (continental_shelf_width_km * 1000.0)) / (rho_water * g * mean_shelf_depth_m)

        # 3. Wave Setup
        wave_surge_m = 0.15 * min(4.0, (w_ms / 15.0) ** 1.5)

        total_surge = round(ib_surge_m + wind_surge_m + wave_surge_m, 3)
        return max(0.0, total_surge)

    def evaluate_outfall_states(
        self,
        t_hours: float = 0.0,
        cyclonic_surge_m: float = 0.0,
        storm_scenario: str = "monsoon"
    ) -> Dict[str, Any]:
        """
        Evaluates coastal boundary conditions and outfall lockout status across Chennai.
        """
        # Scenario default surge if not overridden
        if cyclonic_surge_m == 0.0:
            if storm_scenario.lower() == "michaung":
                cyclonic_surge_m = 0.85
            elif storm_scenario.lower() == "2015_flood":
                cyclonic_surge_m = 0.65
            elif storm_scenario.lower() == "monsoon":
                cyclonic_surge_m = 0.25

        astro_tide = self.compute_astronomical_tide(t_hours)
        sea_level_m = round(astro_tide + cyclonic_surge_m, 3)

        outfalls_data = []
        locked_out_count = 0

        for out in self.CHENNAI_OUTFALLS:
            invert = out["invert_m"]
            hgl = out["default_hgl"]
            head_diff = round(hgl - sea_level_m, 3)

            if sea_level_m <= invert:
                status = "FREE_GRAVITY"
                eff_ratio = 1.0
                throttling = 0.0
            elif sea_level_m < hgl:
                status = "THROTTLED_BACKWATER"
                # Submerged orifice equation ratio: sqrt((hgl - sea) / (hgl - invert))
                delta_total = max(0.05, hgl - invert)
                eff_ratio = round(math.sqrt(max(0.01, head_diff / delta_total)), 3)
                throttling = round(1.0 - eff_ratio, 3)
            elif abs(head_diff) <= 0.05:
                status = "TIDAL_LOCKOUT"
                eff_ratio = 0.0
                throttling = 1.0
                locked_out_count += 1
            else:
                status = "REVERSE_INTRUSION"
                eff_ratio = -round(math.sqrt(min(2.0, abs(head_diff))), 3)
                throttling = 1.0
                locked_out_count += 1

            outfalls_data.append({
                "outfall_name": out["name"],
                "bed_invert_m_msl": invert,
                "sea_water_level_m_msl": sea_level_m,
                "upstream_hgl_m_msl": hgl,
                "head_difference_m": head_diff,
                "discharge_status": status,
                "throttling_factor": throttling,
                "effective_discharge_ratio": eff_ratio,
            })

        return {
            "timestamp_offset_hours": t_hours,
            "astronomical_tide_m_msl": astro_tide,
            "cyclonic_surge_m": cyclonic_surge_m,
            "total_coastal_head_m_msl": sea_level_m,
            "tidal_regime": "Semi-diurnal (Spring/Neap active)",
            "outfalls_monitored": len(self.CHENNAI_OUTFALLS),
            "outfalls_locked_out": locked_out_count,
            "outfalls": outfalls_data,
        }
