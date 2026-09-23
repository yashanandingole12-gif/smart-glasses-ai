"""
God's Eye View: 3D Spatial Intelligence Engine.
Inspired by bilawalsidhu/gods-eye-view.
Bridges 1st-person egocentric wearable camera/IMU view to world-scale 3D exocentric bird's-eye geospatial space.
"""
from typing import Dict, Any, List, Optional
import math
import time
from pydantic import BaseModel, Field


class SpatialPose3D(BaseModel):
    """6-DoF Position and Orientation in geospatial coordinate space."""
    latitude: float = 19.0760  # Default Mumbai / Mumbai Central Platform
    longitude: float = 72.8777
    altitude_m: float = 15.0
    heading_deg: float = 0.0    # 0 = North, 90 = East, etc.
    pitch_deg: float = 0.0
    roll_deg: float = 0.0


class SpatialPOI(BaseModel):
    """3D Point of Interest or detected entity anchored in world space."""
    poi_id: str
    label: str
    category: str  # "TRANSIT_SIGN", "BUILDING", "OBSTACLE", "PERSON", "CIVIC_ASSET"
    latitude: float
    longitude: float
    altitude_m: float
    distance_to_wearer_m: float
    bearing_deg: float
    in_wearer_fov: bool = False
    frustum_screen_coords: Optional[Dict[str, float]] = None  # Normalized x, y in [-1, 1]


class GodsEyeSpatialEngine:
    """
    Translates egocentric smart glasses orientation into exocentric 3D bird's-eye view.
    Enables dual-perspective reasoning:
    1. First-Person HUD view (HUD overlays, directional arrows, object callouts)
    2. Exocentric 'God's Eye' satellite/aerial 3D map (orbital view, trajectory trace, spatial anchoring)
    """

    def __init__(self, horizontal_fov_deg: float = 68.0, vertical_fov_deg: float = 42.0):
        self.horizontal_fov_deg = horizontal_fov_deg
        self.vertical_fov_deg = vertical_fov_deg
        self.current_pose = SpatialPose3D()
        self.known_world_anchors: List[SpatialPOI] = []
        self._initialize_default_civic_anchors()

    def _initialize_default_civic_anchors(self) -> None:
        """Initializes sample world anchors (e.g. metro signs, civic assets, platforms)."""
        self.known_world_anchors = [
            SpatialPOI(
                poi_id="poi_metro_p3",
                label="Mumbai Central Metro Platform 3 Signboard",
                category="TRANSIT_SIGN",
                latitude=19.0762,
                longitude=72.8779,
                altitude_m=14.5,
                distance_to_wearer_m=12.5,
                bearing_deg=15.0
            ),
            SpatialPOI(
                poi_id="poi_civic_pothole_01",
                label="Reported Road Degradation Zone",
                category="CIVIC_ASSET",
                latitude=19.0758,
                longitude=72.8775,
                altitude_m=13.0,
                distance_to_wearer_m=28.0,
                bearing_deg=210.0
            ),
            SpatialPOI(
                poi_id="poi_ev_charging_hub",
                label="Clean Energy Transit Hub",
                category="BUILDING",
                latitude=19.0770,
                longitude=72.8785,
                altitude_m=18.0,
                distance_to_wearer_m=95.0,
                bearing_deg=45.0
            )
        ]

    def update_wearer_pose(
        self,
        lat: float,
        lon: float,
        altitude_m: float,
        heading_deg: float,
        pitch_deg: float = 0.0,
        roll_deg: float = 0.0
    ) -> SpatialPose3D:
        """Updates the 6-DoF pose of the glasses in world space."""
        self.current_pose.latitude = lat
        self.current_pose.longitude = lon
        self.current_pose.altitude_m = altitude_m
        self.current_pose.heading_deg = heading_deg % 360.0
        self.current_pose.pitch_deg = pitch_deg
        self.current_pose.roll_deg = roll_deg
        self._recompute_frustum_intersections()
        return self.current_pose

    def _recompute_frustum_intersections(self) -> None:
        """Projects 3D POIs into the wearer's 1st-person FoV frustum."""
        h_half = self.horizontal_fov_deg / 2.0
        heading = self.current_pose.heading_deg

        for poi in self.known_world_anchors:
            # Compute angular offset between glasses heading and POI bearing
            angle_diff = (poi.bearing_deg - heading + 180.0) % 360.0 - 180.0
            
            if abs(angle_diff) <= h_half:
                poi.in_wearer_fov = True
                norm_x = angle_diff / h_half  # Range [-1.0, 1.0]
                norm_y = 0.0                  # Level horizon approximation
                poi.frustum_screen_coords = {"x": round(norm_x, 3), "y": round(norm_y, 3)}
            else:
                poi.in_wearer_fov = False
                poi.frustum_screen_coords = None

    def get_exocentric_orbital_snapshot(self) -> Dict[str, Any]:
        """
        Generates a 3D God's Eye orbital spatial map payload for CesiumJS / 3D Canvas visualizers.
        """
        return {
            "satellite_view": {
                "orbital_altitude_m": self.current_pose.altitude_m + 150.0,
                "center_lat": self.current_pose.latitude,
                "center_lon": self.current_pose.longitude,
                "look_at_heading_deg": self.current_pose.heading_deg,
                "camera_mode": "EXOCENTRIC_GODS_EYE_3D"
            },
            "wearer_frustum": {
                "origin": {
                    "lat": self.current_pose.latitude,
                    "lon": self.current_pose.longitude,
                    "alt_m": self.current_pose.altitude_m
                },
                "heading_deg": self.current_pose.heading_deg,
                "horizontal_fov_deg": self.horizontal_fov_deg,
                "range_m": 50.0
            },
            "spatial_anchors": [p.model_dump() for p in self.known_world_anchors],
            "entities_in_fov": [p.model_dump() for p in self.known_world_anchors if p.in_wearer_fov]
        }
