"""
Unit Tests for Tactical Add-Ons: Coastal Boundary, CML Mesh, CAP Alerts, and Pump Optimizer.
"""

import unittest
from ai_service.layer0.cml_mesh import CMLMeshRetriever
from ai_service.layer2.coastal_boundary import CoastalBoundaryEngine
from ai_service.layer4.pump_optimizer import MunicipalPumpOptimizer
from ai_service.layer4.cap_emitter import CAPAlertEmitter


class TestTacticalAddons(unittest.TestCase):
    """Test suite for new tactical modules."""

    def test_01_cml_mesh_retrieval(self):
        """Verify ITU-R P.838 CML power law inversion."""
        retriever = CMLMeshRetriever()
        rate = retriever.retrieve_rain_rate(
            frequency_ghz=18.0,
            polarization="H",
            path_length_km=4.0,
            rsl_dbm=-52.0,
            baseline_dbm=-45.0,
            waa_db=1.5
        )
        self.assertGreater(rate, 5.0)

        telemetry = retriever.get_mesh_telemetry(storm_scenario="michaung")
        self.assertEqual(telemetry["status"], "success")
        self.assertGreaterEqual(telemetry["active_cml_links"], 5)
        self.assertGreater(telemetry["mesh_mean_rain_rate_mm_hr"], 10.0)

    def test_02_coastal_boundary_tidal_surge(self):
        """Verify astronomical tide and Holland surge outfall states."""
        engine = CoastalBoundaryEngine()
        astro_tide = engine.compute_astronomical_tide(t_hours=6.0)
        self.assertIsInstance(astro_tide, float)

        surge = engine.compute_cyclonic_surge(central_pressure_hpa=975.0, sustained_wind_speed_kmh=110.0)
        self.assertGreater(surge, 0.5)

        outfalls = engine.evaluate_outfall_states(t_hours=6.0, cyclonic_surge_m=1.2, storm_scenario="michaung")
        self.assertEqual(outfalls["outfalls_monitored"], 4)
        self.assertGreater(outfalls["outfalls_locked_out"], 0)

    def test_03_pump_optimizer(self):
        """Verify municipal de-watering pump placement rankings."""
        opt = MunicipalPumpOptimizer()
        recs = opt.optimize_deployments(max_recommendations=5)
        self.assertEqual(len(recs), 5)
        self.assertEqual(recs[0]["priority_rank"], 1)
        self.assertIn("required_capacity_m3_hr", recs[0])
        self.assertIn("action_directive", recs[0])

    def test_04_cap_alert_xml_and_bulletins(self):
        """Verify OASIS CAP v1.2 XML generation and Tamil translation."""
        emitter = CAPAlertEmitter()
        xml_str = emitter.generate_cap_xml(
            headline_en="Test Flood Warning",
            headline_ta="சோதனை வெள்ள எச்சரிக்கை",
            description_en="Heavy rain expected.",
            description_ta="கனமழை எதிர்பார்க்கப்படுகிறது.",
            instruction_en="Stay safe.",
            instruction_ta="பாதுகாப்பாக இருக்கவும்.",
            zone_no=9
        )
        self.assertIn("<alert", xml_str)
        self.assertIn("en-IN", xml_str)
        self.assertIn("ta-IN", xml_str)

        bulletins = emitter.generate_ward_engineer_bulletin(
            zone_no=9,
            locality="T. Nagar Usman Road",
            predicted_depth_cm=45.0,
            surcharge_rate_m3_s=1.2
        )
        self.assertIn("whatsapp_technical_bulletin", bulletins)
        self.assertIn("citizen_sms_ta", bulletins)


if __name__ == "__main__":
    unittest.main()
