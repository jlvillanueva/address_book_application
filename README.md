# Address Book API

A small REST API built with FastAPI, SQLAlchemy, and SQLite. It supports creating,
listing, retrieving, updating, and deleting addresses, plus searching for saved
addresses within a distance of geographic coordinates.

## Project layout

The application keeps HTTP handling, address operations, and persistence in
separate modules:

- `app/main.py` creates the FastAPI application and registers the address routes.
- `app/route/addresses.py` handles endpoint parameters, validation integration,
  and HTTP response codes.
- `app/services/addresses.py` contains reusable address operations and
  operation logging.
- `app/services/distance.py` calculates geographic distances.
- `app/models/addresses.py` defines the SQLAlchemy address model.
- `app/database.py` configures SQLAlchemy and provides database sessions.
- `app/schemas.py` validates request data and structures API responses.

This keeps the same endpoint-versus-operation separation used in the reference
APIs, while using FastAPI routers, Pydantic schemas, and dependency injection.

## Requirements

- Python 3.9 or later
- pip

## Install and run

From the repository root, run:

```bash
cd address_book_api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000/docs> for interactive Swagger documentation. The
SQLite database, `address_book.db`, is created in this directory when the app
starts. The API logs startup and address create, update, delete, and not-found
events without logging address details.

To run the tests:

```bash
pytest
```

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/addresses` | Create an address |
| `GET` | `/addresses` | List all addresses |
| `GET` | `/addresses/{address_id}` | Retrieve one address |
| `PUT` | `/addresses/{address_id}` | Replace an address |
| `DELETE` | `/addresses/{address_id}` | Delete an address |
| `GET` | `/addresses/nearby` | Search by `latitude`, `longitude`, and `distance_km` |

Coordinates are validated as latitude `-90..90` and longitude `-180..180`.
Nearby-search distances are in kilometers. Results include their calculated
distance and are sorted from nearest to farthest. The app uses the Haversine
formula and checks the saved addresses in Python, which is suitable for this
small assessment project.

Example request:

```bash
curl -X POST http://127.0.0.1:8000/addresses \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Home",
    "street": "1 Main Street",
    "city": "Makati",
    "country": "Rizal",
    "latitude": 37.7749,
    "longitude": -122.4194
  }'
```

Example nearby search:

```bash
curl 'http://127.0.0.1:8000/addresses/nearby?latitude=37.7749&longitude=-122.4194&distance_km=5'
```
