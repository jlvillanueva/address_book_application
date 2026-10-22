import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    test_session_local = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = test_session_local()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setattr("app.main.engine", test_engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    test_engine.dispose()


def address_payload(**overrides):
    payload = {
        "name": "Home",
        "street": "1 Main Street",
        "city": "San Francisco",
        "country": "United States",
        "latitude": 37.7749,
        "longitude": -122.4194,
    }
    payload.update(overrides)
    return payload


def test_create_get_update_and_delete_address(client):
    created = client.post("/addresses", json=address_payload())
    assert created.status_code == 201
    created_data = created.json()
    address_id = created_data["address_id"]
    assert created_data["name"] == "Home"

    retrieved = client.get(f"/addresses/{address_id}")
    assert retrieved.status_code == 200
    assert retrieved.json()["city"] == "San Francisco"

    updated = client.put(
        f"/addresses/{address_id}",
        json=address_payload(name="Office"),
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Office"

    deleted = client.delete(f"/addresses/{address_id}")
    assert deleted.status_code == 204
    assert client.get(f"/addresses/{address_id}").status_code == 404


def test_list_addresses_returns_all_addresses(client):
    client.post("/addresses", json=address_payload())
    client.post(
        "/addresses",
        json=address_payload(name="Office", city="Oakland"),
    )

    response = client.get("/addresses")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    assert [address["name"] for address in results] == ["Home", "Office"]


def test_nearby_search_returns_only_addresses_within_radius(client):
    client.post("/addresses", json=address_payload())
    client.post(
        "/addresses",
        json=address_payload(
            name="Far away",
            city="Los Angeles",
            latitude=34.0522,
            longitude=-118.2437,
        ),
    )

    response = client.get(
        "/addresses/nearby",
        params={
            "latitude": 37.7749,
            "longitude": -122.4194,
            "distance_km": 5,
        },
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["name"] == "Home"
    assert results[0]["distance_km"] == 0


@pytest.mark.parametrize(
    "field,value",
    [
        ("latitude", 91),
        ("latitude", -91),
        ("longitude", 181),
        ("longitude", -181),
    ],
)
def test_create_rejects_invalid_coordinates(client, field, value):
    response = client.post("/addresses", json=address_payload(**{field: value}))
    assert response.status_code == 422


def test_nearby_search_rejects_invalid_coordinates(client):
    response = client.get(
        "/addresses/nearby",
        params={"latitude": 91, "longitude": 0, "distance_km": 1},
    )
    assert response.status_code == 422


def test_missing_address_returns_not_found(client):
    response = client.get("/addresses/999")
    assert response.status_code == 404
