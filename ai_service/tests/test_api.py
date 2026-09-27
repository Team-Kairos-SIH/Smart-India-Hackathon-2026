import unittest
import sys
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from ai_service.api import app

# Helper mock for Layer4Service
def get_mock_service():
    mock_service = MagicMock()
    # Default successful route response
    mock_service.route.return_value = {
        "status": "SUCCESS",
        "route_geometry": [[13.1, 80.1], [13.2, 80.2]],
        "total_distance_m": 1500.0,
        "eta_min": 5.0
    }
    
    # Default successful assets response
    mock_service.get_asset_status.return_value = {
        "status": "SUCCESS",
        "total_monitored": 20,
        "assets": [
            {
                "substation_id": f"SS-{i}",
                "status": "UNKNOWN",
                "uncertainty": "PLINTH_UNKNOWN",
                "maximum_site_depth_cm": 15.0
            } for i in range(1, 21)
        ]
    }
    return mock_service


class TestAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        self.patcher = patch("ai_service.api.get_layer4_service", return_value=get_mock_service())
        self.mock_layer4 = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    # --- POST /route Tests ---

    def test_route_valid(self):
        # 1. valid route
        response = self.client.post(
            "/route",
            json={
                "vehicle_type": "ambulance",
                "origin": {"latitude": 13.0, "longitude": 80.0},
                "destination": {"latitude": 13.1, "longitude": 80.1}
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("route_geometry", data)

    def test_route_invalid_vehicle(self):
        # 2. invalid vehicle (simulate failure in engine)
        self.mock_layer4.return_value.route.return_value = {
            "status": "FAILED",
            "failure_reason": "Invalid vehicle type"
        }
        response = self.client.post(
            "/route",
            json={
                "vehicle_type": "invalid_boat",
                "origin": {"latitude": 13.0, "longitude": 80.0},
                "destination": {"latitude": 13.1, "longitude": 80.1}
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("invalid vehicle", response.json()["detail"]["failure_reason"].lower())

    def test_route_invalid_coordinates(self):
        # 3. invalid coordinates
        response = self.client.post(
            "/route",
            json={
                "vehicle_type": "ambulance",
                "origin": {"latitude": "invalid", "longitude": 80.0},
                "destination": {"latitude": 13.1, "longitude": 80.1}
            }
        )
        self.assertEqual(response.status_code, 422)

    def test_route_missing_origin(self):
        # 4. missing origin
        response = self.client.post(
            "/route",
            json={
                "vehicle_type": "ambulance",
                "destination": {"latitude": 13.1, "longitude": 80.1}
            }
        )
        self.assertEqual(response.status_code, 422)

    def test_route_missing_destination(self):
        # 5. missing destination
        response = self.client.post(
            "/route",
            json={
                "vehicle_type": "ambulance",
                "origin": {"latitude": 13.0, "longitude": 80.0}
            }
        )
        self.assertEqual(response.status_code, 422)

    def test_route_invalid_departure_time(self):
        # 6. invalid departure time
        response = self.client.post(
            "/route",
            json={
                "vehicle_type": "ambulance",
                "origin": {"latitude": 13.0, "longitude": 80.0},
                "destination": {"latitude": 13.1, "longitude": 80.1},
                "departure_time": "not_a_time"
            }
        )
        self.assertEqual(response.status_code, 422)

    def test_route_blocked_no_route(self):
        # 7. blocked/no route
        self.mock_layer4.return_value.route.return_value = {
            "status": "FAILED",
            "failure_reason": "no safe route found"
        }
        response = self.client.post(
            "/route",
            json={
                "vehicle_type": "ambulance",
                "origin": {"latitude": 13.0, "longitude": 80.0},
                "destination": {"latitude": 13.1, "longitude": 80.1}
            }
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("no safe route found", response.json()["detail"]["failure_reason"].lower())

    def test_route_layer3_unavailable(self):
        # 8. Layer 3 unavailable/invalid response
        self.mock_layer4.return_value.route.side_effect = Exception("Layer 3 timeout")
        response = self.client.post(
            "/route",
            json={
                "vehicle_type": "ambulance",
                "origin": {"latitude": 13.0, "longitude": 80.0},
                "destination": {"latitude": 13.1, "longitude": 80.1}
            }
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("Layer 3 timeout", response.json()["detail"])

    # --- GET /assets/status Tests ---

    def test_assets_successful(self):
        # 1. successful response
        response = self.client.get("/assets/status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "SUCCESS")

    def test_assets_all_20_returned(self):
        # 2. all 20 substations returned
        response = self.client.get("/assets/status")
        self.assertEqual(response.json()["total_monitored"], 20)
        self.assertEqual(len(response.json()["assets"]), 20)

    def test_assets_unknown_plinth_remains_unknown(self):
        # 3. unknown plinth remains unknown
        response = self.client.get("/assets/status")
        assets = response.json()["assets"]
        self.assertEqual(assets[0]["uncertainty"], "PLINTH_UNKNOWN")
        self.assertEqual(assets[0]["status"], "UNKNOWN")

    def test_assets_missing_flood_data_not_zero(self):
        # 4. missing flood data is not treated as zero
        self.mock_layer4.return_value.get_asset_status.return_value = {
            "status": "SUCCESS",
            "total_monitored": 1,
            "assets": [{
                "substation_id": "SS-1",
                "status": "UNKNOWN",
                "uncertainty": "DATA_UNAVAILABLE",
                "maximum_site_depth_cm": 0.0
            }]
        }
        response = self.client.get("/assets/status")
        asset = response.json()["assets"][0]
        self.assertEqual(asset["uncertainty"], "DATA_UNAVAILABLE")
        self.assertEqual(asset["status"], "UNKNOWN")

    def test_assets_monitor_failure(self):
        # 5. monitor failure is handled correctly
        self.mock_layer4.return_value.get_asset_status.return_value = {
            "status": "FAILED",
            "error": "Asset DB offline"
        }
        response = self.client.get("/assets/status")
        self.assertEqual(response.status_code, 500)
        self.assertIn("Asset DB offline", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
