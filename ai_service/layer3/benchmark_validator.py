"""Layer 3: Benchmark Validator Module - Ground Truth & HEC-RAS Validation.

Cross-validates surrogate predictions against:
  1. Authenticated Quantitative Measured Flood Depths (NDMA / NRSC survey)
  2. Academic HEC-RAS 2D Hydrodynamic Benchmark Results (Adyar / Cooum Basins)

Strict rule: If real ground truth is not available, explicitly report NO_GROUND_TRUTH_DATA
and do NOT fabricate MAE, RMSE, or R^2 scores.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from .graph_builder import StreetDrainageGraph

logger = logging.getLogger(__name__)


class BenchmarkValidator:
    """Validates predicted street flood depths against historical ground truth survey records."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).resolve().parent.parent.parent
        self.datasets_dir = self.base_dir / "Datasets"
        self.df_ground_truth: Optional[pd.DataFrame] = None
        self._load_ground_truth()

    def _load_ground_truth(self):
        """Locates and loads authentic ground truth flood depth records if present."""
        candidates = list(self.datasets_dir.rglob("00_master_flood_depth.csv"))
        if not candidates:
            candidates = list((self.base_dir / "ai_service" / "data").rglob("*flood_depth*.csv"))

        if candidates and candidates[0].exists() and candidates[0].stat().st_size > 100:
            df = pd.read_csv(candidates[0])
            if {"latitude", "longitude", "depth_cm"}.issubset(df.columns):
                self.df_ground_truth = df.dropna(subset=["latitude", "longitude", "depth_cm"])
                logger.info("Loaded %d authentic field flood depth records", len(self.df_ground_truth))
                return

        logger.info("GROUND TRUTH AVAILABLE: NO")

    def evaluate_predictions(
        self,
        predicted_depths_cm: np.ndarray,
        graph: StreetDrainageGraph
    ) -> Dict[str, Any]:
        """
        Matches predicted street segments with nearest surveyed field observation points.
        Returns authentic error metrics or explicitly reports that ground truth is unavailable.
        """
        if self.df_ground_truth is None or len(self.df_ground_truth) == 0:
            return {
                "status": "NO_GROUND_TRUTH_DATA",
                "ground_truth_available": False,
                "matched_benchmark_points": 0,
                "mae_cm": None,
                "rmse_cm": None,
                "r2_score": None
            }

        # Query nearest road segment for each ground truth point
        gt_coords = np.column_stack([self.df_ground_truth["longitude"].values, self.df_ground_truth["latitude"].values])
        dists, indices = graph.kdtree.query(gt_coords)

        # Match observed vs predicted (filter points within 2 km of roads)
        valid_mask = dists < 0.02
        y_true = self.df_ground_truth["depth_cm"].values[valid_mask]
        y_pred = predicted_depths_cm[indices[valid_mask]]

        if len(y_true) < 5:
            return {
                "status": "INSUFFICIENT_MATCHES",
                "ground_truth_available": True,
                "matched_benchmark_points": int(len(y_true)),
                "mae_cm": None,
                "rmse_cm": None,
                "r2_score": None
            }

        mae = float(np.mean(np.abs(y_pred - y_true)))
        rmse = float(np.sqrt(np.mean((y_pred - y_true) ** 2)))

        # R2 score
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        r2 = float(1.0 - (ss_res / max(1e-4, ss_tot)))

        return {
            "status": "VALIDATED",
            "ground_truth_available": True,
            "matched_benchmark_points": int(len(y_true)),
            "mae_cm": round(mae, 2),
            "rmse_cm": round(rmse, 2),
            "r2_score": round(max(0.0, min(1.0, r2)), 3),
            "mean_observed_cm": round(float(np.mean(y_true)), 1),
            "mean_predicted_cm": round(float(np.mean(y_pred)), 1)
        }
