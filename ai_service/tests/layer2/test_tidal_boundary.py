"""Unit tests for Layer 2 Tidal Boundary Module (Bay of Bengal Harmonics & Outfall Throttling)."""

import math
import unittest

from ai_service.layer2.drainage_graph import TidalBoundaryEngine


class TestTidalBoundaryEngine(unittest.TestCase):
    """Test suite for Bay of Bengal astronomical semi-diurnal tides and outfall backwater throttling."""

    def setUp(self):
        self.engine = TidalBoundaryEngine(datum_msl_m=0.0)

    def test_01_astronomical_harmonics_amplitudes(self):
        """Verify M2 (0.42m) and S2 (0.18m) harmonic parameters for Chennai Port."""
        self.assertAlmostEqual(self.engine.amp_m2, 0.42)
        self.assertAlmostEqual(self.engine.amp_s2, 0.18)
        self.assertAlmostEqual(self.engine.period_m2_hr, 12.4206, places=3)
        self.assertAlmostEqual(self.engine.period_s2_hr, 12.0000, places=3)

        # High tide at t=0: both cosines = 1.0 -> 0.42 + 0.18 = 0.60m MSL
        h_t0 = self.engine.compute_tidal_stage_m(t_hours=0.0, storm_surge_m=0.0)
        self.assertAlmostEqual(h_t0, 0.60, places=3)

    def test_02_cyclonic_storm_surge_offset(self):
        """Storm surge offset (e.g. Cyclone Michaung 0.35m) must add directly to water stage."""
        h_astro = self.engine.compute_tidal_stage_m(t_hours=3.0, storm_surge_m=0.0)
        h_surge = self.engine.compute_tidal_stage_m(t_hours=3.0, storm_surge_m=0.35)
        self.assertAlmostEqual(h_surge - h_astro, 0.35, places=4)

    def test_03_free_gravity_outfall_discharge(self):
        """When tide stage is below outfall invert, no backwater throttling occurs (factor = 1.0)."""
        # Invert at 2.5m MSL, tide at 0.5m MSL
        throttle = self.engine.compute_outfall_throttle_factor(invert_elev_m=2.5, tidal_stage_m=0.5)
        self.assertEqual(throttle, 1.0)

    def test_04_submerged_outfall_backwater_throttling(self):
        """When tide stage rises above outfall invert, capacity is throttled (factor < 1.0)."""
        # Invert at 0.5m MSL, tide at 1.2m MSL (0.7m submergence)
        throttle = self.engine.compute_outfall_throttle_factor(invert_elev_m=0.5, tidal_stage_m=1.2)
        self.assertLess(throttle, 1.0)
        self.assertGreaterEqual(throttle, 0.15)

    def test_05_severe_submergence_minimum_bound(self):
        """Extreme coastal storm surge cannot throttle below physical minimum (0.15)."""
        throttle = self.engine.compute_outfall_throttle_factor(invert_elev_m=0.0, tidal_stage_m=5.0)
        self.assertAlmostEqual(throttle, 0.15, places=4)


if __name__ == "__main__":
    unittest.main()
