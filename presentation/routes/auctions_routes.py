from fastapi import APIRouter, Depends
from pydantic import BaseModel
from presentation.api.dependencies import get_auction_repository, get_id_generator, get_clock
from application.use_cases.create_auction_use_case import CreateAuctionUseCase
from application.use_cases.start_auction_use_case import StartAuctionUseCase
from application.use_cases.get_auctions_use_case import GetAuctionsUseCase
from application.use_cases.cancel_auction_use_case import CancelAuctionUseCase
from application.use_cases.close_auction_use_case import CloseAuctionUseCase
from datetime import datetime
from typing import Optional
from presentation.api.types import UUID7Str

from domain.ValueObjects.money import Currency
from decimal import Decimal

class CreateAuctionRequest(BaseModel):
    seller_id: UUID7Str

class StartAuctionRequest(BaseModel):
    seller_id: UUID7Str
    reserve_price: Decimal
    currency: Currency
    product_id: UUID7Str
    expires_at: datetime
    minimum_percentage: Decimal

class CancelAuctionRequest(BaseModel):
    seller_id: UUID7Str

router = APIRouter()

@router.post("/auctions", status_code=201)
def create_auction(request: CreateAuctionRequest, repo = Depends(get_auction_repository), id_generator = Depends(get_id_generator)):
    use_case = CreateAuctionUseCase(repo, id_generator)
    new_id = use_case.execute(request.seller_id)
    return {"auction_id": new_id}


@router.post("/auctions/{auction_id}/start", status_code=200)
def start_auction(auction_id: UUID7Str, request: StartAuctionRequest, repo = Depends(get_auction_repository), clock = Depends(get_clock)):
    use_case = StartAuctionUseCase(repo, clock)
    use_case.execute(auction_id, request.seller_id, request.reserve_price, request.currency.value, request.product_id, request.expires_at, request.minimum_percentage)
    return {"message": "Auction started successfully"}


@router.get("/auctions", status_code=200)
def list_auctions(
    limit: int = 10, 
    cursor: Optional[str] = None, 
    seller_id: Optional[str] = None, 
    status: Optional[str] = None, 
    repo = Depends(get_auction_repository)
):
    use_case = GetAuctionsUseCase(repo)
    return use_case.execute(limit, cursor, seller_id, status)


@router.post("/auctions/{auction_id}/cancel", status_code=200)
def cancel_auction(auction_id: UUID7Str, request: CancelAuctionRequest, repo = Depends(get_auction_repository)):
    use_case = CancelAuctionUseCase(repo)
    use_case.execute(auction_id, request.seller_id)
    return {"message": "Auction cancelled successfully"}


@router.post("/auctions/{auction_id}/close", status_code=200)
def close_auction(auction_id: UUID7Str, repo = Depends(get_auction_repository), clock = Depends(get_clock)):
    use_case = CloseAuctionUseCase(repo, clock)
    use_case.execute(auction_id)
    return {"message": "Auction closed successfully"}