"""
Unit & Integration Tests for Master 5-Layer Digital Twin Orchestrator.
"""

import unittest
import numpy as np

from ai_service.orchestration.master_coupler import MasterTwinCoupler, MasterTwinResult


class TestMasterTwinCoupler(unittest.TestCase):
    """Test suite for 5-layer coupled execution."""

    @classmethod
    def setUpClass(cls):
        cls.coupler = MasterTwinCoupler()

    def test_01_coupler_initialization(self):
        """Verify all 5 layers are loaded cleanly."""
        self.assertIsNotNone(self.coupler.l0_pipeline)
        self.assertIsNotNone(self.coupler.runoff_gen)
        self.assertIsNotNone(self.coupler.l2_pipeline)
        self.assertIsNotNone(self.coupler.l3_pipeline)
        self.assertIsNotNone(self.coupler.pump_optimizer)

    def test_02_full_twin_run_michaung(self):
        """Verify 5-layer execution on Michaung storm scenario."""
        res = self.coupler.run_full_twin(
            scenario="michaung",
            clogging_factor=0.35,
            tidal_surge_m=0.85
        )
        self.assertIsInstance(res, MasterTwinResult)
        self.assertEqual(len(res.dataframe), 7894)

        # Check required columns from all layers
        df = res.dataframe
        for col in [
            "depth_T+60m_cm",
            "flow_velocity_m_s",
            "corridor_discharge_m3_s",
            "hazard_vx_d_m2_s",
            "washaway_hazard_tier",
            "is_street_channel"
        ]:
            self.assertIn(col, df.columns)

        kpis = res.to_kpi_summary()
        self.assertEqual(kpis["status"], "success")
        self.assertEqual(kpis["active_road_segments"], 7894)
        self.assertGreater(kpis["peak_depth_t60_cm"], 20.0)
        self.assertGreater(len(res.pump_recommendations), 0)


if __name__ == "__main__":
    unittest.main()
