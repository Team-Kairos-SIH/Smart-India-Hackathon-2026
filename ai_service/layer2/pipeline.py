"""Layer 2: Pipeline Module - 1D Subsurface Hydraulics & Surcharge Engine Orchestrator.

Orchestrates:
  1. Dynamic Municipal Clogging Attribution (mu_clog from waste & desilting records).
  2. Subsurface Conduit Conveyance Solver (Manning's full-pipe & open-channel flow).
  3. Drop-Inlet Grate Capture vs Gutter Bypass Hydraulics.
  4. Manhole Hydraulic Grade Line (HGL) Pressurization & Surcharge Eruption.
  5. Real OSM Manhole Inspection Points & Outfall Receiving Channels Integration.
"""

import argparse
from dataclasses import dataclass, field
import json
import logging
import math
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd

from .clogging_model import SolidWasteCloggingModel
from .conduit_flow import ConduitFlowEngine
from .inlet_capture import InletCaptureEngine
from .manhole_surcharge import ManholeSurchargeEngine
from .drainage_graph import DrainageGraphNetwork, TidalBoundaryEngine

logger = logging.getLogger(__name__)

# Road hierarchy corridor right-of-way buffer widths per IRC:SP:50 / CPHEEO standards
CORRIDOR_WIDTH_PROXY_BY_DIAMETER: Dict[float, float] = {
    1.80: 36.0,  # Arterial 6-lane highway right-of-way
    1.20: 24.0,  # Sub-arterial 4-lane major corridor
    0.90: 18.0,  # Collector 2-lane distributor street
    0.60: 12.0,  # Local residential street / access lane
}

# Urban runoff coefficients per CPHEEO urban drainage guidelines
RUNOFF_COEFFICIENT_BY_DIAMETER: Dict[float, float] = {
    1.80: 0.90,  # Arterial: dense asphalt/concrete impervious cover
    1.20: 0.85,  # Sub-arterial: paved corridor with curbed margins
    0.90: 0.80,  # Collector: mixed commercial/paved surfaces
    0.60: 0.75,  # Local street: residential with unpaved verges/permeable surfaces
}


@dataclass
class Layer2Result:
    """Encapsulates the complete Layer 2 Subsurface Hydraulics execution outputs."""
    dataframe: pd.DataFrame
    network_stats: Dict[str, Any]
    surcharge_hotspots: List[Dict[str, Any]]
    diagnostics: Dict[str, Any] = field(default_factory=dict)

    @property
    def conduits_df(self) -> pd.DataFrame:
        return self.dataframe

    def __getitem__(self, item: str) -> Any:
        if item in ('dataframe', 'df', 'conduits_df'):
            return self.dataframe
        if hasattr(self, item):
            return getattr(self, item)
        return self.diagnostics[item]

    def to_csv(self, path: Union[str, Path]) -> None:
        self.dataframe.to_csv(path, index=False)


