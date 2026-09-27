"""Integration tests for Layer 2 Pipeline Module (1D Subsurface Hydraulics Orchestrator)."""

import os
import tempfile
import unittest
import numpy as np
import pandas as pd

from ai_service.layer2.pipeline import Layer2Pipeline, Layer2Result


class TestLayer2Pipeline(unittest.TestCase):
    """Integration test suite for Layer 2 hydraulic simulation execution on real Chennai data."""

    @classmethod
    def setUpClass(cls):
        cls.pipeline = Layer2Pipeline()

    def test_01_real_conduit_simulation_and_output_schema(self):
        """Verify baseline 65 mm/hr simulation on real Chennai drainage graph."""
        result = self.pipeline.run(storm_intensity_mm_hr=65.0, clogging_modifier=1.0)

        self.assertIsInstance(result, Layer2Result)
        self.assertIsInstance(result.dataframe, pd.DataFrame)
        df = result.dataframe

        # 1. Real conduit count verification
        self.assertGreater(len(df), 0)
        self.assertEqual(len(df), len(self.pipeline.graph_network.edges))

        # 2. Waterway classification: only real stormwater conduits
        for ww in df["waterway"].unique():
            self.assertIn(ww, ["drain", "ditch"])

        # 3. Output schema completeness
        expected_cols = [
            "edge_id",
            "drain_id",
            "from_node",
            "to_node",
            "waterway",
            "zone_no",
            "length_m",
            "diameter_m",
            "slope_m_per_m",
            "slope_provenance",
            "z_ground_m",
            "ground_elevation_provenance",
            "invert_elevation_m",
            "invert_provenance",
            "clogging_factor",
            "clogging_provenance",
            "nominal_capacity_m3_s",
            "effective_capacity_m3_s",
            "tidal_throttle",
            "tidal_throttled_capacity_m3_s",
            "is_coastal_outfall",
            "surface_inflow_m3_s",
            "inlet_captured_m3_s",
            "gutter_bypass_m3_s",
            "capacity_utilization_pct",
            "is_choked",
            "hgl_m",
            "head_above_ground_m",
            "backflow_discharge_m3_s",
            "is_surcharged",
            "provenance",
        ]
        for col in expected_cols:
            self.assertIn(col, df.columns)

        # 4. Real DEM ground elevation used (not constant 5.0m)
        self.assertFalse((df["z_ground_m"] == 5.0).all())
        self.assertGreater(df["z_ground_m"].std(), 1.0)
        self.assertGreater(df["z_ground_m"].max(), 30.0)

        # 5. Nominal capacity >= effective capacity
        self.assertTrue((df["nominal_capacity_m3_s"] >= df["effective_capacity_m3_s"]).all())

        # 6. Tidal throttling does not increase capacity
        self.assertTrue((df["effective_capacity_m3_s"] >= df["tidal_throttled_capacity_m3_s"]).all())

        # 7. Gutter bypass is non-negative
        self.assertTrue((df["gutter_bypass_m3_s"] >= 0.0).all())

        # 8. Clogging factor satisfies [0.05, 0.85]
        self.assertTrue((df["clogging_factor"] >= 0.05).all())
        self.assertTrue((df["clogging_factor"] <= 0.85).all())

        # 9. Provenance dictionary populated
        sample_prov = df.iloc[0]["provenance"]
        self.assertIsInstance(sample_prov, dict)
        self.assertIn("ground_elevation", sample_prov)
        self.assertIn("clogging", sample_prov)
        self.assertIn("catchment_area", sample_prov)

    def test_02_dynamic_clogging_sensitivity(self):
        """Increasing solid waste clogging must reduce effective conduit conveyance."""
        res_cleaned = self.pipeline.run(storm_intensity_mm_hr=65.0, clogging_modifier=0.5)
        res_clogged = self.pipeline.run(storm_intensity_mm_hr=65.0, clogging_modifier=1.5)

        cap_cleaned = res_cleaned.dataframe["effective_capacity_m3_s"].sum()
        cap_clogged = res_clogged.dataframe["effective_capacity_m3_s"].sum()

        # Dynamic Manning recalculation must cause cleaned network capacity to exceed clogged capacity
        self.assertGreater(cap_cleaned, cap_clogged)
        self.assertGreater(
            res_clogged.diagnostics["mean_clogging_factor"],
            res_cleaned.diagnostics["mean_clogging_factor"]
        )

    def test_03_storm_intensity_sensitivity_sweep(self):
        """Increasing storm intensity must increase surface runoff and conduit loading."""
        res_drizzle = self.pipeline.run(storm_intensity_mm_hr=15.0)
        res_cloudburst = self.pipeline.run(storm_intensity_mm_hr=120.0)

        runoff_drizzle = res_drizzle.diagnostics["total_surface_inflow_m3_s"]
        runoff_cloudburst = res_cloudburst.diagnostics["total_surface_inflow_m3_s"]
        self.assertGreater(runoff_cloudburst, runoff_drizzle)

        mean_util_drizzle = res_drizzle.dataframe["capacity_utilization_pct"].mean()
        mean_util_cloudburst = res_cloudburst.dataframe["capacity_utilization_pct"].mean()
        self.assertGreater(mean_util_cloudburst, mean_util_drizzle)

    def test_04_real_manhole_hotspot_evaluation(self):
        """Verify real OSM inspection manholes are evaluated and synthetic 25 mock is removed."""
        result = self.pipeline.run(storm_intensity_mm_hr=65.0)

        # Real manhole count matches OSM dataset
        self.assertEqual(len(result.surcharge_hotspots), len(self.pipeline.graph_network.manhole_nodes))

        # Synthetic MH_HOTSPOT IDs must be absent
        for mh in result.surcharge_hotspots:
            self.assertFalse(mh["manhole_id"].startswith("MH_HOTSPOT"))
            self.assertEqual(mh["feature_type"], "OSM_INSPECTION_MANHOLE")
            self.assertIn("association_status", mh)
            self.assertIn("provenance", mh)

        diag = result.diagnostics
        self.assertIn("real_manholes_evaluated", diag)
        self.assertIn("resolved_manholes_count", diag)
        self.assertIn("unresolved_manholes_count", diag)
        self.assertEqual(diag["real_manholes_evaluated"], len(result.surcharge_hotspots))

    def test_05_layer1_coupling_integration(self):
        """Coupling with Layer 1 runoff DataFrame aggregates flows by source_drain_id."""
        sample_edge = self.pipeline.graph_network.edges[0]
        drain_id = sample_edge.get("drain_id", sample_edge["edge_id"])

        mock_l1 = pd.DataFrame([
            {
                "segment_id": "ROAD_001",
                "source_drain_id": drain_id,
                "surface_runoff_inflow_m3_s": 0.42,
                "elevation_ground_m": 8.5
            },
            {
                "segment_id": "ROAD_002",
                "source_drain_id": drain_id,
                "surface_runoff_inflow_m3_s": 0.28,
                "elevation_ground_m": 8.7
            }
        ])

        result = self.pipeline.run(storm_intensity_mm_hr=65.0, layer1_runoff=mock_l1)
        self.assertEqual(result.diagnostics["upstream_runoff_source"], "layer1")

        matched_row = result.dataframe[result.dataframe["drain_id"] == drain_id].iloc[0]
        self.assertAlmostEqual(matched_row["surface_inflow_m3_s"], 0.70, places=2)

    def test_06_layer2_result_accessors_and_serialization(self):
        """Verify Layer2Result property aliases, dict-style access, and CSV export."""
        result = self.pipeline.run(storm_intensity_mm_hr=45.0)

        pd.testing.assert_frame_equal(result.dataframe, result.conduits_df)
        self.assertEqual(len(result["dataframe"]), len(result.dataframe))
        self.assertIn("total_execution_ms", result["diagnostics"])

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
