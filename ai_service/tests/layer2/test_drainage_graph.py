"""Unit tests for Layer 2 Drainage Graph Module (Subsurface Multigraph Topology & CPHEEO Norms)."""

import unittest

from ai_service.layer2.drainage_graph import (
    CPHEEO_PIPE_HIERARCHY,
    DrainageGraphNetwork,
    CMWSSB_FIELD_OVERRIDE_REGISTRY,
)


class TestDrainageGraphNetwork(unittest.TestCase):
    """Test suite for 1D subsurface stormwater graph assembly and CPHEEO standards."""

    def setUp(self):
        self.network = DrainageGraphNetwork()

    def test_01_cpheeo_pipe_hierarchy_standards(self):
        """Verify CPHEEO / IRC:SP:50 stormwater pipe diameter hierarchy."""
        self.assertAlmostEqual(CPHEEO_PIPE_HIERARCHY["arterial"], 1.80)
        self.assertAlmostEqual(CPHEEO_PIPE_HIERARCHY["sub_arterial"], 1.20)
        self.assertAlmostEqual(CPHEEO_PIPE_HIERARCHY["collector"], 0.90)
        self.assertAlmostEqual(CPHEEO_PIPE_HIERARCHY["local"], 0.60)

    def test_02_fallback_topology_scale(self):
        """When raw GeoJSON is unavailable, fallback network must contain 825 calibrated conduits."""
        self.assertGreaterEqual(len(self.network.edges), 825)

    def test_03_conduit_edge_attributes_integrity(self):
        """Every conduit edge must contain complete geometric, hydraulic, and civic attributes."""
        sample_edge = self.network.edges[0]
        required_keys = [
            "edge_id",
            "zone_no",
            "length_m",
            "diameter_m",
            "slope_m_per_m",
            "clogging_factor",
            "is_coastal_outfall",
            "tidal_throttle",
            "effective_capacity_m3_s",
            "nominal_capacity_m3_s",
            "capacity_loss_pct",
        ]
        for key in required_keys:
            self.assertIn(key, sample_edge)

        self.assertGreater(sample_edge["length_m"], 0.0)
        self.assertGreater(sample_edge["diameter_m"], 0.0)
        self.assertGreater(sample_edge["effective_capacity_m3_s"], 0.0)
        self.assertLessEqual(sample_edge["effective_capacity_m3_s"], sample_edge["nominal_capacity_m3_s"])

    def test_04_field_override_registry(self):
        """Municipal field engineers can register custom pipe diameters."""
        test_edge = "DRN_99999"
        DrainageGraphNetwork.register_field_override(test_edge, 2.10)
        self.assertEqual(CMWSSB_FIELD_OVERRIDE_REGISTRY[test_edge], 2.10)

    def test_05_network_statistics_computation(self):
        """Summary statistics of the subsurface drainage network must compute accurately."""
        stats = self.network.get_network_statistics()
        self.assertIn("total_conduits", stats)
        self.assertIn("total_network_length_km", stats)
        self.assertIn("total_effective_discharge_m3_s", stats)
        self.assertIn("mean_clogging_loss_pct", stats)

        self.assertGreater(stats["total_conduits"], 800)
        self.assertGreater(stats["total_network_length_km"], 50.0)
        self.assertGreater(stats["total_effective_discharge_m3_s"], 100.0)
        self.assertGreater(stats["mean_clogging_loss_pct"], 20.0)

    def test_06_coastal_outfall_identification(self):
        """Coastal zones (4, 5, 9, 13) must contain throttled coastal outfall conduits."""
        coastal_edges = [e for e in self.network.edges if e.get("is_coastal_outfall")]
        self.assertGreater(len(coastal_edges), 0)
        for ce in coastal_edges:
            self.assertIn(ce["zone_no"], [4, 5, 9, 13])
            self.assertLessEqual(ce["tidal_throttle"], 1.0)


if __name__ == "__main__":
    unittest.main()
