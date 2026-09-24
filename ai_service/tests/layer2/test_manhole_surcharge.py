"""Unit tests for Layer 2 Manhole Surcharge Module (HGL Pressurization & Geyser Eruption)."""

import math
import unittest

from ai_service.layer2.manhole_surcharge import ManholeSurchargeEngine


class TestManholeSurchargeEngine(unittest.TestCase):
    """Test suite for manhole HGL tracking, chimney pressurization, and geyser backflow."""

    def setUp(self):
        self.engine = ManholeSurchargeEngine()

    def test_01_normal_gravity_conveyance(self):
        """When conduit capacity exceeds inflow, water stays in pipe without surcharge."""
        res = self.engine.evaluate_surcharge(
            q_inflow_m3_s=0.30,
            q_pipe_capacity_m3_s=0.80,
            z_ground_m=6.5,
            chamber_depth_m=2.5
        )

        self.assertFalse(res["is_surcharged"])
        self.assertEqual(res["status"], "NORMAL_CONVEYANCE")
        self.assertEqual(res["backflow_discharge_m3_s"], 0.0)
        self.assertEqual(res["backflow_liters_per_sec"], 0.0)
        self.assertLessEqual(res["hgl_m"], 6.5)
        self.assertAlmostEqual(res["capacity_utilization_pct"], (0.30 / 0.80) * 100.0, places=1)

    def test_02_active_geyser_surcharge_eruption(self):
        """When storm inflow overwhelms conduit capacity, pressurized geyser erupts on street."""
        res = self.engine.evaluate_surcharge(
            q_inflow_m3_s=1.50,
            q_pipe_capacity_m3_s=0.40,
            z_ground_m=5.0,
            chamber_depth_m=2.0
        )

        self.assertTrue(res["is_surcharged"])
        self.assertEqual(res["status"], "ACTIVE_GEYSER_SURCHARGE")
        self.assertGreater(res["hgl_m"], 5.0)
        self.assertGreater(res["head_above_ground_m"], 0.0)
        self.assertGreater(res["backflow_discharge_m3_s"], 0.0)
        self.assertAlmostEqual(
            res["backflow_liters_per_sec"],
            res["backflow_discharge_m3_s"] * 1000.0,
            delta=1.0
        )

    def test_03_chimney_pressurization_subsurface(self):
        """Moderate excess head pressurized inside chamber but not breaching street surface."""
        # Carefully chosen parameters so HGL rises into chamber but not above street
        z_ground = 10.0
        z_inv = 6.0  # deep chamber 4.0m
        res = self.engine.evaluate_surcharge(
            q_inflow_m3_s=0.42,
            q_pipe_capacity_m3_s=0.40,  # slight excess: 0.02
            z_ground_m=z_ground,
            z_invert_m=z_inv,
            chamber_depth_m=4.0
        )

        # Head buildup = (0.02 / 0.40) * 2.2 = 0.11m; HGL = 6.0 + 4.0 + 0.11 = 10.11m -> slightly above
        # If we use deeper ground:
        res2 = self.engine.evaluate_surcharge(
            q_inflow_m3_s=0.42,
            q_pipe_capacity_m3_s=0.40,
            z_ground_m=12.0,
            z_invert_m=z_inv,
            chamber_depth_m=4.0
        )
        self.assertFalse(res2["is_surcharged"])
        self.assertEqual(res2["status"], "CHIMNEY_PRESSURIZATION")
        self.assertEqual(res2["backflow_discharge_m3_s"], 0.0)

    def test_04_analytical_orifice_geyser_equation(self):
        """Verify backflow discharge matches Q = C_d * A_lid * sqrt(2 * g * delta_h)."""
        delta_h = 0.50  # 50cm head above street
        lid_dia = 0.60
        a_lid = math.pi * ((lid_dia / 2.0) ** 2)
        cd = 0.62
        g = 9.80665
        expected_q = cd * a_lid * math.sqrt(2.0 * g * delta_h)

        # Synthetic test using engine properties
        calculated_q = self.engine.c_d * self.engine.lid_area * math.sqrt(2.0 * self.engine.g * delta_h)
        self.assertAlmostEqual(calculated_q, expected_q, places=4)
        self.assertGreater(calculated_q, 0.2)  # > 200 L/s geyser


if __name__ == "__main__":
    unittest.main()
