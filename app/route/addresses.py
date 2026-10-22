from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.addresses import AddressModel
from app.schemas import AddressInput, AddressResponse, NearbyAddressResponse
from app.services import addresses as address_service

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.post(
    "",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_address(
    address: AddressInput,
    db: Session = Depends(get_db),
) -> AddressModel:
    return address_service.AddressAdd(db, address)


@router.get("", response_model=list[AddressResponse])
def list_addresses(
    db: Session = Depends(get_db),
) -> list[AddressModel]:
    return address_service.AddressList(db)


# Keep this static path above /{address_id}, which also matches one URL segment.
@router.get("/nearby", response_model=list[NearbyAddressResponse])
def find_nearby_addresses(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
    distance_km: float = Query(ge=0, le=20038),
    db: Session = Depends(get_db),
) -> list[NearbyAddressResponse]:
    return [
        NearbyAddressResponse.model_validate(
            {
                **AddressResponse.model_validate(address).model_dump(),
                "distance_km": round(distance, 3),
            }
        )
        for address, distance in address_service.AddressListNearby(
            db,
            latitude,
            longitude,
            distance_km,
        )
    ]


@router.get("/{address_id}", response_model=AddressResponse)
def get_address(
    address_id: int,
    db: Session = Depends(get_db),
) -> AddressModel:
    address = address_service.AddressGet(db, address_id)
    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )
    return address


@router.put("/{address_id}", response_model=AddressResponse)
def update_address(
    address_id: int,
    address_data: AddressInput,
    db: Session = Depends(get_db),
) -> AddressModel:
    address = address_service.AddressUpdate(db, address_id, address_data)
    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    return address


@router.delete(
    "/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
) -> Response:
    if not address_service.AddressDelete(db, address_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)