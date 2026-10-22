from math import asin, cos, radians, sin, sqrt


def distance_in_kilometers(
    latitude_a: float,
    longitude_a: float,
    latitude_b: float,
    longitude_b: float,
) -> float:
    """Return the great-circle distance between two coordinates."""
    # Mean Earth radius in kilometers.
    earth_radius_km = 6371.0088
    lat_a, lat_b = radians(latitude_a), radians(latitude_b)
    latitude_delta = radians(latitude_b - latitude_a)
    longitude_delta = radians(longitude_b - longitude_a)

    haversine = (
        sin(latitude_delta / 2) ** 2
        + cos(lat_a) * cos(lat_b) * sin(longitude_delta / 2) ** 2
    )
    central_angle = 2 * asin(sqrt(min(1.0, haversine)))
    return earth_radius_km * central_angle