import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.addresses import AddressModel
from app.schemas import AddressInput
from app.services.distance import distance_in_kilometers

logger = logging.getLogger(__name__)


def AddressAdd(db: Session, address_data: AddressInput) -> AddressModel:
    address = AddressModel(**address_data.model_dump())
    db.add(address)
    db.commit()
    db.refresh(address)
    logger.info("Created address with id=%s", address.address_id)
    return address


def AddressList(db: Session, skip: int = 0, limit: int = 100) -> list[AddressModel]:
    statement = (
        select(AddressModel)
        .order_by(AddressModel.address_id)
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def AddressGet(db: Session, address_id: int) -> Optional[AddressModel]:
    address = db.get(AddressModel, address_id)
    if address is None:
        logger.warning("Address not found with id=%s", address_id)
    return address


def AddressUpdate(
    db: Session,
    address_id: int,
    address_data: AddressInput,
) -> Optional[AddressModel]:
    address = db.get(AddressModel, address_id)
    if address is None:
        logger.warning("Cannot update missing address with id=%s", address_id)
        return None

    for field, value in address_data.model_dump().items():
        setattr(address, field, value)
    db.commit()
    db.refresh(address)
    logger.info("Updated address with id=%s", address_id)
    return address


def AddressDelete(db: Session, address_id: int) -> bool:
    address = db.get(AddressModel, address_id)
    if address is None:
        logger.warning("Cannot delete missing address with id=%s", address_id)
        return False

    db.delete(address)
    db.commit()
    logger.info("Deleted address with id=%s", address_id)
    return True


def AddressListNearby(
    db: Session,
    latitude: float,
    longitude: float,
    distance_km: float,
) -> list[tuple[AddressModel, float]]:
    addresses = db.scalars(select(AddressModel)).all()
    matches = []

    for address in addresses:
        distance = distance_in_kilometers(
            latitude,
            longitude,
            address.latitude,
            address.longitude,
        )
        if distance <= distance_km:
            matches.append((address, distance))

    matches.sort(key=lambda match: match[1])
    return matches
