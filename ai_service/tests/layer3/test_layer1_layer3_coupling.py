"""Unit and integration tests for Layer 1 -> Layer 3 coupling.

Verifies:
  1. Exact segment count matching (7,894 nodes).
  2. Deterministic segment_id ordering alignment (CHN_SEG_00001 ... CHN_SEG_07894).
  3. Layer3Inputs structure across all six forecast horizons (T+15m ... T+180m).
  4. Physical validity of runoff rates and tributary discharge (no NaN, non-negative).
  5. Bypassing of crude 90% runoff coefficient when is_runoff_preprocessed=True.
  6. Analytical volumetric mass conservation (<= 0.0001% tolerance, 0.000000% target).
  7. Sub-second CPU inference latency budget (< 350 ms, < 30 ms typical).
  8. Multi-horizon inundation depth monotonicity and bounds.
  9. Error detection on mismatched segment counts or scrambled segment IDs.
  10. Extensibility of Layer3Inputs for future Layer 2 conduit backflow coupling.
  11. Layer3Pipeline end-to-end integration with Layer 1 runoff coupling.
"""

import unittest
import numpy as np
import pandas as pd
import time

from ai_service.layer3.graph_builder import StreetDrainageGraph
from ai_service.layer3.surrogate_model import PhysicsInformedGraphSurrogate, HORIZONS_MIN
from ai_service.layer3.coupling import Layer3Inputs, from_layer1_runoff
from ai_service.layer1.lulc.runoff_generator import SurfaceRunoffGenerator, RunoffResult


