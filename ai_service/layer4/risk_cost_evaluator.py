import math

class VehicleRiskConfig:
    """
    Centralized configuration for vehicle-specific flood tolerances.
    NOTE: These values are PROJECT ASSUMPTIONS for KAIROS, not universal engineering standards.
    They represent the maximum effective flood depth (in cm) a vehicle can safely traverse.
    """
    TOLERANCES_CM = {
        "two_wheeler": 10.0,
        "passenger_car": 18.0,
        "ambulance": 30.0,
        "ndrf_heavy_rescue": 45.0
    }
    
    @classmethod
    def get_limit_cm(cls, vehicle_type: str) -> float:
        if vehicle_type not in cls.TOLERANCES_CM:
            raise ValueError(f"Unknown vehicle type: '{vehicle_type}'. Supported: {list(cls.TOLERANCES_CM.keys())}")
        return cls.TOLERANCES_CM[vehicle_type]


class FloodHazardEvaluator:
    """
    Evaluates the hazard ratio and passability of a road segment for a specific vehicle.
    """
    @staticmethod
    def evaluate_road_risk(segment_id: str, length_m: float, free_flow_speed_kmh: float, effective_depth_cm: float, vehicle_type: str, k: float = 5.0, p: float = 2.0) -> dict:
        """
        Calculates the complete road-risk evaluation for a specific vehicle on a specific road segment.
        
        Cost Formula for passable roads:
        cost = (L / v0) * (1 + k * r^p)
        where v0 is converted to m/s.
        """
        # 1. Validate segment_id
        if not segment_id:
            raise ValueError("Segment ID cannot be empty.")
            
        # 2. Validate vehicle type
        limit_cm = VehicleRiskConfig.get_limit_cm(vehicle_type)
        if limit_cm <= 0:
            raise ValueError(f"Vehicle depth limit must be strictly positive, got {limit_cm}cm")
            
        # 3. Validate numeric inputs and thresholds
        for val, name in [(effective_depth_cm, "effective_depth_cm"), 
                          (length_m, "length_m"), 
                          (free_flow_speed_kmh, "free_flow_speed_kmh"),
                          (k, "k"), 
                          (p, "p")]:
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                raise TypeError(f"{name} must be strictly numeric.")
            if math.isnan(val):
                raise ValueError(f"{name} cannot be NaN.")
            if math.isinf(val):
                raise ValueError(f"{name} cannot be infinite.")
                
        if effective_depth_cm < 0:
            raise ValueError(f"effective_depth_cm cannot be negative, got {effective_depth_cm}cm")
        if length_m <= 0:
            raise ValueError(f"length_m must be strictly positive, got {length_m}m")
        if free_flow_speed_kmh <= 0:
            raise ValueError(f"free_flow_speed_kmh must be strictly positive, got {free_flow_speed_kmh}km/h")
            
        # 4. Calculate hazard ratio (r)
        hazard_ratio = float(effective_depth_cm) / float(limit_cm)
        
        # 5. Blocking decision
        is_passable = hazard_ratio < 1.0
        status = "PASSABLE" if is_passable else "BLOCKED"
        
        # 6. WHPF Hazard Cost and Travel Time Calculation
        # EXPLICIT UNIT CONVERSION:
        # The routing graph stores free_flow_speed in km/h.
        # We must convert this to meters per second to match length_m.
        # 1 km/h = 1000m / 3600s = 1 / 3.6 m/s
        speed_m_per_second = free_flow_speed_kmh / 3.6
        baseline_time_seconds = length_m / speed_m_per_second
        
        if is_passable:
            # v = v0 * (1 - 0.7*r)
            # Ensure speed does not drop below zero in edge cases
            adjusted_speed_m_per_second = max(0.0, speed_m_per_second * (1.0 - 0.7 * hazard_ratio))
            
            # t = L / v
            if adjusted_speed_m_per_second > 0:
                actual_travel_time_seconds = length_m / adjusted_speed_m_per_second
            else:
                actual_travel_time_seconds = float("inf")
                
            # cost = (L / v0) * (1 + k * r^p)
            hazard_cost_seconds = baseline_time_seconds * (1.0 + k * math.pow(hazard_ratio, p))
        else:
            # Do not calculate normal WHPF cost or speed for a blocked edge.
            adjusted_speed_m_per_second = None
            actual_travel_time_seconds = float("inf")
            hazard_cost_seconds = float("inf")
        
        return {
            "segment_id": segment_id,
            "vehicle_type": vehicle_type,
            "vehicle_depth_limit_cm": limit_cm,
            "effective_depth_cm": float(effective_depth_cm),
            "hazard_ratio": round(hazard_ratio, 4),
            "is_passable": is_passable,
            "status": status,
            "free_flow_speed_kmh": float(free_flow_speed_kmh),
            "free_flow_speed_m_per_s": round(speed_m_per_second, 3),
            "adjusted_speed_m_per_s": round(adjusted_speed_m_per_second, 3) if adjusted_speed_m_per_second is not None else None,
            "free_flow_travel_time_seconds": round(baseline_time_seconds, 2),
            "actual_travel_time_seconds": round(actual_travel_time_seconds, 2) if not math.isinf(actual_travel_time_seconds) else float('inf'),
            "hazard_cost_seconds": float(hazard_cost_seconds) if not math.isinf(hazard_cost_seconds) else float('inf'),
            "k": float(k),
            "p": float(p)
        }


