"""Unit and integration tests for Layer 2 -> Layer 3 coupling.

Verifies:
  1. Layer2Result structure & conduit backflow conversion (from_layer2_backflow).
  2. Exact node count matching (7,894 road nodes).
  3. All six forecast horizons present (T+15m to T+180m).
  4. Physical non-negativity and finite numerical bounds for backflow vectors.
  5. Strict volumetric mass conservation in mapping: sum(Q_node_bf) == sum(Q_conduit_bf).
  6. Non-broadcasting of 25 benchmark manhole hotspots across the 7,894-node graph.
  7. Physical sparsity: non-surcharging conduits produce zero backflow on connected roads.
  8. Backflow impact on street depth: d(Q_surf + Q_backflow) >= d(Q_surf).
  9. Analytical volumetric mass conservation with backflow (0.000000% error target).
  10. Multi-horizon depth monotonicity across T+15m ... T+180m.
  11. Sub-second CPU latency (< 350 ms budget).
  12. attach_layer2_backflow() dataframe enrichment with backflow_rate_m3_s & is_surcharging.
  13. Layer3Pipeline end-to-end execution with automated Layer 1 & Layer 2 coupling.
  14. Robust error handling on missing required columns or NaN backflow values.
  15. Real drainage network loading (825 conduits) without synthetic fallback.
"""

import time
import unittest
import numpy as np
import pandas as pd

from ai_service.layer3.graph_builder import StreetDrainageGraph
from ai_service.layer3.surrogate_model import PhysicsInformedGraphSurrogate, HORIZONS_MIN
from ai_service.layer3.mass_conservation_loss import MassConservationConstraint
from ai_service.layer3.coupling import (
    from_layer1_runoff,
    from_layer2_backflow,
    attach_layer2_backflow,
    Layer3Inputs,
)
from ai_service.layer3.pipeline import Layer3Pipeline
from ai_service.layer1.lulc.runoff_generator import SurfaceRunoffGenerator
from ai_service.layer2.pipeline import Layer2Pipeline, Layer2Result
from ai_service.layer2.drainage_graph import DrainageGraphNetwork


