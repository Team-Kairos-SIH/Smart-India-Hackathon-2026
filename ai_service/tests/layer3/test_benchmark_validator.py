"""Unit tests for Layer 3 BenchmarkValidator with real ground-truth dataset.

Tests scientific rigor, dynamic counts, geodesic Haversine distance spatial matching,
event alignment, missing data handling, and negative R^2 preservation.
"""

import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

from ai_service.layer3.benchmark_validator import (
    BenchmarkValidator,
    haversine_distance_m,
    GROUND_TRUTH_MATCH_TOLERANCE_M,
)
from ai_service.layer3.graph_builder import StreetDrainageGraph


class TestBenchmarkValidator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[3]
        cls.validator = BenchmarkValidator(base_dir=cls.repo_root)
        cls.graph = StreetDrainageGraph(base_dir=cls.repo_root)

    def test_01_haversine_formula_accuracy(self):
        """Verify Haversine formula against known geographic distance."""
        # Distance between Chennai Central (13.0827, 80.2707) and Guindy (13.0067, 80.2025)
        # Known straight-line distance is approx ~11.0 km (11,000 m)
        d_m = haversine_distance_m(13.0827, 80.2707, 13.0067, 80.2025)
        self.assertAlmostEqual(d_m, 11000.0, delta=500.0)

        # Distance between identical points is 0.0
        d_zero = haversine_distance_m(13.0, 80.2, 13.0, 80.2)
        self.assertEqual(d_zero, 0.0)

    def test_02_dynamic_ground_truth_audit(self):
        """Verify ground-truth CSV loading and dynamic count audit."""
        self.assertTrue(self.validator.gt_audit.get("found"))
        total = self.validator.gt_audit["total_records"]
        n_coords = self.validator.gt_audit["n_with_coordinates"]
        n_no_coords = self.validator.gt_audit["n_no_coordinates"]
        n_depth = self.validator.gt_audit["n_with_depth"]
        n_usable = self.validator.gt_audit["n_usable"]

        # Dynamically verify counts against actual loaded dataframe
        df_raw = self.validator.df_raw
        self.assertIsNotNone(df_raw)
        self.assertEqual(len(df_raw), total)
        self.assertEqual(int(df_raw["latitude"].notna().sum()), n_coords)
        self.assertEqual(int(df_raw["latitude"].isna().sum()), n_no_coords)
        self.assertEqual(total, n_coords + n_no_coords)
        self.assertEqual(int(df_raw["depth_cm"].notna().sum()), n_depth)

        # Usable records must have both coords, valid depth, and be in bounds
        self.assertEqual(len(self.validator.df_ground_truth), n_usable)

        # Unmatchable records must be retained with classification
        self.assertIsNotNone(self.validator.df_unmatchable)
        self.assertEqual(len(self.validator.df_unmatchable), n_no_coords)
        self.assertTrue(
            (self.validator.df_unmatchable["classification"] == "UNMATCHABLE_NO_COORDINATES").all()
        )

    def test_03_spatial_matching_and_tolerance(self):
        """Verify spatial matching with exact Haversine distance and configurable tolerance."""
        n_nodes = len(self.graph.nodes_df)
        pred_dummy = np.full(n_nodes, 10.0, dtype=np.float64)

        # Run with default 500m tolerance
        res_500 = self.validator.evaluate_predictions(
            predicted_depths_cm=pred_dummy,
            graph=self.graph,
            model_event_date="2015-12-01",
            match_tolerance_m=500.0,
        )
        self.assertEqual(res_500["status"], "VALIDATED")
        self.assertEqual(res_500["match_tolerance_m"], 500.0)
        self.assertGreater(res_500["matched_benchmark_points"], 0)
        self.assertEqual(
            res_500["matched_benchmark_points"] + res_500["unmatched_observations"],
            self.validator.gt_audit["n_usable"],
        )

        # Verify distance statistics are populated and non-zero
        ds = res_500["dist_stats"]
        self.assertGreater(ds["min_m"], 0.0)
        self.assertLessEqual(ds["max_m"], 500.0)
        self.assertGreaterEqual(ds["mean_m"], ds["min_m"])
        self.assertLessEqual(ds["mean_m"], ds["max_m"])

        # Run with tighter tolerance (e.g. 100m)
        res_100 = self.validator.evaluate_predictions(
            predicted_depths_cm=pred_dummy,
            graph=self.graph,
            model_event_date="2015-12-01",
            match_tolerance_m=100.0,
        )
        self.assertLess(res_100["matched_benchmark_points"], res_500["matched_benchmark_points"])
        self.assertLessEqual(res_100["dist_stats"]["max_m"], 100.0)

    def test_04_unaligned_event_handling(self):
        """Verify unaligned events report GROUND TRUTH AVAILABLE BUT EVENT NOT ALIGNED without fabricated metrics."""
        n_nodes = len(self.graph.nodes_df)
        pred_dummy = np.full(n_nodes, 10.0, dtype=np.float64)

        res = self.validator.evaluate_predictions(
            predicted_depths_cm=pred_dummy,
            graph=self.graph,
            model_storm_event="Cyclone Michaung Dec 2023",
            model_event_date="2023-12-04",
        )
        self.assertEqual(res["status"], "GROUND TRUTH AVAILABLE BUT EVENT NOT ALIGNED")
        self.assertTrue(res["ground_truth_available"])
        self.assertFalse(res["event_aligned"])
        self.assertIsNone(res["mae_cm"])
        self.assertIsNone(res["rmse_cm"])
        self.assertIsNone(res["r2_score"])
        self.assertIn("reason", res)

    def test_05_missing_ground_truth_file(self):
        """Verify missing ground truth file reports NO_GROUND_TRUTH_DATA safely."""
        with tempfile.TemporaryDirectory() as tmpdir:
            empty_validator = BenchmarkValidator(base_dir=Path(tmpdir))
            n_nodes = len(self.graph.nodes_df)
            pred_dummy = np.full(n_nodes, 5.0, dtype=np.float64)

            res = empty_validator.evaluate_predictions(
                predicted_depths_cm=pred_dummy,
                graph=self.graph,
            )
            self.assertEqual(res["status"], "NO_GROUND_TRUTH_DATA")
            self.assertFalse(res["ground_truth_available"])
            self.assertIsNone(res["mae_cm"])
            self.assertIsNone(res["rmse_cm"])
            self.assertIsNone(res["r2_score"])

    def test_06_insufficient_matches_handling(self):
        """Verify insufficient matches (< 5) reports INSUFFICIENT_MATCHES with None metrics."""
        n_nodes = len(self.graph.nodes_df)
        pred_dummy = np.full(n_nodes, 5.0, dtype=np.float64)

        # Intentionally use extremely small tolerance 0.1 m where no points match
        res = self.validator.evaluate_predictions(
            predicted_depths_cm=pred_dummy,
            graph=self.graph,
            model_event_date="2015-12-01",
            match_tolerance_m=0.1,
        )
        self.assertEqual(res["status"], "INSUFFICIENT_MATCHES")
        self.assertTrue(res["ground_truth_available"])
        self.assertIsNone(res["mae_cm"])
        self.assertIsNone(res["rmse_cm"])
        self.assertIsNone(res["r2_score"])

    def test_07_unclamped_negative_r2(self):
        """Verify negative R^2 is preserved exactly and not clamped to [0, 1]."""
        n_nodes = len(self.graph.nodes_df)
        # Predictions that are far from the actual observations
        pred_low = np.full(n_nodes, 1.0, dtype=np.float64)

        res = self.validator.evaluate_predictions(
            predicted_depths_cm=pred_low,
            graph=self.graph,
            model_event_date="2015-12-01",
            match_tolerance_m=500.0,
        )
        self.assertEqual(res["status"], "VALIDATED")
        self.assertIsNotNone(res["r2_score"])
        # With mean observed ~ 140cm and prediction 1cm, R^2 is negative
        self.assertLess(res["r2_score"], 0.0)
        self.assertIsInstance(res["r2_score"], float)

    def test_08_source_composition_reporting(self):
        """Verify matched source composition is tracked."""
        n_nodes = len(self.graph.nodes_df)
        pred_dummy = np.full(n_nodes, 5.0, dtype=np.float64)
        res = self.validator.evaluate_predictions(
            predicted_depths_cm=pred_dummy,
            graph=self.graph,
            model_event_date="2015-12-01",
            match_tolerance_m=500.0,
        )
        srcs = res.get("matched_source_composition")
        self.assertIsInstance(srcs, dict)
        self.assertEqual(sum(srcs.values()), res["matched_benchmark_points"])


if __name__ == "__main__":
    unittest.main()