class TestLayer1Layer3Coupling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = StreetDrainageGraph()
        cls.surrogate = PhysicsInformedGraphSurrogate()
        cls.generator = SurfaceRunoffGenerator()

        # Compute standard Layer 1 runoff under historical 49.8 mm/hr storm event
        cls.l1_runoff = cls.generator.compute_runoff(
            roads_df=cls.graph.nodes_df,
            rainfall_intensity=49.8,
            amc="AMC_III",
            scenario="2015_flood"
        )
        cls.l3_inputs = from_layer1_runoff(cls.l1_runoff, cls.graph)

    def test_01_segment_count_exact_match(self):
        """Layer 1 and Layer 3 must have exactly 7,894 nodes."""
        self.assertEqual(len(self.graph.nodes_df), 7894)
        self.assertEqual(len(self.l1_runoff.runoff_rates_mm_hr), 7894)
        self.assertEqual(len(self.l1_runoff.discharge_m3_s), 7894)
        self.assertEqual(self.l3_inputs.n_nodes, 7894)

    def test_02_deterministic_segment_id_alignment(self):
        """All 7,894 segment IDs must match in exact sequence without permutation."""
        l1_ids = self.l1_runoff.dataframe["segment_id"].values
        l3_ids = self.graph.nodes_df["segment_id"].values
        self.assertTrue(np.array_equal(l1_ids, l3_ids))
        self.assertEqual(l1_ids[0], "CHN_SEG_00001")
        self.assertEqual(l1_ids[-1], "CHN_SEG_07894")
        self.assertTrue(np.array_equal(self.l3_inputs.segment_ids, l3_ids))

    def test_03_layer3_inputs_structure_all_horizons(self):
        """Layer3Inputs must contain valid vectors for all 6 forward horizons."""
        self.assertEqual(self.l3_inputs.source_layer, "layer1")
        self.assertTrue(self.l3_inputs.is_runoff_preprocessed)

        for h in HORIZONS_MIN:
            self.assertIn(h, self.l3_inputs.runoff_vectors)
            self.assertIn(h, self.l3_inputs.discharge_vectors)
            r_vec = self.l3_inputs.runoff_vectors[h]
            q_vec = self.l3_inputs.discharge_vectors[h]
            self.assertEqual(len(r_vec), 7894)
            self.assertEqual(len(q_vec), 7894)
            self.assertFalse(np.isnan(r_vec).any())
            self.assertFalse(np.isnan(q_vec).any())
            self.assertTrue(np.all(r_vec >= 0.0))
            self.assertTrue(np.all(q_vec >= 0.0))

    def test_04_bypass_crude_runoff_abstraction(self):
        """Surrogate with is_runoff_preprocessed=True must NOT apply crude 10% abstraction."""
        # For a known constant runoff rate:
        test_rate = 50.0
        test_vectors = {h: np.full(7894, test_rate, dtype=np.float32) for h in HORIZONS_MIN}

        # Run with is_runoff_preprocessed=True (L1 mode)
        res_preprocessed = self.surrogate.predict_multi_horizon(
            rain_vectors=test_vectors,
            is_runoff_preprocessed=True
        )

        # Run with is_runoff_preprocessed=False (raw rain mode, applies c_runoff=0.90)
        res_raw_rain = self.surrogate.predict_multi_horizon(
            rain_vectors=test_vectors,
            is_runoff_preprocessed=False
        )

        # Preprocessed (100% runoff) depth must be strictly greater than raw rain (90% runoff) depth
        depth_prep = res_preprocessed["horizons"][60]
        depth_raw = res_raw_rain["horizons"][60]
        self.assertTrue(np.all(depth_prep >= depth_raw))
        self.assertGreater(float(np.mean(depth_prep)), float(np.mean(depth_raw)))

    def test_05_analytical_mass_conservation_with_l1_coupling(self):
        """Analytical mass conservation must hold with zero discrepancy (<= 0.0001% error)."""
        res = self.surrogate.predict_multi_horizon(
            rain_vectors=self.l3_inputs.runoff_vectors,
            is_runoff_preprocessed=self.l3_inputs.is_runoff_preprocessed,
            clogging_modifier=0.35
        )
        for h in HORIZONS_MIN:
            m = res["metrics"][f"T+{h}m"]
            self.assertTrue(m["mass_conserved"])
            self.assertLessEqual(m["mass_error_pct"], 0.0001)
            self.assertAlmostEqual(m["mass_error_pct"], 0.0, places=5)

    def test_06_cpu_inference_latency_within_budget(self):
        """Surrogate inference latency must be well under 350 ms CPU budget."""
        times = []
        for _ in range(10):
            t0 = time.perf_counter()
            _ = self.surrogate.predict_multi_horizon(
                rain_vectors=self.l3_inputs.runoff_vectors,
                is_runoff_preprocessed=self.l3_inputs.is_runoff_preprocessed
            )
            times.append((time.perf_counter() - t0) * 1000.0)

        mean_latency = float(np.mean(times))
        p95_latency = float(np.percentile(times, 95))
        print(f"\n[L1->L3 Coupling Latency] Mean: {mean_latency:.2f}ms, P95: {p95_latency:.2f}ms")
        self.assertLess(mean_latency, 350.0)
        self.assertLess(p95_latency, 350.0)

    def test_07_multi_horizon_inundation_depths_monotonic(self):
        """Inundation depths across cumulative horizons must be monotonically non-decreasing."""
        res = self.surrogate.predict_multi_horizon(
            rain_vectors=self.l3_inputs.runoff_vectors,
            is_runoff_preprocessed=self.l3_inputs.is_runoff_preprocessed
        )
        depths = res["horizons"]
        mean_depths = [float(np.mean(depths[h])) for h in HORIZONS_MIN]
        for i in range(len(mean_depths) - 1):
            self.assertLessEqual(mean_depths[i], mean_depths[i + 1])

    def test_08_error_on_segment_count_mismatch(self):
        """Coupling must raise ValueError if segment counts do not match."""
        # Create a truncated RunoffResult mock
        truncated_df = self.l1_runoff.dataframe.iloc[:5000].copy()
        truncated_rr = RunoffResult(
            dataframe=truncated_df,
            runoff_rates_mm_hr=self.l1_runoff.runoff_rates_mm_hr[:5000],
            discharge_m3_s=self.l1_runoff.discharge_m3_s[:5000],
            total_rain_volume_m3=1000.0,
            total_runoff_volume_m3=800.0,
            total_infiltrated_volume_m3=200.0
        )
        with self.assertRaises(ValueError):
            from_layer1_runoff(truncated_rr, self.graph)

    def test_09_error_on_segment_id_mismatch(self):
        """Coupling must raise ValueError if segment IDs are scrambled or permuted."""
        scrambled_df = self.l1_runoff.dataframe.copy()
        # Reverse the segment IDs
        scrambled_df["segment_id"] = scrambled_df["segment_id"].values[::-1]
        scrambled_rr = RunoffResult(
            dataframe=scrambled_df,
            runoff_rates_mm_hr=self.l1_runoff.runoff_rates_mm_hr,
            discharge_m3_s=self.l1_runoff.discharge_m3_s,
            total_rain_volume_m3=1000.0,
            total_runoff_volume_m3=800.0,
            total_infiltrated_volume_m3=200.0
        )
        with self.assertRaises(ValueError):
            from_layer1_runoff(scrambled_rr, self.graph)

    def test_10_layer2_backflow_extensibility(self):
        """Layer3Inputs must accommodate optional backflow_from_layer2 without error."""
        inputs = Layer3Inputs(
            runoff_vectors=self.l3_inputs.runoff_vectors,
            discharge_vectors=self.l3_inputs.discharge_vectors,
            source_layer="layer1",
            n_nodes=7894,
            segment_ids=self.l3_inputs.segment_ids,
            is_runoff_preprocessed=True,
            backflow_from_layer2={h: np.zeros(7894, dtype=np.float64) for h in HORIZONS_MIN}
        )
        self.assertIsNotNone(inputs.backflow_from_layer2)
        self.assertEqual(len(inputs.backflow_from_layer2[60]), 7894)

    def test_11_layer3_pipeline_with_l1_coupling(self):
        """Layer3Pipeline must run cleanly with layer1_runoff parameter."""
        from ai_service.layer3.pipeline import Layer3Pipeline
        pipe = Layer3Pipeline()
        result = pipe.run(
            scenario="2015_flood",
            layer1_runoff=self.l1_runoff
        )
        self.assertEqual(len(result.dataframe), 7894)
        self.assertEqual(result.diagnostics["upstream_forcing"], "layer1")
        self.assertTrue(result.diagnostics["is_runoff_preprocessed"])
        self.assertTrue(result.diagnostics["subsecond_benchmark_passed"])


if __name__ == "__main__":
    unittest.main()
