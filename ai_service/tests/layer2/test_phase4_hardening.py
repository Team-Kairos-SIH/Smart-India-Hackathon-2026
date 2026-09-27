"""Layer 2 Phase 4 Hardening & Validation Test Suite (Real Chennai Stormwater Network).

Covers:
  1. Full Hydraulic Stress Testing across Rainfall Sweep (10, 25, 50, 65, 100 mm/hr).
  2. Dynamic Municipal Solid-Waste Clogging Stress Sweep (0.5, 1.0, 1.5, 2.0).
  3. Extreme Monsoon Cloudburst Scenario (100 mm/hr).
  4. Bay of Bengal Tidal & Cyclonic Storm-Surge Throttling.
  5. Mass-Balance & Ingress Continuity (Q_surf = Q_captured + Q_bypass).
  6. Comprehensive Physical & Hydraulic Sanity Invariants.
  7. Real-Data Provenance & Lineage Audit.
  8. Synthetic Mock Elimination & Zero-CMWSSB Contamination Verification.
  9. Real OSM Manhole Inspection Point Integrity.
"""

import math
import unittest
import numpy as np
import pandas as pd

from ai_service.layer2.pipeline import Layer2Pipeline, Layer2Result


class TestLayer2Phase4Hardening(unittest.TestCase):
    """Rigorous Phase 4 stress-testing and production hardening test suite."""

    @classmethod
    def setUpClass(cls):
        cls.pipeline = Layer2Pipeline()

    def test_01_rainfall_intensity_sweep(self):
        """Rainfall intensity sweep (10, 25, 50, 65, 100 mm/hr) must show monotonic physical response."""
        intensities = [10.0, 25.0, 50.0, 65.0, 100.0]
        results = [self.pipeline.run(storm_intensity_mm_hr=i) for i in intensities]

        inflows = [r.diagnostics["total_surface_inflow_m3_s"] for r in results]
        captured = [r.diagnostics["total_captured_drainage_m3_s"] for r in results]
        mean_utils = [r.dataframe["capacity_utilization_pct"].mean() for r in results]
        choked_counts = [r.diagnostics["choked_conduit_count"] for r in results]

        # Monotonicity checks
        for idx in range(len(intensities) - 1):
            self.assertLess(inflows[idx], inflows[idx + 1], "Surface runoff must strictly increase with rainfall")
            self.assertLessEqual(captured[idx], captured[idx + 1], "Captured inflow must be non-decreasing")
            self.assertLess(mean_utils[idx], mean_utils[idx + 1], "Capacity utilization must strictly increase")
            self.assertLessEqual(choked_counts[idx], choked_counts[idx + 1], "Choked conduits must be non-decreasing")

    def test_02_clogging_stress_sweep(self):
        """Clogging modifier sweep (0.5, 1.0, 1.5, 2.0) must reduce effective capacity and respect [0.05, 0.85]."""
        modifiers = [0.5, 1.0, 1.5, 2.0]
        results = [self.pipeline.run(storm_intensity_mm_hr=65.0, clogging_modifier=m) for m in modifiers]

        eff_capacities = [r.dataframe["effective_capacity_m3_s"].sum() for r in results]
        mean_mus = [r.diagnostics["mean_clogging_factor"] for r in results]

        # Capacity must strictly decrease as clogging increases (until upper clipping limit)
        self.assertGreater(eff_capacities[0], eff_capacities[1])
        self.assertGreater(eff_capacities[1], eff_capacities[2])
        self.assertGreaterEqual(eff_capacities[2], eff_capacities[3])

        for r in results:
            mus = r.dataframe["clogging_factor"]
            self.assertTrue((mus >= 0.05).all(), "All mu_clog must be >= 0.05")
            self.assertTrue((mus <= 0.85).all(), "All mu_clog must be <= 0.85")

    def test_03_extreme_monsoon_cloudburst_scenario(self):
        """100 mm/hr extreme cloudburst model scenario must evaluate full surcharge and backflow."""
        result = self.pipeline.run(storm_intensity_mm_hr=100.0, clogging_modifier=1.0)
        df = result.dataframe
        diag = result.diagnostics

        self.assertEqual(len(df), 567)
        self.assertGreater(diag["total_surface_inflow_m3_s"], 70.0)
        self.assertGreater(diag["choked_conduit_count"], 0)
        self.assertGreater(diag["surcharging_conduits_count"], 0)
        self.assertGreater(diag["total_backflow_discharge_m3_s"], 0.0)

        # Max surcharge head and finite values
        self.assertTrue(np.isfinite(df["hgl_m"]).all())
        self.assertTrue(np.isfinite(df["head_above_ground_m"]).all())
        self.assertTrue((df["head_above_ground_m"] >= 0.0).all())

    def test_04_coastal_storm_surge_tidal_throttling(self):
        """Severe cyclonic storm surge (4.0m) must throttle coastal outfalls below free gravity discharge."""
        # Baseline surge (0.35m) -> Inverts above tide -> Throttle = 1.0
        res_baseline = self.pipeline.run(storm_surge_m=0.35)
        coastal_base = res_baseline.dataframe[res_baseline.dataframe["is_coastal_outfall"]]
        self.assertEqual(len(coastal_base), 8)
        self.assertTrue((coastal_base["tidal_throttle"] == 1.0).all())

        # Extreme cyclonic surge (4.0m) -> Submerges inverts at 3.24m - 3.30m -> Throttle < 1.0
        res_severe = self.pipeline.run(storm_surge_m=4.0)
        coastal_severe = res_severe.dataframe[res_severe.dataframe["is_coastal_outfall"]]
        self.assertEqual(len(coastal_severe), 8)

        # At least the lowest elevation coastal outfalls (DRN_00005, DRN_00006) must be throttled
        throttled_outfalls = coastal_severe[coastal_severe["tidal_throttle"] < 1.0]
        self.assertGreater(len(throttled_outfalls), 0)
        self.assertLess(throttled_outfalls["tidal_throttle"].min(), 1.0)

        # Capacity after throttling must be less than effective capacity
        q_eff_sum = throttled_outfalls["effective_capacity_m3_s"].sum()
        q_throttled_sum = throttled_outfalls["tidal_throttled_capacity_m3_s"].sum()
        self.assertLess(q_throttled_sum, q_eff_sum)

    def test_05_mass_balance_and_flow_continuity(self):
        """Surface inflow must equal captured flow + gutter bypass within numerical tolerance."""
        result = self.pipeline.run(storm_intensity_mm_hr=65.0)
        df = result.dataframe

        # Continuity: Q_surf == Q_captured + Q_bypass on every conduit
        continuity_diff = np.abs(df["surface_inflow_m3_s"] - (df["inlet_captured_m3_s"] + df["gutter_bypass_m3_s"]))
        self.assertTrue((continuity_diff < 1e-3).all(), "Mass balance violation: Q_surf != Q_captured + Q_bypass")

        # Ingress bound: Q_captured <= Q_surf
        self.assertTrue((df["inlet_captured_m3_s"] <= df["surface_inflow_m3_s"] + 1e-5).all())

    def test_06_hydraulic_sanity_and_invariants(self):
        """Rigorous physical sanity checks across all 567 conduits."""
        result = self.pipeline.run(storm_intensity_mm_hr=65.0)
        df = result.dataframe

        # Geometric & Physical Positivity
        self.assertTrue((df["length_m"] > 0.0).all())
        self.assertTrue((df["diameter_m"] > 0.0).all())
        self.assertTrue((df["slope_m_per_m"] > 0.0).all())
        self.assertTrue((df["effective_capacity_m3_s"] > 0.0).all())
        self.assertTrue((df["nominal_capacity_m3_s"] >= df["effective_capacity_m3_s"]).all())
        self.assertTrue((df["effective_capacity_m3_s"] >= df["tidal_throttled_capacity_m3_s"]).all())
        self.assertTrue((df["gutter_bypass_m3_s"] >= 0.0).all())
        self.assertTrue((df["backflow_discharge_m3_s"] >= 0.0).all())

        # No NaNs in critical columns
        critical_cols = [
            "length_m", "diameter_m", "slope_m_per_m", "z_ground_m", "clogging_factor",
            "nominal_capacity_m3_s", "effective_capacity_m3_s", "surface_inflow_m3_s",
            "inlet_captured_m3_s", "gutter_bypass_m3_s", "hgl_m", "backflow_discharge_m3_s"
        ]
        for c in critical_cols:
            self.assertFalse(df[c].isnull().any(), f"NaN found in critical column {c}")

    def test_07_real_data_provenance_audit(self):
        """All provenance tags must accurately identify real data sources and engineering proxies."""
        result = self.pipeline.run(storm_intensity_mm_hr=65.0)
        sample = result.dataframe.iloc[0]
        prov = sample["provenance"]

        self.assertIn("DERIVED_FROM_REAL_GEOMETRY", prov["length"])
        self.assertIn("DERIVED_FROM_REAL_DEM", prov["ground_elevation"])
        self.assertIn("PROXY", prov["terrain_slope"])
        self.assertIn("NOT_SURVEYED", prov["pipe_bed_slope"])
        self.assertIn("ASSUMED", prov["invert_elevation"])
        self.assertEqual(prov["clogging"], "REAL_GCC_DATA")
        self.assertIn("PROXY_REAL_ROAD_HIERARCHY", prov["catchment_area"])
        self.assertIn("ENGINEERING_PROXY", prov["runoff_coefficient"])
        self.assertIn("ENGINEERING_PROXY", prov["inlet_spacing"])

    def test_08_no_synthetic_hotspot_regression(self):
        """Confirm synthetic 25-hotspot mock and artificial IDs are completely absent."""
        result = self.pipeline.run(storm_intensity_mm_hr=65.0)
        hotspots = result.surcharge_hotspots

        self.assertEqual(len(hotspots), 33, "Hotspots must reflect exactly the 33 real OSM manholes")
        for mh in hotspots:
            self.assertFalse(mh["manhole_id"].startswith("MH_HOTSPOT"))
            self.assertEqual(mh["feature_type"], "OSM_INSPECTION_MANHOLE")

    def test_09_waterway_classification_integrity(self):
        """Conduits must be strictly drain or ditch; receiving channels must be segregated."""
        result = self.pipeline.run(storm_intensity_mm_hr=65.0)
        df = result.dataframe

        # Conduits
        self.assertTrue(set(df["waterway"].unique()).issubset({"drain", "ditch"}))
        self.assertNotIn("canal", df["waterway"].unique())
        self.assertNotIn("stream", df["waterway"].unique())
        self.assertNotIn("river", df["waterway"].unique())

        # Receiving reaches segregated
        self.assertEqual(len(self.pipeline.graph_network.receiving_channels), 204)

    def test_10_manhole_honest_unresolved_handling(self):
        """33 OSM manholes outside the association radius must be marked UNRESOLVED_DISCONNECTED."""
        result = self.pipeline.run(storm_intensity_mm_hr=65.0)
        diag = result.diagnostics

        self.assertEqual(diag["real_manholes_evaluated"], 33)
        self.assertEqual(diag["unresolved_manholes_count"], 33)
        self.assertEqual(diag["resolved_manholes_count"], 0)

        for mh in result.surcharge_hotspots:
            self.assertEqual(mh["association_status"], "UNRESOLVED_DISCONNECTED")
            self.assertIsNone(mh["associated_edge_id"])


if __name__ == "__main__":
    unittest.main()