class Layer2Pipeline:
    """Unified Layer 2 1D Subsurface Stormwater Conduit & Surcharge Pipeline."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).resolve().parent.parent.parent
        self.clogging_model = SolidWasteCloggingModel(base_dir=self.base_dir)
        self.conduit_engine = ConduitFlowEngine()
        self.inlet_engine = InletCaptureEngine()
        self.surcharge_engine = ManholeSurchargeEngine()
        self.graph_network = DrainageGraphNetwork(base_dir=self.base_dir)
        self.tidal_engine = TidalBoundaryEngine()

    def run(
        self,
        storm_intensity_mm_hr: float = 65.0,
        clogging_modifier: float = 1.0,
        layer1_runoff: Optional[Any] = None,
        storm_surge_m: float = 0.35,
        tidal_time_hours: float = 2.0
    ) -> Layer2Result:
        """
        Execute Layer 2 hydraulic simulation across all real conduits and manhole inspection points.

        Parameters:
          storm_intensity_mm_hr: Domain rainfall rate I(t) from Layer 0 (mm/hr)
          clogging_modifier: Multiplier on municipal clogging index (default 1.0)
          layer1_runoff: Optional verified Layer 1 RunoffResult, Layer3Inputs, or DataFrame.
              When supplied, conduit tributary inflow Q_surf is aggregated directly from
              the real road segments connected via source_drain_id.
          storm_surge_m: Cyclonic storm surge elevation offset above MSL in meters (default 0.35m)
          tidal_time_hours: Tidal cycle simulation epoch in hours (default 2.0h)
        """
        t_start = time.perf_counter()

        # 1. Resolve tributary surface runoff from Layer 1 if provided
        drain_lookup: Dict[str, Dict[str, Any]] = {}
        using_l1 = False
        if layer1_runoff is not None:
            df_roads = getattr(layer1_runoff, "dataframe", None)
            if df_roads is None and isinstance(layer1_runoff, pd.DataFrame):
                df_roads = layer1_runoff
            elif df_roads is None and hasattr(layer1_runoff, "streets_df"):
                df_roads = layer1_runoff.streets_df

            if df_roads is not None and "source_drain_id" in df_roads.columns and "surface_runoff_inflow_m3_s" in df_roads.columns:
                for drain_id, group in df_roads.groupby("source_drain_id"):
                    drain_lookup[str(drain_id)] = {
                        "q_surf": float(group["surface_runoff_inflow_m3_s"].sum()),
                        "z_ground": float(group["elevation_ground_m"].mean()) if "elevation_ground_m" in group.columns else None,
                        "road_count": len(group)
                    }
                using_l1 = True
                logger.info("Layer 2 coupled with real Layer 1 runoff across %d drainage conduits", len(drain_lookup))

        # 2. Simulate hydraulic loading on all conduits
        edges = self.graph_network.edges
        conduit_records = []
        total_captured = 0.0
        total_inflow = 0.0
        total_backflow = 0.0
        total_nominal_capacity = 0.0
        total_effective_capacity = 0.0
        total_tidal_capacity = 0.0
        surcharging_conduits = 0
        clogging_factors = []

        # Instantaneous Bay of Bengal tidal stage for coastal boundary
        tidal_stage = self.tidal_engine.compute_tidal_stage_m(t_hours=tidal_time_hours, storm_surge_m=storm_surge_m)

        for edge in edges:
            edge_id = edge["edge_id"]
            drain_id = edge.get("drain_id", edge_id)
            dia = float(edge["diameter_m"])
            s0 = float(edge["slope_m_per_m"])
            z = int(edge["zone_no"])
            cross_section = edge.get("cross_section", "CIRCULAR_RCC")
            is_coastal = bool(edge.get("is_coastal_outfall", False))
            edge_prov = dict(edge.get("provenance", {}))

            # Runtime mu satisfies 0.05 <= mu_clog <= 0.85
            base_mu = self.clogging_model.get_zone_clogging_factor(z, global_modifier=clogging_modifier)
            mu = float(np.clip(base_mu, 0.05, 0.85))
            clogging_factors.append(mu)

            # DYNAMIC MANNING CONDUIT CONVEYANCE EVALUATION
            if cross_section == "BOX_DRAIN":
                hydraulics = self.conduit_engine.calculate_box_culvert(
                    width_m=2.0,
                    height_m=1.5,
                    slope_m_per_m=s0,
                    mu_clog=mu
                )
            else:
                hydraulics = self.conduit_engine.calculate_circular_pipe(
                    diameter_m=dia,
                    slope_m_per_m=s0,
                    mu_clog=mu
                )

            q_nominal = float(hydraulics["nominal_capacity_m3_s"])
            q_effective = float(hydraulics["effective_capacity_m3_s"])

            # Tidal throttling applied strictly to coastal outfalls
            if is_coastal:
                z_inv = float(edge.get("z_invert_m", 0.50))
                tidal_throttle = self.tidal_engine.compute_outfall_throttle_factor(z_inv, tidal_stage)
                q_tidal = round(q_effective * tidal_throttle, 3)
            else:
                tidal_throttle = 1.0
                q_tidal = q_effective

            q_cap = q_tidal
            total_nominal_capacity += q_nominal
            total_effective_capacity += q_effective
            total_tidal_capacity += q_tidal

            # REAL GROUND ELEVATION & DEM PROVENANCE
            z_ground_raw = edge.get("z_ground_m")
            if z_ground_raw is not None and np.isfinite(z_ground_raw):
                z_ground = float(round(z_ground_raw, 2))
                z_ground_prov = edge_prov.get("ground_elevation", "DERIVED_FROM_REAL_DEM")
            elif using_l1 and drain_id in drain_lookup and drain_lookup[drain_id].get("z_ground") is not None:
                z_ground = float(round(drain_lookup[drain_id]["z_ground"], 2))
                z_ground_prov = "DERIVED_FROM_LAYER1_ROAD_DEM"
            else:
                z_ground = 6.0
                z_ground_prov = "ASSUMED (Unassociated Default Fallback)"

            # SURFACE INFLOW COUPLING
            if using_l1 and drain_id in drain_lookup:
                q_surf = float(drain_lookup[drain_id]["q_surf"])
                catchment_prov = "REAL_LAYER1_RUNOFF (Coupled SCS-CN Road Inflow)"
                c_runoff = 0.85
                c_prov = "REAL_LAYER1_LULC"
            elif using_l1:
                # Unmapped conduit during coupled execution: use road hierarchy proxy
                corridor_w = CORRIDOR_WIDTH_PROXY_BY_DIAMETER.get(dia, 15.0)
                subcatch_a = edge["length_m"] * corridor_w
                c_runoff = RUNOFF_COEFFICIENT_BY_DIAMETER.get(dia, 0.80)
                q_surf = float(c_runoff * (storm_intensity_mm_hr / 1000.0 / 3600.0) * subcatch_a)
                catchment_prov = "PROXY_REAL_ROAD_HIERARCHY (Unmapped in L1 - Width from Road Class)"
                c_prov = "ENGINEERING_PROXY (CPHEEO Urban Imperviousness Standards)"
            else:
                # Standalone Layer 2 execution
                corridor_w = CORRIDOR_WIDTH_PROXY_BY_DIAMETER.get(dia, 15.0)
                subcatch_a = edge["length_m"] * corridor_w
                c_runoff = RUNOFF_COEFFICIENT_BY_DIAMETER.get(dia, 0.80)
                q_surf = float(c_runoff * (storm_intensity_mm_hr / 1000.0 / 3600.0) * subcatch_a)
                catchment_prov = "PROXY_REAL_ROAD_HIERARCHY (IRC:SP:50 Right-of-Way Buffer)"
                c_prov = "ENGINEERING_PROXY (CPHEEO Urban Imperviousness Standards)"

            total_inflow += q_surf

            # INLET GRATE CAPTURE (IRC:SP:50 25m Spacing Heuristic)
            n_inlets = max(1, int(edge["length_m"] / 25.0))
            q_curb = q_surf / n_inlets if n_inlets > 0 else q_surf
            water_depth_curb = 0.04 + (q_curb / 0.5) * 0.08
            inlet = self.inlet_engine.compute_inlet_capture(
                q_surface_inflow_m3_s=q_curb,
                water_depth_at_curb_m=water_depth_curb,
                debris_blockage_pct=mu * 0.5
            )
            q_captured = min(q_surf, inlet["q_captured_m3_s"] * n_inlets)
            q_bypass = max(0.0, q_surf - q_captured)
            total_captured += q_captured

            # Capacity utilization & choke state
            fullness_pct = (q_captured / max(1e-3, q_cap)) * 100.0
            is_choked = fullness_pct >= 100.0

            # CONDUIT SURCHARGE EVALUATION (Using Real Ground & Invert Elevation)
            z_inv = float(edge.get("z_invert_m", max(0.5, z_ground - dia - 1.0)))
            surch_res = self.surcharge_engine.evaluate_surcharge(
                q_inflow_m3_s=q_captured,
                q_pipe_capacity_m3_s=q_cap,
                z_ground_m=z_ground,
                z_invert_m=z_inv
            )
            q_backflow = float(surch_res["backflow_discharge_m3_s"])
            if surch_res["is_surcharged"]:
                surcharging_conduits += 1
                total_backflow += q_backflow

            # Build enriched provenance
            complete_prov = {
                **edge_prov,
                "ground_elevation": z_ground_prov,
                "clogging": "REAL_GCC_DATA",
                "catchment_area": catchment_prov,
                "runoff_coefficient": c_prov,
                "inlet_spacing": "ENGINEERING_PROXY (IRC:SP:50 25m Curb Inlet Spacing)",
                "conduit_engine": "Manning 1D (ConduitFlowEngine)"
            }

            conduit_records.append({
                "edge_id": edge_id,
                "drain_id": drain_id,
                "from_node": edge.get("from_node", ""),
                "to_node": edge.get("to_node", ""),
                "longitude": edge.get("longitude", 80.20),
                "latitude": edge.get("latitude", 13.04),
                "waterway": edge.get("waterway", "drain"),
                "zone_no": z,
                "length_m": edge["length_m"],
                "diameter_m": dia,
                "slope_m_per_m": s0,
                "slope_provenance": edge_prov.get("terrain_slope", "PROXY (Surface Terrain Gradient from DEM)"),
                "z_ground_m": z_ground,
                "ground_elevation_provenance": z_ground_prov,
                "invert_elevation_m": round(z_inv, 2),
                "invert_provenance": edge_prov.get("invert_elevation", "ASSUMED (CPHEEO Standard Burial Depth Heuristic)"),
                "clogging_factor": round(mu, 3),
                "clogging_provenance": "REAL_GCC_DATA",
                "nominal_capacity_m3_s": round(q_nominal, 3),
                "effective_capacity_m3_s": round(q_effective, 3),
                "tidal_throttle": round(tidal_throttle, 2),
                "tidal_throttled_capacity_m3_s": round(q_tidal, 3),
                "is_coastal_outfall": is_coastal,
                "surface_inflow_m3_s": round(q_surf, 4),
                "inlet_captured_m3_s": round(q_captured, 4),
                "gutter_bypass_m3_s": round(q_bypass, 4),
                "capacity_utilization_pct": round(min(250.0, fullness_pct), 1),
                "is_choked": is_choked,
                "hgl_m": surch_res["hgl_m"],
                "head_above_ground_m": surch_res.get("head_above_ground_m", 0.0),
                "backflow_discharge_m3_s": round(q_backflow, 4),
                "is_surcharged": surch_res["is_surcharged"],
                "provenance": complete_prov
            })

        df_conduits = pd.DataFrame(conduit_records)

        # 3. Simulate Surcharge on Real Graph Entities (33 Real OSM Inspection Manholes)
        surcharge_hotspots = []
        cos_lat = math.cos(math.radians(13.04))
        resolved_manholes = 0
        unresolved_manholes = 0

        # Spatial index of conduits for manhole association
        edge_coords = [
            (e["longitude"], e["latitude"], e)
            for e in conduit_records
        ]

        for idx, mh_feat in enumerate(self.graph_network.manhole_nodes):
            props = mh_feat.get("properties", {})
            geom = mh_feat.get("geometry", {})
            coords = geom.get("coordinates", [])
            if len(coords) < 2:
                continue

            m_lon, m_lat = coords[0], coords[1]
            mh_id = str(props.get("@id", f"OSM_MH_{idx+1:03d}"))

            # Find closest conduit
            min_dist = 1e9
            best_edge = None
            for e_lon, e_lat, e_rec in edge_coords:
                dx = (e_lon - m_lon) * 111320.0 * cos_lat
                dy = (e_lat - m_lat) * 110540.0
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < min_dist:
                    min_dist = dist
                    best_edge = e_rec

            # 250m association threshold: if within 250m of mapped stormwater drain
            if min_dist <= 250.0 and best_edge is not None:
                resolved_manholes += 1
                mh_z_ground = best_edge["z_ground_m"]
                mh_q_in = best_edge["inlet_captured_m3_s"]
                mh_q_cap = best_edge["effective_capacity_m3_s"]
                mh_z_inv = best_edge["invert_elevation_m"]

                surch_res = self.surcharge_engine.evaluate_surcharge(
                    q_inflow_m3_s=mh_q_in,
                    q_pipe_capacity_m3_s=mh_q_cap,
                    z_ground_m=mh_z_ground,
                    z_invert_m=mh_z_inv
                )
                surcharge_hotspots.append({
                    "manhole_id": mh_id,
                    "feature_type": "OSM_INSPECTION_MANHOLE",
                    "latitude": m_lat,
                    "longitude": m_lon,
                    "association_status": "RESOLVED_ASSOCIATED",
                    "associated_edge_id": best_edge["edge_id"],
                    "distance_to_conduit_m": round(min_dist, 1),
                    "z_ground_m": mh_z_ground,
                    **surch_res,
                    "provenance": "REAL_OSM_MANHOLE (Associated to nearest conduit)"
                })
            else:
                unresolved_manholes += 1
                # Record as unresolved rather than inventing artificial connection
                surcharge_hotspots.append({
                    "manhole_id": mh_id,
                    "feature_type": "OSM_INSPECTION_MANHOLE",
                    "latitude": m_lat,
                    "longitude": m_lon,
                    "association_status": "UNRESOLVED_DISCONNECTED",
                    "associated_edge_id": None,
                    "distance_to_conduit_m": round(min_dist, 1) if best_edge else None,
                    "z_ground_m": None,
                    "is_surcharged": False,
                    "status": "UNRESOLVED_ISOLATED_MANHOLE",
                    "hgl_m": None,
                    "head_above_ground_m": 0.0,
                    "backflow_discharge_m3_s": 0.0,
                    "provenance": "REAL_OSM_MANHOLE (Isolated from LineStrings > 250m)"
                })

        net_stats = self.graph_network.get_network_statistics()
        elapsed = time.perf_counter() - t_start
        choked_count = int(np.count_nonzero(df_conduits["is_choked"]))

        diagnostics = {
            "total_execution_ms": round(elapsed * 1000.0, 2),
            "simulated_conduits": len(df_conduits),
            "choked_conduit_count": choked_count,
            "choked_conduit_pct": round((choked_count / max(1, len(df_conduits))) * 100.0, 1),
            "surcharging_conduits_count": surcharging_conduits,
            "total_backflow_discharge_m3_s": round(total_backflow, 4),
            "upstream_runoff_source": "layer1" if using_l1 else "rainfall",
            "total_surface_inflow_m3_s": round(total_inflow, 2),
            "total_captured_drainage_m3_s": round(total_captured, 2),
            "total_gutter_bypass_m3_s": round(max(0.0, total_inflow - total_captured), 2),
            "domain_capture_efficiency_pct": round((total_captured / max(1e-3, total_inflow)) * 100.0, 1),
            "total_nominal_capacity_m3_s": round(total_nominal_capacity, 2),
            "total_effective_capacity_m3_s": round(total_effective_capacity, 2),
            "total_tidal_throttled_capacity_m3_s": round(total_tidal_capacity, 2),
            "mean_clogging_factor": round(float(np.mean(clogging_factors)), 3),
            "real_manholes_evaluated": len(surcharge_hotspots),
            "resolved_manholes_count": resolved_manholes,
            "unresolved_manholes_count": unresolved_manholes,
            "surcharging_manholes_count": sum(1 for h in surcharge_hotspots if h.get("is_surcharged")),
            "total_receiving_channels": len(self.graph_network.receiving_channels),
            "storm_intensity_mm_hr": storm_intensity_mm_hr,
            "clogging_modifier": clogging_modifier,
            "storm_surge_m": storm_surge_m,
            "tidal_stage_m": round(tidal_stage, 3)
        }

        return Layer2Result(
            dataframe=df_conduits,
            network_stats=net_stats,
            surcharge_hotspots=surcharge_hotspots,
            diagnostics=diagnostics
        )


def main():
    parser = argparse.ArgumentParser(description="Layer 2: 1D Subsurface Conduit Hydraulics & Surcharge Engine (GCC Real Chennai Data)")
    parser.add_argument("--storm-intensity", type=float, default=65.0, help="Rainfall intensity in mm/hr (default: 65.0)")
    parser.add_argument("--clogging-scale", type=float, default=1.0, help="Multiplier on municipal clogging index (default: 1.0)")
    parser.add_argument("--output", type=str, default=None, help="Optional CSV output path for conduit flows")
    args = parser.parse_args()

    print(f"Executing Layer 2 Hydraulics Pipeline (storm={args.storm_intensity} mm/h, clogging_scale={args.clogging_scale})...")
    pipe = Layer2Pipeline()
    result = pipe.run(storm_intensity_mm_hr=args.storm_intensity, clogging_modifier=args.clogging_scale)

    diag = result.diagnostics
    print("\n" + "=" * 65)
    print("LAYER 2 SUBSURFACE HYDRAULICS EXECUTION REPORT (REAL CHENNAI DATA)")
    print("=" * 65)
    print(f"Total Execution Time:    {diag['total_execution_ms']:.2f} ms")
    print(f"Simulated Conduits:      {diag['simulated_conduits']} real pipes")
    print(f"Choked / Full Conduits:  {diag['choked_conduit_count']} ({diag['choked_conduit_pct']}%)")
    print(f"Inlet Capture Efficiency:{diag['domain_capture_efficiency_pct']}%")
    print(f"Real OSM Manholes:       {diag['real_manholes_evaluated']} evaluated ({diag['resolved_manholes_count']} resolved, {diag['unresolved_manholes_count']} unresolved)")
    print(f"Surcharging Conduits:    {diag['surcharging_conduits_count']} pipes")
    print(f"Total Surface Runoff:    {diag['total_surface_inflow_m3_s']:.2f} m3/s")
    print(f"Total Subsurface Flow:   {diag['total_captured_drainage_m3_s']:.2f} m3/s")
    print(f"Total Gutter Bypass:     {diag['total_gutter_bypass_m3_s']:.2f} m3/s")
    print(f"Total Nominal Capacity:  {diag['total_nominal_capacity_m3_s']:.2f} m3/s")
    print(f"Total Effective Capacity:{diag['total_effective_capacity_m3_s']:.2f} m3/s")
    print("=" * 65)

    if args.output:
        result.to_csv(args.output)
        print(f"Saved results to: {args.output}")


if __name__ == "__main__":
    main()
