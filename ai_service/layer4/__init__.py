"""Layer 4: Dynamic Safe Emergency Navigation & Critical Assets Safeguarding (GCC / MoES 26085).

Authoritative public API for flood-aware A* emergency routing, multi-vehicle clearance
matrix enforcement (ambulance, rescue truck, car, two-wheeler), hydrodynamic impedance
travel cost calculation, and critical infrastructure (TANGEDCO 230kV/110kV substations)
plinth submergence monitoring.
"""

from .routing_engine import DynamicRoutingEngine, RouteRequest, SnappingResult
from .risk_cost_evaluator import (
    VehicleRiskConfig,
    FloodHazardEvaluator,
    RiskCostEvaluator,
    VehicleProfile,
    VEHICLE_PROFILES,
)
from .critical_assets_monitor import (
    CriticalAssetsMonitor,
    CHENNAI_SUBSTATIONS,
    MEDICAL_OXYGEN_DEPOTS,
)
from .pipeline import Layer4Pipeline, Layer4Result
from .service import Layer4Service

__all__ = [
    "DynamicRoutingEngine",
    "RouteRequest",
    "SnappingResult",
    "VehicleRiskConfig",
    "FloodHazardEvaluator",
    "RiskCostEvaluator",
    "VehicleProfile",
    "VEHICLE_PROFILES",
    "CriticalAssetsMonitor",
    "CHENNAI_SUBSTATIONS",
    "MEDICAL_OXYGEN_DEPOTS",
    "Layer4Pipeline",
    "Layer4Result",
    "Layer4Service",
]
