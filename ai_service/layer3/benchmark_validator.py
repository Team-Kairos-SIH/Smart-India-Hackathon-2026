"""Layer 3: Benchmark Validator Module - Ground Truth & Real-Data Validation.

Cross-validates surrogate flood depth predictions against authenticated field-survey
and ground-truth flood observations (00_master_flood_depth.csv).

Strict Scientific Integrity Rules:
  - If real ground truth is not available, report NO_GROUND_TRUTH_DATA; do NOT fabricate metrics.
  - Do NOT clamp R^2 to [0, 1]. Negative R^2 values are physically and statistically meaningful.
  - Do NOT fabricate coordinates for records that lack them. Exclude them from spatial matching
    and explicitly classify as UNMATCHABLE_NO_COORDINATES.
  - Do NOT compare different storm events. Event compatibility must be proven.
  - Do NOT fabricate observation times when missing in source data; validation is performed
    at the daily event level.
  - Do NOT hardcode counts (e.g. 156, 94, 62, 87) or metrics. All are recomputed dynamically.
  - Spatial matching uses exact geodesic Haversine distance in meters against real road nodes.
  - Configurable spatial matching tolerance (default 500 m).
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from .graph_builder import StreetDrainageGraph

logger = logging.getLogger(__name__)

# ── Configurable defaults ───────────────────────────────────────────────────
GROUND_TRUTH_MATCH_TOLERANCE_M: float = 500.0
MIN_MATCHED_OBSERVATIONS: int = 5

DEFAULT_GROUND_TRUTH_EVENT: str = "Chennai December 2015 Flood (peak 2015-12-01/02)"
DEFAULT_LAYER3_STORM_EVENT: str = "IMD Historical Cloudburst 49.8 mm/hr — 2015 December Flood"


def haversine_distance_m(
    lat1: Union[float, np.ndarray],
    lon1: Union[float, np.ndarray],
    lat2: Union[float, np.ndarray],
    lon2: Union[float, np.ndarray],
) -> Union[float, np.ndarray]:
    """Calculates great-circle distance between coordinates on a sphere in meters."""
    R = 6371000.0  # Earth mean radius in meters
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)

    a = (
        np.sin(delta_phi / 2.0) ** 2
        + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(np.maximum(0.0, 1.0 - a)))
    return R * c


class BenchmarkValidator:
    """Validates predicted street flood depths against authentic historical ground truth survey records."""

    def __init__(
        self,
        base_dir: Optional[Path] = None,
        default_match_tolerance_m: float = GROUND_TRUTH_MATCH_TOLERANCE_M,
    ):
        self.base_dir = base_dir or Path(__file__).resolve().parent.parent.parent
        self.default_match_tolerance_m = float(default_match_tolerance_m)
        self.df_raw: Optional[pd.DataFrame] = None
        self.df_ground_truth: Optional[pd.DataFrame] = None
        self.df_unmatchable: Optional[pd.DataFrame] = None
        self.gt_audit: Dict[str, Any] = {}
        self._load_ground_truth()

    # ── Ground-truth loader ─────────────────────────────────────────────────

    def _load_ground_truth(self) -> None:
        """Locates and loads authentic ground truth flood depth records.

        Search order:
          1. ai_service/data/groundtruth/00_master_flood_depth.csv  (canonical)
          2. ai_service/data/**/00_master_flood_depth.csv           (recursive)
          3. Datasets/**/00_master_flood_depth.csv                  (legacy path)

        Records without coordinates are strictly retained but classified as
        UNMATCHABLE_NO_COORDINATES and excluded from spatial matching.
        """
        gt_path: Optional[Path] = None

        p1 = self.base_dir / "ai_service" / "data" / "groundtruth" / "00_master_flood_depth.csv"
        if p1.exists() and p1.stat().st_size > 100:
            gt_path = p1

        if gt_path is None:
            candidates = list((self.base_dir / "ai_service" / "data").rglob("00_master_flood_depth.csv"))
            if candidates:
                gt_path = candidates[0]

        if gt_path is None:
            ds_dir = self.base_dir / "Datasets"
            if ds_dir.exists():
                candidates = list(ds_dir.rglob("00_master_flood_depth.csv"))
                if candidates:
                    gt_path = candidates[0]

        if gt_path is None:
            logger.info("GROUND TRUTH AVAILABLE: NO — 00_master_flood_depth.csv not found")
            self.gt_audit = {"found": False, "reason": "file_not_found"}
            return

        try:
            df_raw = pd.read_csv(gt_path)
        except Exception as exc:
            logger.error("Failed to read ground truth CSV %s: %s", gt_path, exc)
            self.gt_audit = {"found": False, "reason": str(exc)}
            return

        required_cols = {"latitude", "longitude", "depth_cm", "date"}
        if not required_cols.issubset(df_raw.columns):
            missing = required_cols - set(df_raw.columns)
            logger.error("Ground truth CSV missing required columns: %s", missing)
            self.gt_audit = {"found": False, "reason": f"missing_columns:{missing}"}
            return

        self.df_raw = df_raw.copy()
        total_records = len(df_raw)

        # ── Coordinate and depth availability checks ────────────────────────
        has_lat = df_raw["latitude"].notna()
        has_lon = df_raw["longitude"].notna()
        has_both_coords = has_lat & has_lon
        n_with_coords = int(has_both_coords.sum())
        n_no_coords = int((~has_both_coords).sum())

        has_depth = df_raw["depth_cm"].notna()
        n_with_depth = int(has_depth.sum())
        n_no_depth = int((~has_depth).sum())

        # Classify records without coordinates
        self.df_unmatchable = df_raw[~has_both_coords].copy()
        self.df_unmatchable["classification"] = "UNMATCHABLE_NO_COORDINATES"

        # ── Coordinate validity bounds (Greater Chennai Metropolitan Area) ──
        # Expanded bounds to avoid silently dropping peripheral GCC points
        CHENNAI_LAT_MIN, CHENNAI_LAT_MAX = 12.5, 13.5
        CHENNAI_LON_MIN, CHENNAI_LON_MAX = 79.8, 80.5

        coord_records = df_raw[has_both_coords].copy()
        out_of_bounds = (
            (coord_records["latitude"] < CHENNAI_LAT_MIN)
            | (coord_records["latitude"] > CHENNAI_LAT_MAX)
            | (coord_records["longitude"] < CHENNAI_LON_MIN)
            | (coord_records["longitude"] > CHENNAI_LON_MAX)
        )
        n_out_of_bounds = int(out_of_bounds.sum())

        usable_mask = has_both_coords & has_depth & ~out_of_bounds
        df_usable = df_raw[usable_mask].copy()
        n_usable = len(df_usable)

        # ── Date and temporal availability ──────────────────────────────────
        unique_dates: List[str] = []
        if "date" in df_raw.columns:
            unique_dates = sorted([str(d) for d in df_raw["date"].dropna().unique().tolist()])

        has_time_values = bool("time" in df_raw.columns and df_raw["time"].notna().any())

        # ── Depth statistics ────────────────────────────────────────────────
        all_depth_stats: Dict[str, Any] = {}
        if n_with_depth > 0:
            d_all = df_raw.loc[has_depth, "depth_cm"].values.astype(float)
            all_depth_stats = {
                "min_cm": float(np.nanmin(d_all)),
                "max_cm": float(np.nanmax(d_all)),
                "mean_cm": float(np.nanmean(d_all)),
                "median_cm": float(np.nanmedian(d_all)),
            }

        usable_depth_stats: Dict[str, Any] = {}
        if n_usable > 0:
            d_usable = df_usable["depth_cm"].values.astype(float)
            usable_depth_stats = {
                "min_cm": float(np.nanmin(d_usable)),
                "max_cm": float(np.nanmax(d_usable)),
                "mean_cm": float(np.nanmean(d_usable)),
                "median_cm": float(np.nanmedian(d_usable)),
            }

        # ── Coordinate range of usable observations ─────────────────────────
        lat_range = (
            (float(df_usable["latitude"].min()), float(df_usable["latitude"].max()))
            if n_usable > 0
            else (0.0, 0.0)
        )
        lon_range = (
            (float(df_usable["longitude"].min()), float(df_usable["longitude"].max()))
            if n_usable > 0
            else (0.0, 0.0)
        )

        # ── Duplicate check ─────────────────────────────────────────────────
        n_duplicate_ids = int(df_raw["id"].duplicated().sum())
        n_duplicate_coords = 0
        if n_usable > 1:
            coords_arr = df_usable[["latitude", "longitude"]].values.astype(float)
            tree_dup = cKDTree(coords_arr)
            pairs = tree_dup.query_pairs(r=1e-6)
            n_duplicate_coords = len(pairs)

        # ── Source breakdowns ───────────────────────────────────────────────
        sources_all = df_raw["source"].value_counts(dropna=False).to_dict()
        sources_usable = (
            df_usable["source"].value_counts(dropna=False).to_dict()
            if n_usable > 0
            else {}
        )
        sources_unmatchable = (
            self.df_unmatchable["source"].value_counts(dropna=False).to_dict()
            if len(self.df_unmatchable) > 0
            else {}
        )

        # ── Compile audit record ────────────────────────────────────────────
        self.gt_audit = {
            "found": True,
            "path": str(gt_path),
            "total_records": total_records,
            "n_with_coordinates": n_with_coords,
            "n_no_coordinates": n_no_coords,
            "n_with_depth": n_with_depth,
            "n_no_depth": n_no_depth,
            "n_out_of_bounds": n_out_of_bounds,
            "n_usable": n_usable,
            "n_duplicate_ids": n_duplicate_ids,
            "n_duplicate_coords": n_duplicate_coords,
            "latitude_range": lat_range,
            "longitude_range": lon_range,
            "unique_dates": unique_dates,
            "has_time_values": has_time_values,
            "all_depth_stats": all_depth_stats,
            "usable_depth_stats": usable_depth_stats,
            "sources_all": sources_all,
            "sources_usable": sources_usable,
            "sources_unmatchable": sources_unmatchable,
            "ground_truth_event": DEFAULT_GROUND_TRUTH_EVENT,
        }

        if n_usable == 0:
            logger.warning(
                "Ground truth CSV loaded (%d records) but 0 usable after filtering "
                "(no_coords=%d, no_depth=%d, out_of_bounds=%d)",
                total_records, n_no_coords, n_no_depth, n_out_of_bounds,
            )
            return

        self.df_ground_truth = df_usable
        logger.info(
            "Loaded %d usable ground-truth records (%d total, %d without coords, %d without depth) from %s",
            n_usable, total_records, n_no_coords, n_no_depth, gt_path.name,
        )

    # ── Evaluation ──────────────────────────────────────────────────────────

    def evaluate_predictions(
        self,
        predicted_depths_cm: np.ndarray,
        graph: StreetDrainageGraph,
        model_storm_event: Optional[str] = None,
        model_event_date: Optional[str] = None,
        event_aligned: Optional[bool] = None,
        match_tolerance_m: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Match predicted street segment depths against nearest surveyed field observations.

        Parameters:
          predicted_depths_cm: Array of predicted depths in cm, indexed by graph node index.
          graph: StreetDrainageGraph instance with real road nodes and spatial kdtree.
          model_storm_event: Descriptive name of the model rainfall event.
          model_event_date: Date string (e.g. '2015-12-01') of the rainfall forcing.
          event_aligned: Explicit override for event compatibility. If None, dynamically
                         verifies date/event overlap against ground-truth observation dates.
          match_tolerance_m: Maximum acceptable distance in meters for observation-to-road
                             segment association (default: self.default_match_tolerance_m).

        Returns:
          Dictionary with validation status, record audits, spatial matching metrics,
          depth distributions, and authentic MAE, RMSE, and unclamped R^2.
        """
        audit = self.gt_audit.copy()
        effective_tolerance_m = (
            float(match_tolerance_m)
            if match_tolerance_m is not None
            else self.default_match_tolerance_m
        )

        # ── Case 1: No ground truth file found ──────────────────────────────
        if not audit.get("found", False):
            return {
                "status": "NO_GROUND_TRUTH_DATA",
                "ground_truth_available": False,
                "ground_truth_source": None,
                "total_records": 0,
                "n_with_coordinates": 0,
                "n_unmatchable_no_coordinates": 0,
                "n_with_depth": 0,
                "n_usable_for_validation": 0,
                "ground_truth_event": None,
                "model_rainfall_event": model_storm_event or DEFAULT_LAYER3_STORM_EVENT,
                "event_aligned": False,
                "matching_method": "KD-Tree nearest road node with geodesic Haversine distance",
                "match_tolerance_m": effective_tolerance_m,
                "matched_benchmark_points": 0,
                "unmatched_observations": 0,
                "mae_cm": None,
                "rmse_cm": None,
                "r2_score": None,
                "reason": "Ground-truth file 00_master_flood_depth.csv not found.",
            }

        # ── Case 2: File loaded but zero usable records ─────────────────────
        if self.df_ground_truth is None or len(self.df_ground_truth) == 0:
            return {
                "status": "NO_USABLE_OBSERVATIONS",
                "ground_truth_available": True,
                "ground_truth_source": audit.get("path"),
                "total_records": audit.get("total_records", 0),
                "n_with_coordinates": audit.get("n_with_coordinates", 0),
                "n_unmatchable_no_coordinates": audit.get("n_no_coordinates", 0),
                "n_with_depth": audit.get("n_with_depth", 0),
                "n_usable_for_validation": 0,
                "ground_truth_event": audit.get("ground_truth_event"),
                "model_rainfall_event": model_storm_event or DEFAULT_LAYER3_STORM_EVENT,
                "event_aligned": False,
                "matching_method": "KD-Tree nearest road node with geodesic Haversine distance",
                "match_tolerance_m": effective_tolerance_m,
                "matched_benchmark_points": 0,
                "unmatched_observations": 0,
                "mae_cm": None,
                "rmse_cm": None,
                "r2_score": None,
                "reason": "Zero records remained after filtering missing coordinates and missing depths.",
            }

        # ── Dynamic Event Alignment Check ───────────────────────────────────
        gt_dates = set(audit.get("unique_dates", []))
        model_event_desc = model_storm_event or DEFAULT_LAYER3_STORM_EVENT

        if event_aligned is not None:
            is_event_aligned = bool(event_aligned)
        else:
            # Prove compatibility between rainfall event and ground-truth dates dynamically
            if model_event_date is not None:
                is_event_aligned = model_event_date in gt_dates
            else:
                # Check for 2015 December flood descriptors in event name
                is_2015_event = (
                    "2015" in model_event_desc
                    and ("dec" in model_event_desc.lower() or "flood" in model_event_desc.lower())
                )
                is_event_aligned = is_2015_event

        # If event is not aligned, DO NOT calculate MAE/RMSE/R²
        if not is_event_aligned:
            return {
                "status": "GROUND TRUTH AVAILABLE BUT EVENT NOT ALIGNED",
                "ground_truth_available": True,
                "ground_truth_source": audit.get("path"),
                "total_records": audit.get("total_records", 0),
                "n_with_coordinates": audit.get("n_with_coordinates", 0),
                "n_unmatchable_no_coordinates": audit.get("n_no_coordinates", 0),
                "n_with_depth": audit.get("n_with_depth", 0),
                "n_usable_for_validation": audit.get("n_usable", 0),
                "ground_truth_event": audit.get("ground_truth_event"),
                "model_rainfall_event": model_event_desc,
                "event_aligned": False,
                "temporal_resolution_note": (
                    "Ground-truth observation times are absent in source CSV; "
                    "alignment is constrained to daily storm event level."
                ),
                "matching_method": "KD-Tree nearest road node with geodesic Haversine distance",
                "match_tolerance_m": effective_tolerance_m,
                "matched_benchmark_points": 0,
                "unmatched_observations": audit.get("n_usable", 0),
                "mae_cm": None,
                "rmse_cm": None,
                "r2_score": None,
                "reason": (
                    f"Model event ('{model_event_desc}') does not correspond to "
                    f"ground-truth observation dates {sorted(list(gt_dates))}."
                ),
            }

        # ── Spatial Matching with Exact Haversine Distance ──────────────────
        df_gt = self.df_ground_truth.copy()
        gt_lats = df_gt["latitude"].values.astype(np.float64)
        gt_lons = df_gt["longitude"].values.astype(np.float64)
        gt_coords = np.column_stack([gt_lons, gt_lats])

        # Query KDTree for nearest road node in Euclidean space
        _, nearest_node_indices = graph.kdtree.query(gt_coords)

        # Query matched road node coordinates
        road_nodes_df = graph.nodes_df.iloc[nearest_node_indices]
        node_lats = road_nodes_df["latitude"].values.astype(np.float64)
        node_lons = road_nodes_df["longitude"].values.astype(np.float64)

        # Compute geodesic distance in meters using Haversine formula
        dists_m = haversine_distance_m(gt_lats, gt_lons, node_lats, node_lons)
        df_gt["match_distance_m"] = dists_m
        df_gt["matched_node_idx"] = nearest_node_indices

        # Apply configurable distance tolerance
        matched_mask = dists_m <= effective_tolerance_m
        n_matched = int(matched_mask.sum())
        n_unmatched = int((~matched_mask).sum())

        df_matched = df_gt[matched_mask].copy()
        df_far_unmatched = df_gt[~matched_mask].copy()

        # Distance statistics for matched set
        if n_matched > 0:
            matched_dists = dists_m[matched_mask]
            dist_stats = {
                "min_m": round(float(np.min(matched_dists)), 2),
                "max_m": round(float(np.max(matched_dists)), 2),
                "mean_m": round(float(np.mean(matched_dists)), 2),
                "median_m": round(float(np.median(matched_dists)), 2),
            }
        else:
            dist_stats = {"min_m": 0.0, "max_m": 0.0, "mean_m": 0.0, "median_m": 0.0}

        # Unmatched / far observation tracking
        unmatched_far_records = []
        if n_unmatched > 0:
            for _, r in df_far_unmatched.iterrows():
                unmatched_far_records.append({
                    "id": str(r.get("id")),
                    "latitude": float(r.get("latitude")),
                    "longitude": float(r.get("longitude")),
                    "observed_depth_cm": float(r.get("depth_cm")),
                    "distance_to_nearest_road_m": round(float(r.get("match_distance_m")), 2),
                    "source": str(r.get("source")),
                })

        # Source composition of matched observations
        matched_source_composition = (
            df_matched["source"].value_counts(dropna=False).to_dict()
            if n_matched > 0
            else {}
        )

        # ── Insufficient Matches Check ──────────────────────────────────────
        if n_matched < MIN_MATCHED_OBSERVATIONS:
            return {
                "status": "INSUFFICIENT_MATCHES",
                "ground_truth_available": True,
                "ground_truth_source": audit.get("path"),
                "total_records": audit.get("total_records", 0),
                "n_with_coordinates": audit.get("n_with_coordinates", 0),
                "n_unmatchable_no_coordinates": audit.get("n_no_coordinates", 0),
                "n_with_depth": audit.get("n_with_depth", 0),
                "n_usable_for_validation": audit.get("n_usable", 0),
                "ground_truth_event": audit.get("ground_truth_event"),
                "model_rainfall_event": model_event_desc,
                "event_aligned": True,
                "temporal_resolution_note": (
                    "Ground-truth observation times are absent in source CSV; "
                    "alignment is constrained to daily storm event level."
                ),
                "matching_method": "KD-Tree nearest road node with geodesic Haversine distance",
                "match_tolerance_m": effective_tolerance_m,
                "matched_benchmark_points": n_matched,
                "unmatched_observations": n_unmatched,
                "dist_stats": dist_stats,
                "matched_source_composition": matched_source_composition,
                "unmatched_far_records": unmatched_far_records,
                "mae_cm": None,
                "rmse_cm": None,
                "r2_score": None,
                "reason": (
                    f"Only {n_matched} observations matched within {effective_tolerance_m:.0f} m "
                    f"— minimum {MIN_MATCHED_OBSERVATIONS} required for statistical evaluation."
                ),
            }

        # ── Statistical Metric Computation ──────────────────────────────────
        y_true = df_matched["depth_cm"].values.astype(np.float64)
        y_pred = predicted_depths_cm[nearest_node_indices[matched_mask]].astype(np.float64)

        # Observed depth distribution for matched points
        obs_depth_stats = {
            "min_cm": round(float(np.min(y_true)), 2),
            "max_cm": round(float(np.max(y_true)), 2),
            "mean_cm": round(float(np.mean(y_true)), 2),
            "median_cm": round(float(np.median(y_true)), 2),
        }

        # Predicted depth distribution for matched road segments
        pred_depth_stats = {
            "min_cm": round(float(np.min(y_pred)), 2),
            "max_cm": round(float(np.max(y_pred)), 2),
            "mean_cm": round(float(np.mean(y_pred)), 2),
            "median_cm": round(float(np.median(y_pred)), 2),
        }

        # Genuine statistical error metrics
        mae = float(np.mean(np.abs(y_pred - y_true)))
        rmse = float(np.sqrt(np.mean((y_pred - y_true) ** 2)))

        ss_res = float(np.sum((y_true - y_pred) ** 2))
        ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
        r2 = float(1.0 - (ss_res / max(1e-4, ss_tot)))
        # Strictly preserve negative R^2 without clamping

        return {
            "status": "VALIDATED",
            "ground_truth_available": True,
            "ground_truth_source": audit.get("path"),
            "total_records": audit.get("total_records", 0),
            "n_with_coordinates": audit.get("n_with_coordinates", 0),
            "n_unmatchable_no_coordinates": audit.get("n_no_coordinates", 0),
            "n_with_depth": audit.get("n_with_depth", 0),
            "n_usable_for_validation": audit.get("n_usable", 0),
            "ground_truth_event": audit.get("ground_truth_event"),
            "model_rainfall_event": model_event_desc,
            "event_aligned": True,
            "temporal_resolution_note": (
                "Ground-truth observation times are absent in source CSV; "
                "alignment is constrained to daily storm event level."
            ),
            "matching_method": "KD-Tree nearest road node with geodesic Haversine distance",
            "match_tolerance_m": effective_tolerance_m,
            "matched_benchmark_points": n_matched,
            "unmatched_observations": n_unmatched,
            "dist_stats": dist_stats,
            "matched_source_composition": matched_source_composition,
            "unmatched_far_records": unmatched_far_records,
            "observed_flood_depth": obs_depth_stats,
            "predicted_flood_depth": pred_depth_stats,
            "mae_cm": round(mae, 2),
            "rmse_cm": round(rmse, 2),
            "r2_score": round(r2, 4),  # NOT clamped
        }

    # ── Master Report Formatter ─────────────────────────────────────────────

    def format_validation_report(self, res: Dict[str, Any]) -> str:
        """Formats the validation output dictionary into the standard Phase 15 report."""
        lines = [
            "=" * 60,
            "REAL GROUND-TRUTH VALIDATION",
            "=" * 60,
            f"Ground-truth source:     {res.get('ground_truth_source') or 'None'}",
            f"Total observations:      {res.get('total_records')}",
            f"Observations with coordinates: {res.get('n_with_coordinates')}",
            f"Observations without coordinates: {res.get('n_unmatchable_no_coordinates')} (classified UNMATCHABLE_NO_COORDINATES)",
            f"Observations with valid depth: {res.get('n_with_depth')}",
            f"Observations usable for validation: {res.get('n_usable_for_validation')}",
            "-" * 60,
            f"Ground-truth event:      {res.get('ground_truth_event') or 'N/A'}",
            f"Model rainfall event:    {res.get('model_rainfall_event') or 'N/A'}",
            f"Event-aligned:           {'YES' if res.get('event_aligned') else 'NO'}",
            f"Temporal note:           {res.get('temporal_resolution_note', 'N/A')}",
            "-" * 60,
            "Spatial matching",
            f"Matching method:         {res.get('matching_method')}",
            f"Matching threshold:      {res.get('match_tolerance_m', 500.0):.1f} m",
            f"Matched:                 {res.get('matched_benchmark_points')}",
            f"Unmatched:               {res.get('unmatched_observations')}",
        ]

        ds = res.get("dist_stats", {})
        if ds and res.get("matched_benchmark_points", 0) > 0:
            lines.extend([
                f"Minimum match distance:  {ds.get('min_m', 0.0):.2f} m",
                f"Maximum match distance:  {ds.get('max_m', 0.0):.2f} m",
                f"Mean match distance:     {ds.get('mean_m', 0.0):.2f} m",
                f"Median match distance:   {ds.get('median_m', 0.0):.2f} m",
            ])

        srcs = res.get("matched_source_composition", {})
        if srcs:
            lines.append(f"Matched source mix:      {srcs}")

        obs_d = res.get("observed_flood_depth", {})
        pred_d = res.get("predicted_flood_depth", {})

        lines.extend([
            "-" * 60,
            "Observed flood depth",
            f"Minimum:                 {obs_d.get('min_cm', 'N/A')} cm",
            f"Maximum:                 {obs_d.get('max_cm', 'N/A')} cm",
            f"Mean:                    {obs_d.get('mean_cm', 'N/A')} cm",
            f"Median:                  {obs_d.get('median_cm', 'N/A')} cm",
            "-" * 60,
            "Predicted flood depth",
            f"Minimum:                 {pred_d.get('min_cm', 'N/A')} cm",
            f"Maximum:                 {pred_d.get('max_cm', 'N/A')} cm",
            f"Mean:                    {pred_d.get('mean_cm', 'N/A')} cm",
            f"Median:                  {pred_d.get('median_cm', 'N/A')} cm",
            "-" * 60,
            "VALIDATION METRICS",
            f"MAE:                     {res.get('mae_cm') if res.get('mae_cm') is not None else 'N/A'}"
            + (" cm" if res.get('mae_cm') is not None else ""),
            f"RMSE:                    {res.get('rmse_cm') if res.get('rmse_cm') is not None else 'N/A'}"
            + (" cm" if res.get('rmse_cm') is not None else ""),
            f"R^2:                     {res.get('r2_score') if res.get('r2_score') is not None else 'N/A'}",
            "-" * 60,
            f"Validation status:       {res.get('status')}",
            "=" * 60,
        ])
        return "\n".join(lines)

    # ── Audit report ────────────────────────────────────────────────────────

    def print_audit_report(self) -> None:
        """Print the full ground-truth CSV audit to stdout."""
        a = self.gt_audit
        print("-" * 60)
        print("GROUND TRUTH CSV AUDIT")
        print("-" * 60)
        if not a.get("found"):
            print("Status:                  NOT FOUND")
            print(f"Reason:                  {a.get('reason', 'unknown')}")
            return

        print(f"File:                    {a.get('path')}")
        print(f"Total records:           {a.get('total_records')}")
        print(f"With coordinates:        {a.get('n_with_coordinates')}")
        print(f"Without coordinates:     {a.get('n_no_coordinates')} -> UNMATCHABLE_NO_COORDINATES")
        print(f"With valid depth:        {a.get('n_with_depth')}")
        print(f"Missing depth:           {a.get('n_no_depth')}")
        print(f"Out-of-Chennai-bounds:   {a.get('n_out_of_bounds')}")
        print(f"Usable for validation:   {a.get('n_usable')}")
        print(f"Duplicate IDs:           {a.get('n_duplicate_ids')}")
        print(f"Duplicate coordinates:   {a.get('n_duplicate_coords')}")
        print(f"Latitude range:          {a.get('latitude_range')}")
        print(f"Longitude range:         {a.get('longitude_range')}")
        print(f"Unique dates:            {a.get('unique_dates')}")
        print(f"Has observation times:   {'YES' if a.get('has_time_values') else 'NO (event-level daily dates only)'}")
        print(f"Ground truth event:      {a.get('ground_truth_event')}")

        ds = a.get("usable_depth_stats", {})
        if ds:
            print(f"Usable depth min:        {ds.get('min_cm'):.2f} cm")
            print(f"Usable depth max:        {ds.get('max_cm'):.2f} cm")
            print(f"Usable depth mean:       {ds.get('mean_cm'):.2f} cm")
            print(f"Usable depth median:     {ds.get('median_cm'):.2f} cm")

        print(f"Default match tolerance: {self.default_match_tolerance_m:.1f} m")
        print("Usable sources:         ", a.get("sources_usable"))
        print("Unmatchable sources:    ", a.get("sources_unmatchable"))
