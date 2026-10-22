import pytest

from app.services.distance import distance_in_kilometers


def test_distance_between_same_coordinates_is_zero():
    distance = distance_in_kilometers(14.5995, 120.9842, 14.5995, 120.9842)

    assert distance == pytest.approx(0)


def test_one_degree_of_longitude_at_equator_is_about_111_km():
    distance = distance_in_kilometers(0, 0, 0, 1)

    assert distance == pytest.approx(111.2, abs=0.2)
