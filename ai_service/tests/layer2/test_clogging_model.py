"""Unit tests for Layer 2 Solid Waste Clogging Model Module."""

import unittest

from ai_service.layer2.clogging_model import (
    DEFAULT_MANNING_ROUGHNESS,
    SolidWasteCloggingModel,
)


class TestSolidWasteCloggingModel(unittest.TestCase):
    """Test suite for municipal solid waste degradation and desilting arrears penalties."""

    def setUp(self):
        self.model = SolidWasteCloggingModel()

    def test_01_default_manning_roughness_constants(self):
        """Verify standard CPHEEO / IS 456 clean Manning roughness values."""
        self.assertIn("rcc_pipe", DEFAULT_MANNING_ROUGHNESS)
        self.assertIn("box_culvert", DEFAULT_MANNING_ROUGHNESS)
        self.assertIn("masonry_open", DEFAULT_MANNING_ROUGHNESS)
        self.assertIn("natural_channel", DEFAULT_MANNING_ROUGHNESS)

        self.assertAlmostEqual(DEFAULT_MANNING_ROUGHNESS["rcc_pipe"], 0.013)
        self.assertAlmostEqual(DEFAULT_MANNING_ROUGHNESS["box_culvert"], 0.015)
        self.assertAlmostEqual(DEFAULT_MANNING_ROUGHNESS["masonry_open"], 0.020)
        self.assertAlmostEqual(DEFAULT_MANNING_ROUGHNESS["natural_channel"], 0.030)

    def test_02_zonal_clogging_factors_exist_for_all_15_zones(self):
        """All 15 GCC municipal zones must have calibrated or baseline clogging factors."""
        for z in range(1, 16):
            mu = self.model.get_zone_clogging_factor(z)
            self.assertGreaterEqual(mu, 0.05)
            self.assertLessEqual(mu, 0.85)

    def test_03_global_clogging_modifier_scaling(self):
        """Verify global modifier scales clogging while respecting clipping boundaries."""
        base_mu = self.model.get_zone_clogging_factor(10, global_modifier=1.0)

        # Scaled down (e.g. post-desilting campaign)
        reduced_mu = self.model.get_zone_clogging_factor(10, global_modifier=0.5)
        self.assertLessEqual(reduced_mu, base_mu)

        # Scaled up (e.g. heavy pre-monsoon littering)
        increased_mu = self.model.get_zone_clogging_factor(10, global_modifier=2.0)
        self.assertGreaterEqual(increased_mu, base_mu)
        self.assertLessEqual(increased_mu, 0.85)

        # Zero modifier clamps to baseline minimum clogging floor (0.05)
        zero_mu = self.model.get_zone_clogging_factor(10, global_modifier=0.0)
        self.assertEqual(zero_mu, 0.05)
        self.assertGreaterEqual(zero_mu, 0.05)
        self.assertLessEqual(zero_mu, 0.85)

    def test_04_conduit_penalties_formulation(self):
        """Verify effective area A_eff = A0*(1-mu) and roughness n_eff = n0*(1+1.8*mu)."""
        nominal_a = 2.0
        nominal_n = 0.015
        mu = 0.35

        a_eff, n_eff = self.model.apply_conduit_penalties(
            nominal_area_m2=nominal_a,
            nominal_manning_n=nominal_n,
            mu_clog=mu
        )

        self.assertAlmostEqual(a_eff, nominal_a * (1.0 - mu), places=3)
        self.assertAlmostEqual(n_eff, nominal_n * (1.0 + 1.8 * mu), places=4)

    def test_05_extreme_clipping_bounds(self):
        """Out-of-bound clogging factors must be clamped to [0.05, 0.85]."""
        a_eff, n_eff = self.model.apply_conduit_penalties(1.0, 0.015, mu_clog=1.5)
        self.assertAlmostEqual(a_eff, 1.0 * (1.0 - 0.85), places=3)
        self.assertAlmostEqual(n_eff, 0.015 * (1.0 + 1.8 * 0.85), places=4)

        a_eff_neg, n_eff_neg = self.model.apply_conduit_penalties(1.0, 0.015, mu_clog=-0.5)
        self.assertAlmostEqual(a_eff_neg, 1.0 * (1.0 - 0.05), places=3)
        self.assertAlmostEqual(n_eff_neg, 0.015 * (1.0 + 1.8 * 0.05), places=4)


if __name__ == "__main__":
    unittest.main()
