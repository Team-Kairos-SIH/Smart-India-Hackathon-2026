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

    def test_02_real_data_topology_and_classification(self):
        """Validate real Chennai stormwater network topology and conduit classification."""
        self.assertGreater(len(self.network.edges), 0)
        self.assertGreater(len(self.network.nodes), 0)

        # Conduit edges must strictly originate from stormwater features
        for edge in self.network.edges:
            self.assertIn(
                edge.get("waterway"),
                ["drain", "ditch"],
                f"Edge {edge.get('edge_id')} has invalid non-stormwater waterway tag: {edge.get('waterway')}"
            )
            self.assertIn(edge["from_node"], self.network.nodes)
            self.assertIn(edge["to_node"], self.network.nodes)
            self.assertGreater(edge["length_m"], 0.0)
            self.assertIn("drain_id", edge)
            # Confirm real DEM provenance tag is present (not synthetic fallback)
            self.assertIn("DERIVED_FROM_REAL_DEM", edge["provenance"]["ground_elevation"])

        # Receiving channels (canals, streams, rivers) and manhole points must be segregated
        self.assertGreater(len(self.network.receiving_channels), 0)
        self.assertGreater(len(self.network.manhole_nodes), 0)

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
            "provenance",
        ]
        for key in required_keys:
            self.assertIn(key, sample_edge)

        self.assertGreater(sample_edge["length_m"], 0.0)
        self.assertGreater(sample_edge["diameter_m"], 0.0)
        self.assertGreater(sample_edge["effective_capacity_m3_s"], 0.0)
        self.assertLessEqual(sample_edge["effective_capacity_m3_s"], sample_edge["nominal_capacity_m3_s"])

        # Check provenance dictionary tags
        prov = sample_edge["provenance"]
        self.assertIn("ground_elevation", prov)
        self.assertIn("diameter", prov)
        self.assertIn("terrain_slope", prov)
        self.assertIn("pipe_bed_slope", prov)
        self.assertIn("invert_elevation", prov)
        self.assertIn("clogging", prov)

    def test_04_field_override_registry(self):
        """Municipal field engineers can register custom pipe diameters."""
        test_edge = "DRN_99999"
        DrainageGraphNetwork.register_field_override(test_edge, 2.10)
        self.assertEqual(CMWSSB_FIELD_OVERRIDE_REGISTRY[test_edge], 2.10)

    def test_05_network_statistics_computation(self):
        """Summary statistics of the subsurface drainage network must compute accurately from real data."""
        stats = self.network.get_network_statistics()
        self.assertIn("total_conduits", stats)
        self.assertIn("total_network_length_km", stats)
        self.assertIn("total_effective_discharge_m3_s", stats)
        self.assertIn("mean_clogging_loss_pct", stats)

        # 1. Total conduits equals actual production conduit edges count
        self.assertEqual(stats["total_conduits"], len(self.network.edges))
        self.assertGreater(stats["total_conduits"], 0)

        # 2. Total length is positive and matches edge lengths sum
        total_len_calc_km = sum(e["length_m"] for e in self.network.edges) / 1000.0
        self.assertAlmostEqual(stats["total_network_length_km"], round(total_len_calc_km, 2), places=1)
        self.assertGreater(stats["total_network_length_km"], 0.0)

        # 3. Conveyance is non-negative and effective <= nominal
        total_eff_q = sum(e["effective_capacity_m3_s"] for e in self.network.edges)
        total_nom_q = sum(e["nominal_capacity_m3_s"] for e in self.network.edges)
        self.assertGreaterEqual(stats["total_effective_discharge_m3_s"], 0.0)
        self.assertLessEqual(total_eff_q, total_nom_q)

        # 4. Clogging loss percentage is within valid range [0, 100]
        self.assertGreaterEqual(stats["mean_clogging_loss_pct"], 0.0)
        self.assertLessEqual(stats["mean_clogging_loss_pct"], 100.0)

        # 5. Min and max capacity are internally consistent
        if "max_conduit_capacity_m3_s" in stats and "min_conduit_capacity_m3_s" in stats:
            self.assertGreaterEqual(stats["max_conduit_capacity_m3_s"], stats["min_conduit_capacity_m3_s"])
            self.assertGreater(stats["min_conduit_capacity_m3_s"], 0.0)

    def test_06_coastal_outfall_identification(self):
        """Coastal zones (4, 5, 9, 13) must contain throttled coastal outfall conduits."""
        coastal_edges = [e for e in self.network.edges if e.get("is_coastal_outfall")]
        self.assertGreater(len(coastal_edges), 0)
        for ce in coastal_edges:
            self.assertIn(ce["zone_no"], [4, 5, 9, 13])
            self.assertLessEqual(ce["tidal_throttle"], 1.0)


if __name__ == "__main__":
    unittest.main()
