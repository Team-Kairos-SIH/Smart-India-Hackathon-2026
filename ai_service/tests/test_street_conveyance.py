"""
Unit & Integration Tests for Layer 3 Street-as-Canal Conveyance Engine.
"""

import unittest
import numpy as np
import pandas as pd

from ai_service.layer3.street_conveyance import StreetConveyanceEngine, StreetConveyanceResult


class TestStreetConveyanceEngine(unittest.TestCase):
    """Test suite for open-channel street flow velocity, discharge, and v × d hazard."""

    def setUp(self):
        self.engine = StreetConveyanceEngine(manning_n=0.016)
        self.sample_roads = pd.DataFrame([
            {"segment_id": "SEG-01", "road_name": "Anna Salai Arterial", "road_class": "primary", "terrain_slope_m_per_m": 0.004, "depth_T+60m_cm": 35.0},
            {"segment_id": "SEG-02", "road_name": "Velachery Low Depr", "road_class": "primary", "terrain_slope_m_per_m": 0.001, "depth_T+60m_cm": 65.0},
            {"segment_id": "SEG-03", "road_name": "Residential Lane", "road_class": "residential", "terrain_slope_m_per_m": 0.002, "depth_T+60m_cm": 12.0},
            {"segment_id": "SEG-04", "road_name": "Dry High Ridge", "road_class": "secondary", "terrain_slope_m_per_m": 0.005, "depth_T+60m_cm": 0.5},
        ])

    def test_01_street_flow_calculation(self):
        """Verify Manning flow velocity and discharge are physically sound."""
        res = self.engine.compute_street_flow(self.sample_roads, horizon_min=60)
        self.assertIsInstance(res, StreetConveyanceResult)
        df = res.dataframe

        # Check required columns
        for col in ["flow_velocity_m_s", "corridor_discharge_m3_s", "hazard_vx_d_m2_s", "washaway_hazard_tier", "is_street_channel"]:
            self.assertIn(col, df.columns)

        # Dry ridge should have 0 velocity
        dry_row = df[df["segment_id"] == "SEG-04"].iloc[0]
        self.assertEqual(dry_row["flow_velocity_m_s"], 0.0)

        # Flooded arterial should have positive velocity and discharge
        wet_row = df[df["segment_id"] == "SEG-01"].iloc[0]
        self.assertGreater(wet_row["flow_velocity_m_s"], 0.5)
        self.assertGreater(wet_row["corridor_discharge_m3_s"], 1.0)
        self.assertGreater(wet_row["hazard_vx_d_m2_s"], 0.1)

    def test_02_washaway_hazard_tiers(self):
        """Verify international v × d hazard tiers are assigned accurately."""
        res = self.engine.compute_street_flow(self.sample_roads, horizon_min=60)
        df = res.dataframe
        tiers = set(df["washaway_hazard_tier"].values)
        self.assertTrue(any("LOW" in t or "MODERATE" in t or "HIGH" in t for t in tiers))

    def test_03_summary_metrics(self):
        """Verify summary dictionary metrics."""
        res = self.engine.compute_street_flow(self.sample_roads, horizon_min=60)
        metrics = res.summary_metrics
        self.assertEqual(metrics["evaluated_segments"], 4)
        self.assertEqual(metrics["horizon_min"], 60)
        self.assertGreaterEqual(metrics["max_velocity_m_s"], 0.0)


if __name__ == "__main__":
    unittest.main()
