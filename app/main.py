import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.database import Base, engine
from app.route.addresses import router as addresses_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Create the SQLite tables before the API starts accepting requests.
    Base.metadata.create_all(bind=engine)
    logger.info("Address book database is ready")
    yield


app = FastAPI(
    title="Address Book API",
    description="Create, manage, and search addresses by geographic distance.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(addresses_router)
