"""
KAIROS: Master 5-Layer Hydrodynamic & Tactical Emergency Digital Twin Orchestrator
Smart India Hackathon 2026 (Problem Statement #26085)
Ministry of Earth Sciences (MoES) & Greater Chennai Corporation (GCC) Pilot

Chains all 5 layers into a single in-memory execution pipeline:
  Layer 0: Multi-Sensor Rainfall Nowcasting & CML Virtual Gauge Mesh
  Layer 1: 2D Micro-Topography, Cartosat-1 DEM & Soil Runoff
  Layer 2: 1D Subsurface Stormwater Conduit Hydraulics, Clogging & Coastal Tide
  Layer 3: Mass-Conserved PI-GNN Surrogate & "Street-as-Canal" Conveyance
  Layer 4: First Responder Clearance Navigation & Municipal Pump Dispatch
"""

import argparse
from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd

# Layer imports (lazy loaded with safe fallbacks)
from ..layer0.pipeline import Layer0Pipeline
from ..layer0.cml_mesh import CMLMeshRetriever
from ..layer1.lulc.runoff_generator import SurfaceRunoffGenerator
from ..layer2.pipeline import Layer2Pipeline
from ..layer2.coastal_boundary import CoastalBoundaryEngine
from ..layer3.pipeline import Layer3Pipeline
from ..layer3.street_conveyance import StreetConveyanceEngine
from ..layer4.service import Layer4Service
from ..layer4.pump_optimizer import MunicipalPumpOptimizer
from ..layer4.cap_emitter import CAPAlertEmitter

logger = logging.getLogger(__name__)


@dataclass
class MasterTwinResult:
    """Encapsulates the end-to-end execution of all 5 layers."""
    dataframe: pd.DataFrame
    horizons_depths: Dict[int, np.ndarray]
    diagnostics: Dict[str, Any]
    pump_recommendations: List[Dict[str, Any]]
    coastal_outfall_status: Dict[str, Any]
    cml_telemetry: Dict[str, Any]
    street_conveyance_summary: Dict[str, Any]

    def to_kpi_summary(self) -> Dict[str, Any]:
        """Returns high-level executive KPIs for the ICCC Command Twin."""
        d60 = self.horizons_depths.get(60, np.zeros(len(self.dataframe)))
        d_cm_max = float(np.max(d60)) if len(d60) > 0 else 0.0
        inundated_roads = int(np.sum(d60 >= 10.0))
        critical_roads = int(np.sum(d60 >= 30.0))

        return {
            "status": "success",
            "active_road_segments": len(self.dataframe),
            "peak_depth_t60_cm": round(d_cm_max, 1),
            "inundated_roads_count": inundated_roads,
            "critical_impassable_roads_count": critical_roads,
            "coastal_outfalls_locked": self.coastal_outfall_status.get("outfalls_locked_out", 0),
            "recommended_pumps_count": len(self.pump_recommendations),
            "cml_mesh_mean_rain_mm_hr": self.cml_telemetry.get("mesh_mean_rain_rate_mm_hr", 0.0),
            "total_execution_ms": self.diagnostics.get("total_runtime_ms", 0.0)
        }


