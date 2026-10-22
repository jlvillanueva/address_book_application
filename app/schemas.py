from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AddressInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    street: str = Field(min_length=1, max_length=150)
    city: str = Field(min_length=1, max_length=150)
    country: str = Field(min_length=1, max_length=150)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class AddressResponse(AddressInput):
    model_config = ConfigDict(from_attributes=True)

    address_id: int
    created_at: datetime
    updated_at: datetime


class NearbyAddressResponse(AddressResponse):
    distance_km: float