class TestLayer2Layer3Coupling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = StreetDrainageGraph()
        cls.surrogate = PhysicsInformedGraphSurrogate()
        cls.l1_gen = SurfaceRunoffGenerator()
        cls.l2_pipe = Layer2Pipeline()

        # 1. Compute upstream Layer 1 runoff (49.8 mm/hr peak cloudburst)
        cls.l1_runoff = cls.l1_gen.compute_runoff(
            roads_df=cls.graph.nodes_df,
            rainfall_intensity=49.8,
            amc="AMC_III",
            scenario="2015_flood",
        )
        cls.l3_inputs = from_layer1_runoff(cls.l1_runoff, cls.graph)

        # 2. Compute upstream Layer 2 conduit hydraulics using real Layer 1 runoff
        cls.l2_res = cls.l2_pipe.run(
            storm_intensity_mm_hr=49.8,
            clogging_modifier=1.0,
            layer1_runoff=cls.l1_runoff,
        )

        # 3. Convert conduit backflow to Layer 3 street node vectors
        cls.bf_vectors = from_layer2_backflow(cls.l2_res, cls.graph)

    def test_01_layer2_result_structure(self):
        """Layer 2 execution must produce valid conduit dataframe and 25 hotspots."""
        self.assertIsInstance(self.l2_res, Layer2Result)
        df_c = self.l2_res.dataframe
        self.assertIsInstance(df_c, pd.DataFrame)
        self.assertEqual(len(df_c), 825)
        self.assertIn("backflow_discharge_m3_s", df_c.columns)
        self.assertIn("drain_id", df_c.columns)
        self.assertIn("is_surcharged", df_c.columns)
        self.assertEqual(len(self.l2_res.surcharge_hotspots), 25)

    def test_02_real_drainage_network_loaded(self):
        """Drainage network graph must load real 825 conduits without fallback."""
        net = DrainageGraphNetwork()
        self.assertEqual(len(net.edges), 825)
        self.assertTrue(all("way/" in e.get("drain_id", "") or "DRN_" in e.get("edge_id", "") for e in net.edges))

    def test_03_from_layer2_backflow_shape_and_horizons(self):
        """from_layer2_backflow must return 7,894-element vectors for all 6 horizons."""
        self.assertEqual(len(self.bf_vectors), len(HORIZONS_MIN))
        for h in HORIZONS_MIN:
            self.assertIn(h, self.bf_vectors)
            vec = self.bf_vectors[h]
            self.assertEqual(len(vec), 7894)
            self.assertFalse(np.isnan(vec).any())
            self.assertTrue(np.all(vec >= 0.0))

    def test_04_strict_volumetric_conservation_in_mapping(self):
        """Total conduit backflow must equal total node backflow exactly."""
        tot_conduit_bf = float(self.l2_res.dataframe["backflow_discharge_m3_s"].sum())
        tot_node_bf = float(self.bf_vectors[60].sum())
        self.assertGreater(tot_conduit_bf, 0.0)
        self.assertAlmostEqual(tot_conduit_bf, tot_node_bf, places=4)

    def test_05_no_hotspot_broadcasting(self):
        """The 25 benchmark manhole hotspots must NOT be broadcast across the 7,894 nodes."""
        node_bf = self.bf_vectors[60]
        # Benchmark hotspot IDs are MH_HOTSPOT_01 .. MH_HOTSPOT_25
        hotspot_ids = [h["manhole_id"] for h in self.l2_res.surcharge_hotspots]
        self.assertEqual(len(hotspot_ids), 25)

        # Ensure node backflow values are NOT identical constants repeated 7894 times
        unique_bf_vals = np.unique(node_bf)
        self.assertGreater(len(unique_bf_vals), 50)
        # Surcharging nodes should be distinct from the 25 benchmark manhole points
        self.assertNotEqual(len(unique_bf_vals), 25)
        # There should be nodes without backflow (not uniformly applied)
        zero_bf_nodes = int(np.count_nonzero(node_bf == 0.0))
        self.assertGreater(zero_bf_nodes, 100)

    def test_06_physical_backflow_impact_on_street_depth(self):
        """Coupling backflow must increase domain street depths compared to surface runoff alone."""
        # Baseline: surface runoff alone
        res_no_bf = self.surrogate.predict_multi_horizon(
            rain_vectors=self.l3_inputs.runoff_vectors,
            clogging_modifier=0.35,
            is_runoff_preprocessed=True,
            backflow_vectors=None,
        )

        # Coupled: surface runoff + conduit backflow
        res_with_bf = self.surrogate.predict_multi_horizon(
            rain_vectors=self.l3_inputs.runoff_vectors,
            clogging_modifier=0.35,
            is_runoff_preprocessed=True,
            backflow_vectors=self.bf_vectors,
        )

        depth_no_bf = res_no_bf["horizons"][60]
        depth_with_bf = res_with_bf["horizons"][60]

        # Domain-wide mean and peak depths must strictly increase due to backflow injection
        self.assertGreater(float(np.mean(depth_with_bf)), float(np.mean(depth_no_bf)))
        self.assertGreater(float(np.max(depth_with_bf)), float(np.max(depth_no_bf)))

        # Surcharging road nodes must show significant depth increase
        surcharging_nodes = self.bf_vectors[60] > 0.0
        self.assertGreater(int(np.count_nonzero(surcharging_nodes)), 0)
        mean_surch_with_bf = float(np.mean(depth_with_bf[surcharging_nodes]))
        mean_surch_no_bf = float(np.mean(depth_no_bf[surcharging_nodes]))
        self.assertGreater(mean_surch_with_bf, mean_surch_no_bf)

    def test_07_analytical_mass_conservation_with_backflow(self):
        """Volumetric continuity with backflow must achieve 0.000000% error target."""
        loss_fn = MassConservationConstraint()
        res_coupled = self.surrogate.predict_multi_horizon(
            rain_vectors=self.l3_inputs.runoff_vectors,
            clogging_modifier=0.35,
            is_runoff_preprocessed=True,
            backflow_vectors=self.bf_vectors,
        )

        for h in HORIZONS_MIN:
            m = res_coupled["metrics"][f"T+{h}m"]
            self.assertAlmostEqual(m["mass_error_pct"], 0.0, places=5)
            self.assertAlmostEqual(m["vol_discrepancy_m3"], 0.0, places=4)
            self.assertTrue(m["mass_conserved"])

    def test_08_multi_horizon_depth_monotonicity(self):
        """Street water depth must be monotonically non-decreasing over storm duration."""
        res_coupled = self.surrogate.predict_multi_horizon(
            rain_vectors=self.l3_inputs.runoff_vectors,
            clogging_modifier=0.35,
            is_runoff_preprocessed=True,
            backflow_vectors=self.bf_vectors,
        )
        horizons = [15, 30, 60, 90, 120, 180]
        for i in range(len(horizons) - 1):
            h_curr = horizons[i]
            h_next = horizons[i + 1]
            d_curr = res_coupled["horizons"][h_curr]
            d_next = res_coupled["horizons"][h_next]
            # Mean and max depths must grow with accumulated rainfall & backflow
            self.assertGreaterEqual(float(np.mean(d_next)), float(np.mean(d_curr)))
            self.assertGreaterEqual(float(np.max(d_next)), float(np.max(d_curr)))

    def test_09_subsecond_cpu_latency_budget(self):
        """Coupled surrogate inference across all 6 horizons must execute in < 350 ms."""
        t0 = time.perf_counter()
        _ = self.surrogate.predict_multi_horizon(
            rain_vectors=self.l3_inputs.runoff_vectors,
            clogging_modifier=0.35,
            is_runoff_preprocessed=True,
            backflow_vectors=self.bf_vectors,
        )
        inf_ms = (time.perf_counter() - t0) * 1000.0
        self.assertLess(inf_ms, 350.0)

    def test_10_attach_layer2_backflow_dataframe(self):
        """attach_layer2_backflow must add backflow_rate_m3_s and is_surcharging to DataFrame."""
        df_roads = self.graph.nodes_df.copy()
        enriched = attach_layer2_backflow(df_roads, self.l2_res, self.graph)
        self.assertIn("backflow_rate_m3_s", enriched.columns)
        self.assertIn("is_surcharging", enriched.columns)
        self.assertEqual(len(enriched), 7894)
        self.assertFalse(enriched["backflow_rate_m3_s"].isna().any())
        self.assertTrue(enriched["is_surcharging"].dtype == bool or enriched["is_surcharging"].dtype == np.bool_)

    def test_11_layer3_pipeline_end_to_end_coupling(self):
        """Layer3Pipeline must run end-to-end with automated Layer 1 & Layer 2 coupling."""
        pipe = Layer3Pipeline()
        result = pipe.run(
            scenario="2015_flood",
            clogging_factor=0.35,
            use_layer1_coupling=True,
            use_layer2_coupling=True,
        )
        self.assertEqual(len(result.dataframe), 7894)
        self.assertEqual(result.diagnostics["layer2_coupling"], "layer2_coupled")
        self.assertTrue(result.diagnostics["backflow_active"])
        self.assertEqual(result.diagnostics["upstream_forcing"], "layer1")
        self.assertTrue(result.diagnostics["subsecond_benchmark_passed"])

    def test_12_error_handling_invalid_conduit_dataframe(self):
        """from_layer2_backflow must raise ValueError on missing column or NaN values."""
        bad_df = pd.DataFrame({"drain_id": ["way/123", "way/456"], "wrong_column": [1.0, 2.0]})
        with self.assertRaises(ValueError):
            from_layer2_backflow(bad_df, self.graph)

        nan_df = pd.DataFrame({
            "drain_id": ["way/123", "way/456"],
            "backflow_discharge_m3_s": [1.0, np.nan],
        })
        with self.assertRaises(ValueError):
            from_layer2_backflow(nan_df, self.graph)


if __name__ == "__main__":
    unittest.main()
