from fastapi import APIRouter, Depends
from pydantic import BaseModel
from decimal import Decimal
from presentation.api.dependencies import get_auction_repository, get_id_generator, get_clock
from presentation.api.types import UUID7Str
from application.use_cases.add_bid_use_case import AddBidUseCase

class AddBidRequest(BaseModel):
    user_id: UUID7Str
    amount: Decimal
    currency: str

router = APIRouter()

@router.post("/auctions/{auction_id}/bids", status_code=201)
def add_bid(auction_id: UUID7Str, request: AddBidRequest, repo = Depends(get_auction_repository), id_generator = Depends(get_id_generator), clock = Depends(get_clock)):
    use_case = AddBidUseCase(repo, id_generator, clock)
    use_case.execute(
        auction_id=auction_id,
        user_id=request.user_id,
        amount=request.amount,
        currency=request.currency
    )
    return {"message": "Bid added successfully"}
