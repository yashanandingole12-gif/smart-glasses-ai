"""
Test Suite for God's Eye View: 3D Spatial Intelligence Engine.
Inspired by bilawalsidhu/gods-eye-view.
Validates 6-DoF pose tracking, FOV frustum intersection, distance/bearing geospatial calculation,
and exocentric orbital satellite maps.
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.spatial.gods_eye_engine import GodsEyeSpatialEngine, SpatialPose3D
from backend.app.services.spatial.spatial_anchors import SpatialAnchorResolver

client = TestClient(app)


class TestGodsEyeSpatialEngine:
    """Validates egocentric-to-exocentric 3D spatial intelligence."""

    def test_wearer_pose_and_frustum_intersection(self):
        engine = GodsEyeSpatialEngine(horizontal_fov_deg=68.0)
        
        # Orient glasses directly toward North (Heading 0°)
        # POI "Metro P3 Sign" is at bearing 15°, which is within half-FOV of 34°
        pose = engine.update_wearer_pose(lat=19.0760, lon=72.8777, altitude_m=15.0, heading_deg=0.0)
        assert pose.heading_deg == 0.0

        snapshot = engine.get_exocentric_orbital_snapshot()
        assert snapshot["satellite_view"]["camera_mode"] == "EXOCENTRIC_GODS_EYE_3D"
        assert len(snapshot["spatial_anchors"]) >= 3

        # Metro sign should be in FOV
        in_fov_labels = [e["label"] for e in snapshot["entities_in_fov"]]
        assert any("Metro Platform 3" in l for l in in_fov_labels)

        # Turn head 180° (facing South, Heading 180°) -> Metro sign should exit FOV
        engine.update_wearer_pose(lat=19.0760, lon=72.8777, altitude_m=15.0, heading_deg=180.0)
        snapshot_south = engine.get_exocentric_orbital_snapshot()
        in_fov_south = [e["label"] for e in snapshot_south["entities_in_fov"]]
        assert not any("Metro Platform 3" in l for l in in_fov_south)

    def test_spatial_anchor_geospatial_calculations(self):
        # Calculate distance and bearing between Mumbai Central coordinates
        lat1, lon1 = 19.0760, 72.8777
        lat2, lon2 = 19.0762, 72.8779
        dist_m, bearing_deg = SpatialAnchorResolver.calculate_distance_and_bearing(lat1, lon1, lat2, lon2)
        assert dist_m > 0.0
        assert 0.0 <= bearing_deg <= 360.0

        # Destination coordinate projection
        dest_lat, dest_lon = SpatialAnchorResolver.calculate_destination_coordinate(lat1, lon1, dist_m, bearing_deg)
        assert abs(dest_lat - lat2) < 1e-4
        assert abs(dest_lon - lon2) < 1e-4


class TestGodsEyeAPIEndpoints:
    """Tests FastAPI spatial endpoints."""

    def test_gods_eye_endpoints(self):
        resp_map = client.get("/api/v1/spatial/gods-eye")
        assert resp_map.status_code == 200
        data = resp_map.json()
        assert data["success"] is True
        assert "spatial_map" in data

        resp_pose = client.post("/api/v1/spatial/pose", json={
            "latitude": 19.0765,
            "longitude": 72.8780,
            "altitude_m": 16.0,
            "heading_deg": 45.0
        })
        assert resp_pose.status_code == 200
        assert resp_pose.json()["pose"]["heading_deg"] == 45.0
