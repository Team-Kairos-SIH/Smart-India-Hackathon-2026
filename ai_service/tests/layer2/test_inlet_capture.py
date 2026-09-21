"""Unit tests for Layer 2 Inlet Capture Module (Drop-Inlet Weir vs Orifice Flow & Bypass)."""

import unittest

from ai_service.layer2.inlet_capture import InletCaptureEngine


class TestInletCaptureEngine(unittest.TestCase):
    """Test suite for curb drop-inlet capture hydraulics and gutter bypass balance."""

    def setUp(self):
        self.engine = InletCaptureEngine()

    def test_01_unsubmerged_weir_regime(self):
        """Shallow curb ponding (h < 0.12m) must operate under weir flow regime."""
        res = self.engine.compute_inlet_capture(
            q_surface_inflow_m3_s=0.25,
            water_depth_at_curb_m=0.06,
            grate_length_m=1.0,
            grate_width_m=0.5,
            debris_blockage_pct=0.10
        )

        self.assertEqual(res["regime"], "UNSUBMERGED_WEIR")
        self.assertGreater(res["q_captured_m3_s"], 0.0)
        self.assertGreaterEqual(res["q_bypass_m3_s"], 0.0)
        self.assertAlmostEqual(
            res["q_captured_m3_s"] + res["q_bypass_m3_s"],
            res["q_surface_m3_s"],
            places=2
        )

    def test_02_submerged_orifice_regime(self):
        """Deep curb ponding (h >= 0.12m) must operate under submerged orifice flow regime."""
        res = self.engine.compute_inlet_capture(
            q_surface_inflow_m3_s=0.60,
            water_depth_at_curb_m=0.20,
            grate_length_m=1.0,
            grate_width_m=0.5,
            debris_blockage_pct=0.15
        )

        self.assertEqual(res["regime"], "SUBMERGED_ORIFICE")
        self.assertGreater(res["q_captured_m3_s"], 0.0)
        self.assertAlmostEqual(
            res["q_captured_m3_s"] + res["q_bypass_m3_s"],
            res["q_surface_m3_s"],
            places=2
        )

    def test_03_strict_mass_conservation(self):
        """Inlet captured flow + gutter bypass flow must strictly equal surface inflow."""
        test_inflows = [0.05, 0.15, 0.35, 0.80, 1.50]
        test_depths = [0.02, 0.08, 0.12, 0.18, 0.35]

        for q_in in test_inflows:
            for h in test_depths:
                res = self.engine.compute_inlet_capture(
                    q_surface_inflow_m3_s=q_in,
                    water_depth_at_curb_m=h,
                    debris_blockage_pct=0.20
                )
                total_accounted = res["q_captured_m3_s"] + res["q_bypass_m3_s"]
                self.assertAlmostEqual(total_accounted, q_in, places=2)

    def test_04_debris_blockage_reduces_capture_efficiency(self):
        """Surface debris on inlet grate bars must degrade capture efficiency."""
        clean = self.engine.compute_inlet_capture(
            q_surface_inflow_m3_s=0.50,
            water_depth_at_curb_m=0.15,
            debris_blockage_pct=0.0
        )
        clogged = self.engine.compute_inlet_capture(
            q_surface_inflow_m3_s=0.50,
            water_depth_at_curb_m=0.15,
            debris_blockage_pct=0.50
        )

        self.assertGreater(clean["capture_efficiency_pct"], clogged["capture_efficiency_pct"])
        self.assertGreater(clogged["q_bypass_m3_s"], clean["q_bypass_m3_s"])

    def test_05_capture_cannot_exceed_surface_inflow(self):
        """Captured discharge must never exceed incoming overland surface runoff."""
        res = self.engine.compute_inlet_capture(
            q_surface_inflow_m3_s=0.02,
            water_depth_at_curb_m=0.10,
            grate_length_m=2.0,
            grate_width_m=1.0
        )
        self.assertLessEqual(res["q_captured_m3_s"], 0.02)
        self.assertAlmostEqual(res["q_bypass_m3_s"], 0.0, places=3)
        self.assertEqual(res["capture_efficiency_pct"], 100.0)


if __name__ == "__main__":
    unittest.main()
