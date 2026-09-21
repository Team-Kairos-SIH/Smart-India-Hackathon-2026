"""Unit tests for Layer 2 Conduit Flow Module (Manning Circular & Box Culvert Hydraulics)."""

import math
import unittest

from ai_service.layer2.conduit_flow import ConduitFlowEngine


class TestConduitFlowEngine(unittest.TestCase):
    """Test suite for Manning 1D subsurface conveyance calculations."""

    def setUp(self):
        self.engine = ConduitFlowEngine()

    def test_01_circular_pipe_clean_conveyance(self):
        """Verify analytical clean capacity for circular RCC pipe."""
        dia = 1.20
        slope = 0.0020
        res = self.engine.calculate_circular_pipe(
            diameter_m=dia,
            slope_m_per_m=slope,
            mu_clog=0.0,
            base_n=0.013
        )

        self.assertEqual(res["type"], "circular_rcc")
        self.assertEqual(res["diameter_m"], 1.20)
        self.assertEqual(res["clogging_factor"], 0.0)
        self.assertEqual(res["capacity_loss_pct"], 0.0)

        # Analytical check: A0 = pi * r^2, Rh0 = dia / 4
        a0 = math.pi * ((dia / 2.0) ** 2)
        rh0 = dia / 4.0
        expected_q = (1.0 / 0.013) * a0 * (rh0 ** (2.0 / 3.0)) * math.sqrt(slope)
        self.assertAlmostEqual(res["nominal_capacity_m3_s"], round(expected_q, 3), places=2)
        self.assertAlmostEqual(res["effective_capacity_m3_s"], res["nominal_capacity_m3_s"], places=2)
        self.assertGreater(res["velocity_m_s"], 0.5)

    def test_02_circular_pipe_clogging_degradation(self):
        """Verify dynamic solid waste penalty degrades capacity and increases roughness."""
        dia = 0.90
        slope = 0.0025
        mu = 0.40
        base_n = 0.013

        res = self.engine.calculate_circular_pipe(
            diameter_m=dia,
            slope_m_per_m=slope,
            mu_clog=mu,
            base_n=base_n
        )

        self.assertLess(res["effective_capacity_m3_s"], res["nominal_capacity_m3_s"])
        self.assertGreater(res["capacity_loss_pct"], 50.0)  # > 50% capacity lost under 40% clogging
        self.assertAlmostEqual(res["effective_manning_n"], round(base_n * (1.0 + 1.8 * mu), 4), places=3)

    def test_03_box_culvert_conveyance(self):
        """Verify rectangular box culvert hydraulics for arterial storm drains."""
        w, h = 1.50, 1.20
        slope = 0.0015
        mu = 0.30
        res = self.engine.calculate_box_culvert(
            width_m=w,
            height_m=h,
            slope_m_per_m=slope,
            mu_clog=mu,
            base_n=0.015
        )

        self.assertEqual(res["type"], "box_culvert")
        self.assertEqual(res["width_m"], 1.50)
        self.assertEqual(res["height_m"], 1.20)
        self.assertGreater(res["nominal_capacity_m3_s"], res["effective_capacity_m3_s"])
        self.assertGreater(res["effective_capacity_m3_s"], 0.5)
        self.assertGreater(res["velocity_m_s"], 0.0)

    def test_04_monotonic_scaling(self):
        """Conveyance must scale monotonically with slope and diameter."""
        # Slope monotonicity
        q_low_slope = self.engine.calculate_circular_pipe(1.0, 0.001)["effective_capacity_m3_s"]
        q_high_slope = self.engine.calculate_circular_pipe(1.0, 0.005)["effective_capacity_m3_s"]
        self.assertGreater(q_high_slope, q_low_slope)

        # Diameter monotonicity
        q_small_dia = self.engine.calculate_circular_pipe(0.60, 0.002)["effective_capacity_m3_s"]
        q_large_dia = self.engine.calculate_circular_pipe(1.80, 0.002)["effective_capacity_m3_s"]
        self.assertGreater(q_large_dia, q_small_dia)

    def test_05_clogging_bounds_clipping(self):
        """Clogging index must clip cleanly to [0.0, 0.85]."""
        res_neg = self.engine.calculate_circular_pipe(1.0, 0.002, mu_clog=-0.5)
        self.assertEqual(res_neg["clogging_factor"], 0.0)

        res_excess = self.engine.calculate_circular_pipe(1.0, 0.002, mu_clog=1.5)
        self.assertEqual(res_excess["clogging_factor"], 0.85)

    def test_06_safeguards_on_invalid_inputs(self):
        """Engine should not crash on non-positive or near-zero inputs."""
        res = self.engine.calculate_circular_pipe(diameter_m=-1.0, slope_m_per_m=-0.05)
        self.assertGreater(res["diameter_m"], 0.0)
        self.assertGreater(res["slope_m_per_m"], 0.0)
        self.assertGreater(res["effective_capacity_m3_s"], 0.0)


if __name__ == "__main__":
    unittest.main()
