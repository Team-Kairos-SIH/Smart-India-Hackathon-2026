"""Layer 2: Drainage Graph Module - 1D Directed Drainage Network Topology.

Constructs directed multigraph G = (V, E) of Chennai's subsurface stormwater drainage system:
  - Nodes V: Catch-pits, drop-inlets, manholes, canal outfalls
  - Edges E: Circular RCC conduits, rectangular box drains, arterial canals
  - Attributes: Length L, Diameter/Span D, Slope S_0, Manning Roughness n_eff, Clogging mu_clog
"""

import os
import json
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import pandas as pd
import numpy as np

from .clogging_model import find_dataset_path, SolidWasteCloggingModel
from .conduit_flow import ConduitFlowEngine

logger = logging.getLogger(__name__)

# Official CPHEEO Stormwater Drainage & IRC:SP:50 Hierarchy Norms
CPHEEO_PIPE_HIERARCHY = {
    "arterial": 1.80,     # 1800mm primary trunk outfall / canal feeder
    "sub_arterial": 1.20, # 1200mm secondary trunk storm drain
    "collector": 0.90,    # 900mm neighborhood collector
    "local": 0.60         # 600mm tertiary street branch drain
}

# Live field override registry for CMWSSB/GCC municipal ward engineers
CMWSSB_FIELD_OVERRIDE_REGISTRY: Dict[str, float] = {}


class TidalBoundaryEngine:
    """
    Bay of Bengal astronomical semi-diurnal tide (M2 + S2 harmonics)
    with cyclonic storm surge elevation offset.
    
    Models tailwater backpressure for coastal outfalls:
      - Adyar River Estuary
      - Cooum River Mouth (Napier Bridge)
      - Buckingham Canal
      - Ennore Creek
    """
    def __init__(self, datum_msl_m: float = 0.0):
        self.datum_msl_m = datum_msl_m
        # Harmonic constants for Chennai Port (MoES / Survey of India)
        self.amp_m2 = 0.42   # Principal lunar semi-diurnal (m)
        self.amp_s2 = 0.18   # Principal solar semi-diurnal (m)
        self.period_m2_hr = 12.4206
        self.period_s2_hr = 12.0000

    def compute_tidal_stage_m(self, t_hours: float, storm_surge_m: float = 0.0) -> float:
        """Calculates instantaneous tidal stage (meters MSL) at coastal outfalls."""
        w_m2 = 2.0 * np.pi / self.period_m2_hr
        w_s2 = 2.0 * np.pi / self.period_s2_hr
        astronomical_head = (
            self.amp_m2 * np.cos(w_m2 * t_hours) +
            self.amp_s2 * np.cos(w_s2 * t_hours)
        )
        return float(self.datum_msl_m + astronomical_head + storm_surge_m)

    def compute_outfall_throttle_factor(self, invert_elev_m: float, tidal_stage_m: float) -> float:
        """
        Computes hydraulic backwater throttling coefficient (0.1 to 1.0)
        when coastal tide submerges gravity outfall inverts.
        """
        if tidal_stage_m <= invert_elev_m:
            return 1.0  # Free gravity outfall discharge
        
        # Submerged orifice / backwater head loss
        submergence_m = tidal_stage_m - invert_elev_m
        head_throttle = max(0.15, 1.0 - np.clip(submergence_m / 1.5, 0.0, 0.85))
        return float(head_throttle)


