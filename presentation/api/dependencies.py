from fastapi import Depends
from sqlalchemy.orm import Session
from infrastructure.database.database import get_db
from infrastructure.repositories.postgres_repository import AuctionRepository
from application.ports.auction_repository import AuctionRepositoryInterface
from infrastructure.adapters.uuid7_id_generator import Uuid7IdGenerator
from infrastructure.adapters.system_clock import SystemClock
from domain.Ports.ports import Clock, IdGenerator

def get_auction_repository(session: Session = Depends(get_db)) -> AuctionRepositoryInterface:
    return AuctionRepository(session)

def get_id_generator() -> IdGenerator:
    return Uuid7IdGenerator()

def get_clock() -> Clock:
    return SystemClock()