from dataclasses import dataclass
from typing import Dict, Optional
import numpy as np


@dataclass
class VehicleProfile:
    """Hydrodynamic parameters and wading thresholds for emergency and civilian vehicles."""
    name: str
    d_safe_cm: float
    d_critical_cm: float
    base_speed_kmh: float
    critical_dv_m2_s: float
    alpha: float
    gamma: float
    beta_v: float = 3.0
    description: str = ""


VEHICLE_PROFILES: Dict[str, VehicleProfile] = {
    "ambulance": VehicleProfile(
        name="Emergency Ambulance (Force / Tata Winger 407)",
        d_safe_cm=10.0,
        d_critical_cm=30.0,
        base_speed_kmh=45.0,
        critical_dv_m2_s=0.45,
        alpha=2.5,
        gamma=2.0,
        beta_v=2.5,
        description="Priority Tier 1 Patient Transport. Engine air-intake and electrical ICU equipment at 30 cm height."
    ),
    "rescue_truck": VehicleProfile(
        name="NDRF / Fire Rescue Heavy Truck (4x4)",
        d_safe_cm=25.0,
        d_critical_cm=60.0,
        base_speed_kmh=35.0,
        critical_dv_m2_s=1.05,
        alpha=1.8,
        gamma=1.5,
        beta_v=2.0,
        description="Ashok Leyland 4x4 / BharatBenz Heavy Rescue Vehicle / GCC JCB. Critical clearance 60 cm (raised wading snorkel)."
    ),
    "civilian_car": VehicleProfile(
        name="Civilian Passenger Car (Sedan / Hatchback)",
        d_safe_cm=8.0,
        d_critical_cm=18.0,
        base_speed_kmh=30.0,
        critical_dv_m2_s=0.30,
        alpha=4.0,
        gamma=2.2,
        beta_v=3.0,
        description="Civilian passenger sedan/hatchback/compact SUV. Critical clearance 18 cm."
    ),
    "two_wheeler": VehicleProfile(
        name="Civilian Two-Wheeler (Motorcycle / Scooter)",
        d_safe_cm=3.0,
        d_critical_cm=10.0,
        base_speed_kmh=20.0,
        critical_dv_m2_s=0.15,
        alpha=6.0,
        gamma=2.5,
        beta_v=4.0,
        description="Motorcycle / Scooter. Critical clearance 10 cm (exhaust backflow, spark plug short)."
    ),
}

VEHICLE_PROFILES["civilian_evac"] = VEHICLE_PROFILES["civilian_car"]


