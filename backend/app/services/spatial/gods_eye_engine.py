"""
God's Eye View: 3D Spatial Intelligence Engine.
Inspired by bilawalsidhu/gods-eye-view & Google Earth 3D Photorealistic Geospatial Systems.
Bridges 1st-person egocentric wearable camera/IMU view to world-scale 3D exocentric bird's-eye geospatial space.
Default Home Hub: Nagpur, Maharashtra, India (Zero Mile City).
"""
from typing import Dict, Any, List, Optional
import math
import time
from pydantic import BaseModel, Field


class SpatialPose3D(BaseModel):
    """6-DoF Position and Orientation in geospatial coordinate space."""
    latitude: float = 21.1458   # Default: Nagpur (Sitabuldi / Zero Mile)
    longitude: float = 79.0882
    altitude_m: float = 312.0   # Nagpur elevation ~310m MSL
    heading_deg: float = 0.0    # 0 = North, 90 = East, 180 = South, 270 = West
    pitch_deg: float = 0.0
    roll_deg: float = 0.0


class SpatialPOI(BaseModel):
    """3D Point of Interest or detected entity anchored in world space."""
    poi_id: str
    label: str
    category: str  # "METRO_STATION", "LANDMARK", "TRANSIT_SIGN", "BUILDING", "CIVIC_ASSET"
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
        self._initialize_default_nagpur_anchors()

    def _initialize_default_nagpur_anchors(self) -> None:
        """Initializes landmark world anchors in Nagpur, Maharashtra."""
        self.known_world_anchors = [
            SpatialPOI(
                poi_id="poi_sitabuldi_metro",
                label="Sitabuldi Interchange Metro Station (Aqua/Orange)",
                category="METRO_STATION",
                latitude=21.1458,
                longitude=79.0832,
                altitude_m=315.0,
                distance_to_wearer_m=350.0,
                bearing_deg=260.0
            ),
            SpatialPOI(
                poi_id="poi_zero_mile",
                label="Zero Mile Stone (Geographical Center of India)",
                category="LANDMARK",
                latitude=21.1478,
                longitude=79.0883,
                altitude_m=312.0,
                distance_to_wearer_m=220.0,
                bearing_deg=5.0
            ),
            SpatialPOI(
                poi_id="poi_nagpur_junction",
                label="Nagpur Junction Railway Station (Platform 1)",
                category="METRO_STATION",
                latitude=21.1524,
                longitude=79.0889,
                altitude_m=310.0,
                distance_to_wearer_m=750.0,
                bearing_deg=10.0
            ),
            SpatialPOI(
                poi_id="poi_futala_lake",
                label="Futala Lake Waterfront & Promenade",
                category="CIVIC_ASSET",
                latitude=21.1558,
                longitude=79.0435,
                altitude_m=305.0,
                distance_to_wearer_m=4600.0,
                bearing_deg=285.0
            ),
            SpatialPOI(
                poi_id="poi_nagpur_airport",
                label="Dr. Babasaheb Ambedkar International Airport (NAG)",
                category="METRO_STATION",
                latitude=21.0922,
                longitude=79.0472,
                altitude_m=315.0,
                distance_to_wearer_m=7200.0,
                bearing_deg=215.0
            ),
            SpatialPOI(
                poi_id="poi_deekshabhoomi",
                label="Deekshabhoomi Sacred Stupa",
                category="LANDMARK",
                latitude=21.1278,
                longitude=79.0667,
                altitude_m=314.0,
                distance_to_wearer_m=2800.0,
                bearing_deg=225.0
            )
        ]

    def update_wearer_pose(
        self,
        lat: float,
        lon: float,
        altitude_m: float = 312.0,
        heading_deg: float = 0.0,
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

    def get_google_live_earth_3d_link(self, target_lat: Optional[float] = None, target_lon: Optional[float] = None) -> str:
        """Builds a direct deep link into Google Earth 3D Web orbital viewer."""
        lat = target_lat if target_lat is not None else self.current_pose.latitude
        lon = target_lon if target_lon is not None else self.current_pose.longitude
        return f"https://earth.google.com/web/@{lat},{lon},312a,950d,35y,0h,45t,0r"

    def get_exocentric_orbital_snapshot(self) -> Dict[str, Any]:
        """
        Generates a 3D God's Eye orbital spatial map payload for CesiumJS / 3D Canvas visualizers.
        """
        return {
            "city": "Nagpur, Maharashtra, India",
            "google_earth_3d_url": self.get_google_live_earth_3d_link(),
            "satellite_view": {
                "orbital_altitude_m": self.current_pose.altitude_m + 350.0,
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
                "range_m": 150.0
            },
            "spatial_anchors": [p.model_dump() for p in self.known_world_anchors],
            "entities_in_fov": [p.model_dump() for p in self.known_world_anchors if p.in_wearer_fov]
        }

gods_eye_spatial_engine = GodsEyeSpatialEngine()
