"""
Spatial Anchoring & Geospatial Coordinate Resolver.
Converts local camera object detections into absolute world geospatial coordinates.
"""
from typing import Dict, Any, Tuple
import math


class SpatialAnchorResolver:
    """Calculates geospatial offsets and vector bearings."""

    EARTH_RADIUS_METERS = 6378137.0

    @classmethod
    def calculate_destination_coordinate(
        cls,
        lat: float,
        lon: float,
        distance_m: float,
        bearing_deg: float
    ) -> Tuple[float, float]:
        """Calculates destination lat/lon given start point, distance, and bearing."""
        bearing_rad = math.radians(bearing_deg)
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)

        ang_dist = distance_m / cls.EARTH_RADIUS_METERS

        dest_lat = math.asin(
            math.sin(lat_rad) * math.cos(ang_dist) +
            math.cos(lat_rad) * math.sin(ang_dist) * math.cos(bearing_rad)
        )

        dest_lon = lon_rad + math.atan2(
            math.sin(bearing_rad) * math.sin(ang_dist) * math.cos(lat_rad),
            math.cos(ang_dist) - math.sin(lat_rad) * math.sin(dest_lat)
        )

        return math.degrees(dest_lat), math.degrees(dest_lon)

    @classmethod
    def calculate_distance_and_bearing(
        cls,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> Tuple[float, float]:
        """Returns distance in meters and initial bearing in degrees."""
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        distance = cls.EARTH_RADIUS_METERS * c

        y = math.sin(delta_lambda) * math.cos(phi2)
        x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
        bearing = (math.degrees(math.atan2(y, x)) + 360.0) % 360.0

        return round(distance, 2), round(bearing, 2)