class RiskCostEvaluator:
    """Evaluates dynamic routing impedance weights and hydrodynamic traversal travel times."""

    def __init__(self, vehicle_type: str = "ambulance"):
        v_key = vehicle_type.lower()
        if v_key not in VEHICLE_PROFILES:
            raise ValueError(f"Unknown vehicle type '{vehicle_type}'. Valid: {list(VEHICLE_PROFILES.keys())}")
        self.profile = VEHICLE_PROFILES[v_key]
        self.base_speed_mps = (self.profile.base_speed_kmh * 1000.0) / 3600.0

    def compute_effective_velocity(self, depth_cm: float) -> float:
        """Calculates effective velocity under hydrodynamic drag: V_eff = V_base * (1 - (d / d_c)^2)"""
        p = self.profile
        if depth_cm >= p.d_critical_cm:
            return 0.0
        if depth_cm <= 0.0:
            return self.base_speed_mps

        ratio = depth_cm / p.d_critical_cm
        degradation = max(0.05, 1.0 - (ratio * ratio))
        return self.base_speed_mps * degradation

    def compute_edge_traversal_cost(
        self,
        length_m: float,
        depth_cm: float,
        velocity_mps: float = 0.0,
        enforce_cutoff: bool = True
    ) -> float:
        """Computes dynamic hydrodynamic traversal cost C(e, t) in seconds."""
        p = self.profile
        d_m = depth_cm / 100.0
        dv_product = d_m * abs(velocity_mps)

        if enforce_cutoff:
            if depth_cm >= p.d_critical_cm or dv_product >= p.critical_dv_m2_s:
                return float("inf")

        v_eff = self.compute_effective_velocity(depth_cm)
        if v_eff <= 1e-3:
            return float("inf")

        base_traversal_time_s = length_m / v_eff

        inundation_penalty_s = 0.0
        if depth_cm > p.d_safe_cm:
            depth_span = max(1.0, p.d_critical_cm - p.d_safe_cm)
            norm_excess = (depth_cm - p.d_safe_cm) / depth_span
            inundation_penalty_s = p.alpha * (norm_excess ** p.gamma) * (length_m / self.base_speed_mps)

        velocity_penalty_s = 0.0
        if dv_product > 0.0:
            norm_dv = min(1.0, dv_product / p.critical_dv_m2_s)
            velocity_penalty_s = p.beta_v * (norm_dv ** 2) * (length_m / self.base_speed_mps)

        return base_traversal_time_s + inundation_penalty_s + velocity_penalty_s

    def compute_edge_impedance(
        self,
        lengths_m: np.ndarray,
        depths_cm: np.ndarray,
        velocities_mps: Optional[np.ndarray] = None,
        enforce_cutoff: bool = True
    ) -> np.ndarray:
        """Vectorized computation of dynamic edge traversal weights."""
        p = self.profile
        weights = lengths_m.astype(np.float64).copy()

        valid_mask = depths_cm < p.d_critical_cm
        safe_ratios = np.clip(depths_cm[valid_mask] / p.d_critical_cm, 0.0, 0.98)
        drag_factors = 1.0 / np.maximum(0.04, 1.0 - (safe_ratios ** 2))
        weights[valid_mask] *= drag_factors

        risk_mask = valid_mask & (depths_cm > p.d_safe_cm)
        if np.any(risk_mask):
            depth_span = max(1.0, p.d_critical_cm - p.d_safe_cm)
            norm_excess = (depths_cm[risk_mask] - p.d_safe_cm) / depth_span
            weights[risk_mask] += lengths_m[risk_mask] * p.alpha * np.power(norm_excess, p.gamma)

        if velocities_mps is not None:
            d_m = depths_cm / 100.0
            dv = d_m * np.abs(velocities_mps)
            v_mask = valid_mask & (dv > 0.0)
            if np.any(v_mask):
                norm_dv = np.clip(dv[v_mask] / p.critical_dv_m2_s, 0.0, 1.0)
                weights[v_mask] += lengths_m[v_mask] * p.beta_v * np.square(norm_dv)

            if enforce_cutoff:
                weights[dv >= p.critical_dv_m2_s] = np.inf

        if enforce_cutoff:
            weights[depths_cm >= p.d_critical_cm] = np.inf

        return weights

    def estimate_travel_time_min(
        self,
        length_m: float,
        depth_cm: float,
        velocity_mps: float = 0.0
    ) -> float:
        """Estimates traversal duration in minutes considering water speed degradation."""
        p = self.profile
        if depth_cm >= p.d_critical_cm:
            return float("inf")

        d_m = depth_cm / 100.0
        if (d_m * abs(velocity_mps)) >= p.critical_dv_m2_s:
            return float("inf")

        v_eff = self.compute_effective_velocity(depth_cm)
        if v_eff <= 1e-3:
            return float("inf")

        return (length_m / v_eff) / 60.0
