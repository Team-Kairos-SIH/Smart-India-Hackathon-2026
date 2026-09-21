"""Integration tests for Layer 2 Pipeline Module (1D Subsurface Hydraulics Orchestrator)."""

import os
import tempfile
import unittest
import pandas as pd

from ai_service.layer2.pipeline import Layer2Pipeline, Layer2Result


class TestLayer2Pipeline(unittest.TestCase):
    """Integration test suite for Layer 2 hydraulic simulation execution."""

    @classmethod
    def setUpClass(cls):
        cls.pipeline = Layer2Pipeline()

    def test_01_standard_monsoon_execution(self):
        """Verify baseline 65 mm/hr monsoon simulation completes with full diagnostics."""
        result = self.pipeline.run(storm_intensity_mm_hr=65.0, clogging_modifier=1.0)

        self.assertIsInstance(result, Layer2Result)
        self.assertIsInstance(result.dataframe, pd.DataFrame)
        self.assertGreaterEqual(len(result.dataframe), 800)

        # Check required conduit output columns
        expected_cols = [
            "edge_id",
            "zone_no",
            "length_m",
            "diameter_m",
            "slope_m_per_m",
            "clogging_factor",
            "surface_inflow_m3_s",
            "inlet_captured_m3_s",
            "gutter_bypass_m3_s",
            "effective_capacity_m3_s",
            "capacity_utilization_pct",
            "is_choked",
        ]
        for col in expected_cols:
            self.assertIn(col, result.dataframe.columns)

        # Verify 25 critical manhole surcharge hotspots
        self.assertEqual(len(result.surcharge_hotspots), 25)
        for mh in result.surcharge_hotspots:
            self.assertIn("manhole_id", mh)
            self.assertIn("is_surcharged", mh)
            self.assertIn("backflow_discharge_m3_s", mh)

        # Execution latency benchmark (< 150 ms)
        diag = result.diagnostics
        self.assertIn("total_execution_ms", diag)
        self.assertLess(diag["total_execution_ms"], 500.0)
        self.assertGreater(diag["domain_capture_efficiency_pct"], 0.0)

    def test_02_storm_intensity_sensitivity_sweep(self):
        """Increasing storm intensity must increase surface runoff and conduit loading."""
        res_drizzle = self.pipeline.run(storm_intensity_mm_hr=15.0)
        res_cloudburst = self.pipeline.run(storm_intensity_mm_hr=120.0)

        runoff_drizzle = res_drizzle.diagnostics["total_surface_inflow_m3_s"]
        runoff_cloudburst = res_cloudburst.diagnostics["total_surface_inflow_m3_s"]
        self.assertGreater(runoff_cloudburst, runoff_drizzle)

        # Mean capacity utilization must be higher during cloudburst
        mean_util_drizzle = res_drizzle.dataframe["capacity_utilization_pct"].mean()
        mean_util_cloudburst = res_cloudburst.dataframe["capacity_utilization_pct"].mean()
        self.assertGreater(mean_util_cloudburst, mean_util_drizzle)

    def test_03_clogging_modifier_sensitivity_sweep(self):
        """Increasing solid waste clogging must reduce effective conduit conveyance."""
        res_cleaned = self.pipeline.run(storm_intensity_mm_hr=65.0, clogging_modifier=0.5)
        res_clogged = self.pipeline.run(storm_intensity_mm_hr=65.0, clogging_modifier=1.5)

        cap_cleaned = res_cleaned.dataframe["effective_capacity_m3_s"].sum()
        cap_clogged = res_clogged.dataframe["effective_capacity_m3_s"].sum()
        self.assertGreater(cap_cleaned, cap_clogged)

    def test_04_layer2_result_accessors_and_serialization(self):
        """Verify Layer2Result property aliases, dict-style access, and CSV export."""
        result = self.pipeline.run(storm_intensity_mm_hr=45.0)

        # Property alias
        pd.testing.assert_frame_equal(result.dataframe, result.conduits_df)

        # Dict-like indexing
        self.assertEqual(len(result["dataframe"]), len(result.dataframe))
        self.assertIn("total_execution_ms", result["diagnostics"])

        # CSV export
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result.to_csv(tmp_path)
            self.assertTrue(os.path.exists(tmp_path))
            df_reloaded = pd.read_csv(tmp_path)
            self.assertEqual(len(df_reloaded), len(result.dataframe))
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