class DrainageGraphNetwork:
    """
    Manages 1D topological multigraph representation of real Chennai stormwater conduits
    with CPHEEO standards, DEM terrain gradients, real GCC civic clogging, and tidal boundaries.
    """

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).resolve().parent.parent.parent
        self.clogging_model = SolidWasteCloggingModel(base_dir=self.base_dir)
        self.conduit_engine = ConduitFlowEngine()
        self.tidal_engine = TidalBoundaryEngine()
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []
        self.receiving_channels: List[Dict[str, Any]] = []
        self.manhole_nodes: List[Dict[str, Any]] = []
        self._build_network()

    @staticmethod
    def register_field_override(edge_id: str, diameter_m: float):
        """Allows municipal engineers to set calibrated pipe dimensions."""
        CMWSSB_FIELD_OVERRIDE_REGISTRY[edge_id] = float(diameter_m)

    def _locate_drainage_geojson(self) -> Path:
        """Locates the real drainage network GeoJSON using configurable paths."""
        candidates = []
        env_root = os.environ.get("LAYER2_DATA_ROOT")
        if env_root:
            env_path = Path(env_root)
            candidates.append(env_path / "oms_network" / "drainage network.geojson")
            candidates.append(env_path / "drainage network.geojson")
            candidates.append(env_path / "drainage_network.geojson")

        candidates.append(self.base_dir.parent / "drainage_data" / "oms_network" / "drainage network.geojson")
        candidates.append(self.base_dir.parent / "SIH_Real_Data" / "drainage_data" / "oms_network" / "drainage network.geojson")
        candidates.append(self.base_dir / "ai_service" / "data" / "network" / "drainage_network.geojson")

        try:
            candidates.append(find_dataset_path(self.base_dir, "drainage network.geojson"))
        except Exception:
            pass

        try:
            candidates.append(find_dataset_path(self.base_dir, "drainage_network.geojson"))
        except Exception:
            pass

        for p in candidates:
            if p and p.is_file():
                return p.resolve()

        raise FileNotFoundError(
            "REAL DRAINAGE NETWORK UNAVAILABLE: Required real dataset missing. "
            f"Searched candidate locations: {[str(c) for c in candidates[:5]]}. "
            "Please configure the LAYER2_DATA_ROOT environment variable. "
            "Silent synthetic fallback is prohibited on branch feature/layer2-real-data."
        )

    def _infer_diameter_from_road(self, hw_class: str) -> Tuple[float, str]:
        """Maps road classification to CPHEEO / IRC:SP:50 diameter proxy with explicit provenance."""
        hw = str(hw_class).lower()
        if hw in ["motorway", "trunk", "primary", "primary_link"]:
            return CPHEEO_PIPE_HIERARCHY["arterial"], "PROXY (CPHEEO Arterial Standard)"
        elif hw in ["secondary", "secondary_link"]:
            return CPHEEO_PIPE_HIERARCHY["sub_arterial"], "PROXY (CPHEEO Sub-Arterial Standard)"
        elif hw in ["tertiary", "tertiary_link"]:
            return CPHEEO_PIPE_HIERARCHY["collector"], "PROXY (CPHEEO Collector Standard)"
        elif hw in ["residential", "living_street", "service", "unclassified"]:
            return CPHEEO_PIPE_HIERARCHY["local"], "PROXY (CPHEEO Local Street Standard)"
        return CPHEEO_PIPE_HIERARCHY["local"], "PROXY_DEFAULT (Unassociated Drain - Local Branch Baseline)"

    def _build_network(self):
        """Construct genuine multigraph from real drainage network GeoJSON and DEM attributes."""
        drain_path = self._locate_drainage_geojson()
        logger.info("Building real drainage graph from: %s", drain_path)

        with open(drain_path, "r", encoding="utf-8") as f:
            drain_data = json.load(f)

        features = drain_data.get("features", [])

        # Load road-DEM association table if available
        drain_road_lookup: Dict[str, Dict[str, Any]] = {}
        road_coords = np.empty((0, 2))
        road_elevs = np.empty(0)
        road_slopes = np.empty(0)
        road_zones = np.empty(0, dtype=int)
        road_hw_classes: List[str] = []

        try:
            roads_path = find_dataset_path(self.base_dir, "chennai_roads_with_dem_attributes.csv")
            df_roads = pd.read_csv(roads_path)

            try:
                master_path = find_dataset_path(self.base_dir, "Datasets_master.csv")
                df_master = pd.read_csv(master_path, encoding="utf-16")
                df_roads = pd.merge(df_roads, df_master[["segment_id", "zone_no"]], on="segment_id", how="left")
            except Exception:
                pass

            if "source_drain_id" in df_roads.columns:
                for drain_id, grp in df_roads.groupby("source_drain_id"):
                    drain_road_lookup[str(drain_id)] = {
                        "count": len(grp),
                        "mean_elev": float(grp["elevation_ground_m"].mean()) if "elevation_ground_m" in grp.columns else 6.0,
                        "mean_slope": float(grp["terrain_slope_m_per_m"].mean()) if "terrain_slope_m_per_m" in grp.columns else 0.002,
                        "highway_class": str(grp["source_highway_class"].mode().iloc[0]) if "source_highway_class" in grp.columns and not grp["source_highway_class"].empty else "residential",
                        "zone_no": int(grp["zone_no"].mode().iloc[0]) if "zone_no" in grp.columns and grp["zone_no"].notna().any() else 8
                    }

            if not df_roads.empty and "longitude" in df_roads.columns and "latitude" in df_roads.columns:
                road_coords = df_roads[["longitude", "latitude"]].to_numpy()
                road_elevs = df_roads["elevation_ground_m"].to_numpy() if "elevation_ground_m" in df_roads.columns else np.full(len(df_roads), 6.0)
                road_slopes = df_roads["terrain_slope_m_per_m"].to_numpy() if "terrain_slope_m_per_m" in df_roads.columns else np.full(len(df_roads), 0.002)
                road_zones = df_roads["zone_no"].fillna(8).astype(int).to_numpy() if "zone_no" in df_roads.columns else np.full(len(df_roads), 8, dtype=int)
                road_hw_classes = df_roads["source_highway_class"].fillna("residential").tolist() if "source_highway_class" in df_roads.columns else ["residential"] * len(df_roads)
        except Exception as e:
            logger.warning("Could not load road-DEM association table: %s", e)

        # Categorize GeoJSON features
        st_conduits = []
        manhole_points_coords = set()

        for feat in features:
            props = feat.get("properties", {})
            geom = feat.get("geometry", {})
            gtype = geom.get("type")
            ww = str(props.get("waterway", "")).lower()

            if gtype == "Point" and (props.get("man_made") == "manhole" or props.get("manhole") in ["drain", "sewer"]):
                coords = geom.get("coordinates", [])
                if len(coords) >= 2:
                    pt_key = (round(coords[0], 5), round(coords[1], 5))
                    manhole_points_coords.add(pt_key)
                self.manhole_nodes.append(feat)

            elif gtype == "LineString":
                if ww in ["drain", "ditch"]:
                    st_conduits.append(feat)
                elif ww in ["canal", "stream", "river"]:
                    self.receiving_channels.append(feat)

        cos_lat = math.cos(math.radians(13.04))

        for idx, feat in enumerate(st_conduits):
            edge_id = f"DRN_{idx:05d}"
            props = feat.get("properties", {})
            geom = feat.get("geometry", {})
            drain_id = str(props.get("@id", edge_id))
            coords = geom.get("coordinates", [])

            if len(coords) < 2:
                continue

            # Snapped endpoints (~5 decimal places / ~1m precision)
            start_coord = coords[0]
            end_coord = coords[-1]
            u_key = (round(start_coord[0], 5), round(start_coord[1], 5))
            v_key = (round(end_coord[0], 5), round(end_coord[1], 5))
            u_id = f"ND_{u_key[0]:.5f}_{u_key[1]:.5f}"
            v_id = f"ND_{v_key[0]:.5f}_{v_key[1]:.5f}"

            # Geodesic length computation
            total_l = 0.0
            for i in range(len(coords) - 1):
                dx = (coords[i+1][0] - coords[i][0]) * 111320.0 * cos_lat
                dy = (coords[i+1][1] - coords[i][1]) * 110540.0
                total_l += math.sqrt(dx*dx + dy*dy)
            length_m = max(5.0, round(total_l, 1))

            cen_lon = float(np.mean([pt[0] for pt in coords]))
            cen_lat = float(np.mean([pt[1] for pt in coords]))

            # Road Association & Terrain Attributes
            if drain_id in drain_road_lookup:
                info = drain_road_lookup[drain_id]
                z_ground = round(info["mean_elev"], 2)
                s0 = max(0.0005, min(0.025, round(info["mean_slope"], 5)))
                zone_no = info["zone_no"]
                hw_class = info["highway_class"]
                dia_m, dia_prov = self._infer_diameter_from_road(hw_class)
                z_ground_prov = "DERIVED_FROM_REAL_DEM (source_drain_id Road Match)"
                slope_prov = "PROXY (Surface Terrain Gradient from DEM)"
                zone_prov = "REAL_ASSOCIATION (Layer 1 source_drain_id Match)"
                slope_uncertain = False
            elif len(road_coords) > 0:
                dists_sq = (road_coords[:, 0] - cen_lon)**2 + (road_coords[:, 1] - cen_lat)**2
                min_idx = int(np.argmin(dists_sq))
                z_ground = round(float(road_elevs[min_idx]), 2)
                s0 = max(0.0005, min(0.025, round(float(road_slopes[min_idx]), 5)))
                zone_no = int(road_zones[min_idx])
                hw_class = road_hw_classes[min_idx]
                dia_m, dia_prov = self._infer_diameter_from_road(hw_class)
                z_ground_prov = "DERIVED_FROM_REAL_DEM (Nearest Road Segment Match)"
                slope_prov = "PROXY (Surface Terrain Gradient from DEM)"
                zone_prov = "SPATIAL_PROXY (Nearest Road Segment Match)"
                slope_uncertain = False
            else:
                z_ground = 6.0
                s0 = 0.002
                zone_no = 8
                dia_m = CPHEEO_PIPE_HIERARCHY["local"]
                dia_prov = "PROXY_DEFAULT (Unassociated Drain - Local Branch Baseline)"
                z_ground_prov = "ASSUMED (Default Domain Elevation)"
                slope_prov = "PROXY_FLAT_TERRAIN_MINIMUM"
                zone_prov = "UNKNOWN_FALLBACK"
                slope_uncertain = True

            # Manual field override takes highest precedence
            if edge_id in CMWSSB_FIELD_OVERRIDE_REGISTRY:
                dia_m = CMWSSB_FIELD_OVERRIDE_REGISTRY[edge_id]
                dia_prov = "CALIBRATED_FIELD_OVERRIDE"
            elif drain_id in CMWSSB_FIELD_OVERRIDE_REGISTRY:
                dia_m = CMWSSB_FIELD_OVERRIDE_REGISTRY[drain_id]
                dia_prov = "CALIBRATED_FIELD_OVERRIDE"

            # Structural descriptors
            tunnel_tag = props.get("tunnel")
            layer_tag = props.get("layer")
            is_enclosed = bool(tunnel_tag in ["culvert", "covered", "yes"] or layer_tag in ["-1", "-2"] or props.get("covered") == "yes")
            cross_section = "BOX_DRAIN" if (is_enclosed and dia_m >= 1.80) else ("CIRCULAR_RCC" if is_enclosed else "OPEN_MASONRY_CHANNEL")

            # Coastal outfall determination (GCC Coastal Zones 4, 5, 9, 13 discharging towards Bay of Bengal)
            is_coastal_outfall = bool(zone_no in [4, 5, 9, 13] and cen_lon >= 80.25)
            tidal_stage = self.tidal_engine.compute_tidal_stage_m(t_hours=2.0, storm_surge_m=0.35)
            z_invert = max(0.20, z_ground - 1.20) if is_coastal_outfall else max(0.50, z_ground - dia_m - 1.00)
            tidal_throttle = self.tidal_engine.compute_outfall_throttle_factor(z_invert, tidal_stage) if is_coastal_outfall else 1.0

            # Real GCC clogging factor
            mu = self.clogging_model.get_zone_clogging_factor(zone_no)

            # Hydraulic conveyance calculation
            if cross_section == "BOX_DRAIN":
                hydraulics = self.conduit_engine.calculate_box_culvert(
                    width_m=2.0,
                    height_m=1.5,
                    slope_m_per_m=s0,
                    mu_clog=mu
                )
            else:
                hydraulics = self.conduit_engine.calculate_circular_pipe(
                    diameter_m=dia_m,
                    slope_m_per_m=s0,
                    mu_clog=mu
                )

            effective_cap = round(hydraulics["effective_capacity_m3_s"] * tidal_throttle, 3)

            # Build edge record
            edge_record = {
                "edge_id": edge_id,
                "drain_id": drain_id,
                "from_node": u_id,
                "to_node": v_id,
                "longitude": round(cen_lon, 6),
                "latitude": round(cen_lat, 6),
                "waterway": props.get("waterway", "drain"),
                "is_enclosed": is_enclosed,
                "cross_section": cross_section,
                "structural_tags": {
                    "tunnel": tunnel_tag,
                    "layer": layer_tag,
                    "covered": props.get("covered")
                },
                "zone_no": zone_no,
                "length_m": length_m,
                "diameter_m": dia_m,
                "slope_m_per_m": s0,
                "slope_direction_uncertain": slope_uncertain,
                "z_ground_m": z_ground,
                "z_invert_m": round(z_invert, 2),
                "clogging_factor": mu,
                "is_coastal_outfall": is_coastal_outfall,
                "tidal_throttle": round(tidal_throttle, 2),
                "effective_capacity_m3_s": effective_cap,
                "nominal_capacity_m3_s": hydraulics["nominal_capacity_m3_s"],
                "capacity_loss_pct": hydraulics["capacity_loss_pct"],
                "provenance": {
                    "length": "DERIVED_FROM_REAL_GEOMETRY",
                    "diameter": dia_prov,
                    "ground_elevation": z_ground_prov,
                    "terrain_slope": slope_prov,
                    "pipe_bed_slope": "NOT_SURVEYED (Using Terrain Slope Proxy)",
                    "invert_elevation": "ASSUMED (CPHEEO Standard Burial Depth Heuristic; Not Surveyed)",
                    "clogging": "REAL_GCC_DATA",
                    "zone": zone_prov
                }
            }
            self.edges.append(edge_record)

            # Node creation and snapping
            if u_id not in self.nodes:
                self.nodes[u_id] = {
                    "node_id": u_id,
                    "longitude": u_key[0],
                    "latitude": u_key[1],
                    "z_ground_m": z_ground,
                    "is_outfall": False,
                    "is_manhole": u_key in manhole_points_coords,
                    "connected_edges": []
                }
            self.nodes[u_id]["connected_edges"].append(edge_id)

            if v_id not in self.nodes:
                self.nodes[v_id] = {
                    "node_id": v_id,
                    "longitude": v_key[0],
                    "latitude": v_key[1],
                    "z_ground_m": z_ground,
                    "is_outfall": is_coastal_outfall,
                    "is_manhole": v_key in manhole_points_coords,
                    "connected_edges": []
                }
            self.nodes[v_id]["connected_edges"].append(edge_id)
            if is_coastal_outfall:
                self.nodes[v_id]["is_outfall"] = True

        logger.info(
            "Constructed real Chennai drainage multigraph: %d conduit edges, %d nodes, %d receiving channels",
            len(self.edges), len(self.nodes), len(self.receiving_channels)
        )

    def _build_fallback_topology(self):
        """Isolated legacy fallback method; never invoked in the real-data production path."""
        for i in range(825):
            z = (i % 15) + 1
            mu = self.clogging_model.get_zone_clogging_factor(z)
            dia_m = 1.80 if i % 12 == 0 else (1.20 if i % 4 == 0 else (0.90 if i % 2 == 0 else 0.60))
            is_coastal = z in [4, 5, 9, 13] and (i % 6 == 0)
            throttle = 0.58 if is_coastal else 1.0
            h = self.conduit_engine.calculate_circular_pipe(diameter_m=dia_m, slope_m_per_m=0.002, mu_clog=mu)
            self.edges.append({
                "edge_id": f"DRN_{i:05d}",
                "zone_no": z,
                "length_m": 120.0,
                "diameter_m": dia_m,
                "slope_m_per_m": 0.002,
                "clogging_factor": mu,
                "is_coastal_outfall": is_coastal,
                "tidal_throttle": throttle,
                "effective_capacity_m3_s": round(h["effective_capacity_m3_s"] * throttle, 3),
                "nominal_capacity_m3_s": h["nominal_capacity_m3_s"],
                "capacity_loss_pct": h["capacity_loss_pct"]
            })

    def get_network_statistics(self) -> Dict[str, Any]:
        """Summary metrics of the subsurface drainage system."""
        if not self.edges:
            return {}

        caps = [e["effective_capacity_m3_s"] for e in self.edges]
        losses = [e["capacity_loss_pct"] for e in self.edges]
        lengths = [e["length_m"] for e in self.edges]

        return {
            "total_conduits": len(self.edges),
            "total_nodes": len(self.nodes),
            "total_receiving_channels": len(self.receiving_channels),
            "total_network_length_km": round(sum(lengths) / 1000.0, 2),
            "total_effective_discharge_m3_s": round(sum(caps), 2),
            "mean_clogging_loss_pct": round(float(np.mean(losses)), 1),
            "max_conduit_capacity_m3_s": max(caps),
            "min_conduit_capacity_m3_s": min(caps)
        }