class MasterTwinCoupler:
    """
    Unified In-Memory Master Orchestrator for the 5-Layer Urban Flood Nowcasting Twin.
    """

    def __init__(self, base_dir: Optional[Union[str, Path]] = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parents[2]
        
        # Instantiate engines
        self.l0_pipeline = Layer0Pipeline()
        self.cml_retriever = CMLMeshRetriever()
        self.runoff_gen = SurfaceRunoffGenerator(base_dir=self.base_dir)
        self.l2_pipeline = Layer2Pipeline(base_dir=self.base_dir)
        self.coastal_engine = CoastalBoundaryEngine()
        self.l3_pipeline = Layer3Pipeline(base_dir=self.base_dir)
        self.conveyance_engine = StreetConveyanceEngine()
        self.pump_optimizer = MunicipalPumpOptimizer()
        self.cap_emitter = CAPAlertEmitter()

    def run_full_twin(
        self,
        scenario: str = "monsoon",
        mode: str = "auto",
        clogging_factor: float = 0.35,
        tidal_surge_m: float = 0.85,
        cloudburst_intensity_mm_hr: Optional[float] = None,
        storm_intensity_mm_hr: Optional[float] = None
    ) -> MasterTwinResult:
        """
        Executes end-to-end multi-layer pipeline:
          Layer 0 -> Layer 1 -> Layer 2 -> Layer 3 -> Layer 4
        """
        t_global_start = time.perf_counter()

        if storm_intensity_mm_hr is not None:
            base_rain = storm_intensity_mm_hr
        elif cloudburst_intensity_mm_hr is not None:
            base_rain = cloudburst_intensity_mm_hr
        elif scenario.lower() == "2015_flood":
            base_rain = 85.0
        elif scenario.lower() in ("michaung", "cloudburst"):
            base_rain = 65.0
        else:
            base_rain = 45.0

        # ----------------------------------------------------
        # Step 1: Layer 0 - Multi-Sensor Radar & CML Mesh
        # ----------------------------------------------------
        t0 = time.perf_counter()
        l0_res = self.l0_pipeline.run(scenario=scenario, mode=mode)
        cml_telemetry = self.cml_retriever.get_mesh_telemetry(
            storm_scenario=scenario,
            storm_multiplier=(base_rain / 65.0)
        )
        t_l0 = (time.perf_counter() - t0) * 1000.0

        # ----------------------------------------------------
        # Step 2: Layer 1 - DEM Runoff Generation
        # ----------------------------------------------------
        t0 = time.perf_counter()
        l1_roads = self.l3_pipeline.graph.nodes_df.copy()
        amc_condition = "AMC_III" if (base_rain >= 60.0 or scenario in ("michaung", "2015_flood")) else "AMC_II"
        l1_res = self.runoff_gen.compute_runoff(
            roads_df=l1_roads,
            rainfall_intensity=base_rain,
            amc=amc_condition,
            scenario=scenario
        )
        t_l1 = (time.perf_counter() - t0) * 1000.0

        # ----------------------------------------------------
        # Step 3: Layer 2 - 1D Subsurface Conduit Hydraulics & Coastal Tide
        # ----------------------------------------------------
        t0 = time.perf_counter()
        l2_res = self.l2_pipeline.run(
            storm_intensity_mm_hr=base_rain,
            clogging_modifier=clogging_factor / 0.35,
            layer1_runoff=l1_res
        )
        coastal_status = self.coastal_engine.evaluate_outfall_states(
            cyclonic_surge_m=tidal_surge_m,
            storm_scenario=scenario
        )
        t_l2 = (time.perf_counter() - t0) * 1000.0

        # ----------------------------------------------------
        # Step 4: Layer 3 - PI-GNN Surrogate & Street Conveyance
        # ----------------------------------------------------
        t0 = time.perf_counter()
        l3_res = self.l3_pipeline.run(
            scenario=scenario,
            clogging_factor=clogging_factor,
            storm_scale=1.0 if cloudburst_intensity_mm_hr is None else (cloudburst_intensity_mm_hr / 65.0),
            layer1_runoff=l1_res,
            layer2_backflow=l2_res
        )

        # Apply street-as-canal flow velocity and v × d hazard evaluation
        conveyance_res = self.conveyance_engine.compute_street_flow(
            roads_df=l3_res.dataframe,
            horizon_min=60
        )
        t_l3 = (time.perf_counter() - t0) * 1000.0

        # ----------------------------------------------------
        # Step 5: Layer 4 - Tactical Pump Optimization & Alerts
        # ----------------------------------------------------
        t0 = time.perf_counter()
        pumps = self.pump_optimizer.optimize_deployments(
            roads_df=conveyance_res.dataframe,
            horizon_min=60,
            max_recommendations=5
        )
        t_l4 = (time.perf_counter() - t0) * 1000.0

        total_runtime = (time.perf_counter() - t_global_start) * 1000.0

        diagnostics = {
            "total_runtime_ms": round(total_runtime, 2),
            "layer0_ms": round(t_l0, 2),
            "layer1_ms": round(t_l1, 2),
            "layer2_ms": round(t_l2, 2),
            "layer3_ms": round(t_l3, 2),
            "layer4_ms": round(t_l4, 2),
            "subsecond_benchmark_satisfied": total_runtime < 1000.0,
            "scenario": scenario,
            "clogging_factor": clogging_factor,
            "tidal_surge_m": tidal_surge_m,
            "base_rainfall_mm_hr": base_rain,
        }

        return MasterTwinResult(
            dataframe=conveyance_res.dataframe,
            horizons_depths=l3_res.depth_matrices,
            diagnostics=diagnostics,
            pump_recommendations=pumps,
            coastal_outfall_status=coastal_status,
            cml_telemetry=cml_telemetry,
            street_conveyance_summary=conveyance_res.summary_metrics
        )


def main():
    parser = argparse.ArgumentParser(description="KAIROS: Master 5-Layer Twin Orchestrator CLI")
    parser.add_argument("--scenario", type=str, default="monsoon", choices=["monsoon", "cloudburst", "michaung", "2015_flood"])
    parser.add_argument("--clogging", type=float, default=0.35, help="Solid waste clogging factor (0.0 to 0.85)")
    parser.add_argument("--tide-surge", type=float, default=0.85, help="Coastal storm surge in meters")
    parser.add_argument("--cloudburst", type=float, default=None, help="Optional cloudburst intensity (mm/hr)")
    parser.add_argument("--storm-intensity", type=float, default=None, help="Arbitrary storm rainfall intensity (mm/hr)")

    args = parser.parse_args()

    print("=" * 75)
    print("      KAIROS MASTER 5-LAYER DIGITAL TWIN ORCHESTRATOR")
    print(f"      Scenario: {args.scenario.upper()} | Clogging: {args.clogging} | Surge: {args.tide_surge}m")
    print("=" * 75)

    coupler = MasterTwinCoupler()
    res = coupler.run_full_twin(
        scenario=args.scenario,
        clogging_factor=args.clogging,
        tidal_surge_m=args.tide_surge,
        cloudburst_intensity_mm_hr=args.cloudburst,
        storm_intensity_mm_hr=args.storm_intensity
    )

    kpi = res.to_kpi_summary()
    print("\n[EXECUTION SUMMARY]")
    print(f"  ✓ Total Pipeline Runtime:         {res.diagnostics['total_runtime_ms']} ms")
    print(f"  ✓ Active Road Corridors:          {kpi['active_road_segments']:,} segments")
    print(f"  ✓ Peak Inundation Depth (T+60m):  {kpi['peak_depth_t60_cm']} cm")
    print(f"  ✓ Inundated Corridors (>=10cm):   {kpi['inundated_roads_count']} corridors")
    print(f"  ✓ Critical Impassable (>=30cm):   {kpi['critical_impassable_roads_count']} corridors")
    print(f"  ✓ Coastal Outfalls Locked:        {kpi['coastal_outfalls_locked']} outfalls")
    print(f"  ✓ Mobile Pumps Dispatched:        {kpi['recommended_pumps_count']} high-capacity units")
    print(f"  ✓ Street-as-Canal Fast Channels:  {res.street_conveyance_summary.get('active_street_channels_count', 0)} corridors")

    print("\n" + "=" * 75)
    print("          TOP MUNICIPAL DE-WATERING PUMP DISPATCH SITES")
    print("=" * 75)
    for p in res.pump_recommendations:
        print(f"  [Priority {p['priority_rank']}] {p['road_name']} ({p['zone_name']})")
        print(f"      Depth: {p['predicted_depth_cm']} cm | Unit: {p['recommended_pump_type']}")
        print(f"      Required Capacity: {p['required_capacity_m3_hr']} m³/hr | Action: {p['action_directive']}")


if __name__ == "__main__":
    main()
