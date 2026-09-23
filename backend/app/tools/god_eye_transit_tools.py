"""
God's Eye Live — Transit & Spatial Tools
Enables EVA smart glasses to query live traffic, nearest metro stations,
train schedules, and flight statuses hands-free.
"""

from typing import Dict, Any, Optional
from backend.app.services.transit_service import transit_service

def transit_traffic_status(location: str = "", destination: str = "") -> Dict[str, Any]:
    """
    Check live road traffic, congestion levels, bottlenecks, and alternate routes.
    """
    return transit_service.get_traffic_status(location=location, destination=destination)

def transit_metro_stations(query: str = "") -> Dict[str, Any]:
    """
    Find nearest metro stations, line colors, platform number, and next train arrival times.
    """
    return transit_service.get_nearest_metro(query=query)

def transit_train_schedule(query: str = "") -> Dict[str, Any]:
    """
    Check suburban and intercity train departure schedules, delays, and platform numbers.
    """
    return transit_service.get_train_schedule(query=query)

def transit_flight_status(flight_number: str) -> Dict[str, Any]:
    """
    Track real-time flight status, departure/arrival gate, terminal, and baggage carousel.
    """
    return transit_service.get_flight_status(flight_number=flight_number)

def transit_god_eye_overview(query: str = "") -> Dict[str, Any]:
    """
    Unified God's Eye query across traffic, metro, trains, and flights.
    """
    return transit_service.query_god_eye(message=query)
