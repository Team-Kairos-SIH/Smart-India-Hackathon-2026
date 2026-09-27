"""
Layer 3 Add-on: "Street-as-Canal" Conveyance & Velocity-Depth (v × d) Hydrodynamic Hazard Engine
Smart India Hackathon 2026 (Problem Statement #26085)
Greater Chennai Corporation (GCC) & MoES / NCMRWF Pilot

When subterranean storm drains surcharge, urban streets act as the "Major Drainage System"
(open conveyance channels). This engine evaluates:
  1. Manning's open-channel street flow velocity: v = (1/n) * R_h^(2/3) * S_0^(1/2)
  2. Street corridor discharge: Q = v * A_flow = v * W_road * d_water
  3. International Velocity-Depth Product (v × d) Hydrodynamic Wash-Away Hazard:
     - v × d < 0.4 m²/s: Low hazard (pedestrian wading safe)
     - 0.4 <= v × d < 0.6 m²/s: Moderate hazard (children & two-wheelers lose footing)
     - 0.6 <= v × d < 1.2 m²/s: High hazard (Passenger cars & auto-rickshaws float/washed away)
     - v × d >= 1.2 m²/s: Extreme hazard (Ambulances & heavy trucks lose control)
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


# Road class standard geometric parameters (CPHEEO / IRC guidelines)
ROAD_CLASS_WIDTHS_M = {
    "motorway": 24.0,
    "trunk": 20.0,
    "primary": 16.0,
    "primary_link": 12.0,
    "secondary": 12.0,
    "secondary_link": 10.0,
    "main": 14.0,
    "tertiary": 9.0,
    "tertiary_link": 7.5,
    "street": 7.0,
    "street_limited": 6.0,
    "residential": 5.5,
    "service": 4.5,
    "living_street": 4.5,
    "major_rail": 8.0,
    "minor_rail": 5.0,
    "path": 2.5,
    "driveway": 3.0,
}

# Manning roughness for urban road surfaces (asphalt with light debris)
MANNING_N_ROAD = 0.016


@dataclass
class StreetConveyanceResult:
    """Output summary of street flow velocity and hydrodynamic hazard evaluation."""
    dataframe: pd.DataFrame
    summary_metrics: Dict[str, Any]
    high_hazard_segments: List[Dict[str, Any]]


class StreetConveyanceEngine:
    """
    Computes street-surface open-channel flow velocities, discharges, and wash-away hazards.
    """

    def __init__(self, manning_n: float = MANNING_N_ROAD):
        self.manning_n = manning_n

    def compute_street_flow(
        self,
        roads_df: pd.DataFrame,
        horizon_min: int = 60,
        default_slope: float = 0.002
    ) -> StreetConveyanceResult:
        """
        Calculates flow velocity, corridor discharge, and v × d hazard across road segments.

        Parameters:
          roads_df: DataFrame containing at least segment_id, terrain_slope_m_per_m (or elevation),
                    and depth_T+{horizon_min}m_cm (or depth in cm).
          horizon_min: Forecast horizon to evaluate (default: 60).
          default_slope: Minimum fallback longitudinal street slope S_0.
        """
        df = roads_df.copy()
        depth_col = f"depth_T+{horizon_min}m_cm"
        if depth_col not in df.columns:
            # Fallback to any available depth column or create from d_T+
            candidates = [c for c in df.columns if "depth" in c.lower()]
            if candidates:
                depth_col = candidates[0]
            else:
                df[depth_col] = 15.0

        n_rows = len(df)

        # 1. Resolve Water Depths (convert cm to meters)
        d_cm = df[depth_col].values.astype(np.float32)
        d_m = np.maximum(0.0, d_cm / 100.0)

        # 2. Resolve Longitudinal Street Slopes S_0
        if "terrain_slope_m_per_m" in df.columns:
            s0 = np.maximum(0.0005, df["terrain_slope_m_per_m"].values.astype(np.float32))
        else:
            s0 = np.full(n_rows, default_slope, dtype=np.float32)

        # 3. Resolve Road Widths W (m)
        if "road_class" in df.columns:
            widths = np.array([ROAD_CLASS_WIDTHS_M.get(str(rc).lower(), 7.0) for rc in df["road_class"]], dtype=np.float32)
        else:
            widths = np.full(n_rows, 8.0, dtype=np.float32)

        # 4. Hydraulic Radius: R_h = A / P = (W * d) / (W + 2*d)
        w_d = widths * d_m
        p_wetted = widths + 2.0 * d_m
        rh = np.where(p_wetted > 0, w_d / p_wetted, 0.0).astype(np.float32)

        # 5. Manning Flow Velocity: v = (1 / n) * R_h^(2/3) * S_0^(1/2) (m/s)
        # Suppress velocity if water depth is negligible (< 1 cm)
        raw_v = (1.0 / self.manning_n) * (np.maximum(0.0, rh) ** (2.0 / 3.0)) * np.sqrt(s0)
        v_flow = np.where(d_m > 0.01, np.clip(raw_v, 0.0, 4.5), 0.0).astype(np.float32)

        # 6. Corridor Discharge: Q = v * A_flow = v * W * d (m³/s)
        q_corridor = v_flow * w_d

        # 7. Velocity-Depth Product: v × d (m²/s)
        v_x_d = v_flow * d_m

        # 8. International Wash-Away Hazard Tiers (UK DEFRA / Australian ARR)
        hazard_tiers = []
        for vxd in v_x_d:
            if vxd < 0.4:
                hazard_tiers.append("LOW (Pedestrian Safe)")
            elif vxd < 0.6:
                hazard_tiers.append("MODERATE (Pedestrian Hazard)")
            elif vxd < 1.2:
                hazard_tiers.append("HIGH (Vehicle Floatation & Wash-Away)")
            else:
                hazard_tiers.append("EXTREME (Heavy Emergency Transport Hazard)")

        df = df.assign(
            flow_velocity_m_s=np.round(v_flow, 2),
            corridor_discharge_m3_s=np.round(q_corridor, 2),
            hazard_vx_d_m2_s=np.round(v_x_d, 3),
            washaway_hazard_tier=hazard_tiers,
            is_street_channel=(q_corridor > 1.0) & (v_flow > 0.5)
        )

        # High-hazard hotspots
        high_mask = v_x_d >= 0.6
        high_df = df[high_mask]
        hotspots = []
        for _, r in high_df.head(20).iterrows():
            hotspots.append({
                "segment_id": str(r.get("segment_id", "N/A")),
                "road_name": str(r.get("road_name", f"Corridor {r.get('segment_id', '')}")),
                "depth_cm": float(r.get(depth_col, 0.0)),
                "velocity_m_s": float(r.get("flow_velocity_m_s", 0.0)),
                "discharge_m3_s": float(r.get("corridor_discharge_m3_s", 0.0)),
                "hazard_vx_d": float(r.get("hazard_vx_d_m2_s", 0.0)),
                "washaway_hazard_tier": str(r.get("washaway_hazard_tier", "HIGH"))
            })

        summary = {
            "evaluated_segments": n_rows,
            "horizon_min": horizon_min,
            "active_street_channels_count": int(np.sum(df["is_street_channel"])),
            "mean_velocity_m_s": round(float(np.mean(v_flow[d_m > 0.02])), 2) if np.any(d_m > 0.02) else 0.0,
            "max_velocity_m_s": round(float(np.max(v_flow)), 2),
            "max_discharge_m3_s": round(float(np.max(q_corridor)), 2),
            "vehicle_floatation_hazard_segments": int(np.sum(v_x_d >= 0.6)),
            "extreme_washaway_hazard_segments": int(np.sum(v_x_d >= 1.2)),
        }

        return StreetConveyanceResult(
            dataframe=df,
            summary_metrics=summary,
            high_hazard_segments=hotspots
        )
