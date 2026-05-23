
from domain.Entities.auction import Auction
from application.ports.auction_repository import AuctionRepositoryInterface
from application.dtos.auction_dtos import AuctionResponseDto

class GetAuctionsUseCase:
    def __init__(self, repository: AuctionRepositoryInterface):
        self._repository = repository

    def execute(self, limit: int, cursor: str | None = None, seller_id: str | None = None, status: str | None = None) -> list[AuctionResponseDto]:
        if limit <= 0:
            raise ValueError("Limit must be greater than 0")
            
        auctions = self._repository.find_all(limit=limit, cursor=cursor, seller_id=seller_id, status=status)
        return [AuctionResponseDto.from_entity(auction) for auction in auctions]