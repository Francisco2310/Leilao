
from domain.Entities.auction import Auction
from application.ports.auction_repository import AuctionRepositoryInterface
from application.dtos.auction_dtos import AuctionResponseDto

class GetDraftAuctionsUseCase:
    def __init__(self, repository: AuctionRepositoryInterface):
        self._repository = repository

    def execute(self, start_page: int, total_per_page: int, seller_id: str) -> list[AuctionResponseDto]:
        if not seller_id:
            raise ValueError("Seller ID is required to fetch draft auctions")
            
        auctions = self._repository.find_all(start_page, total_per_page, seller_id=seller_id, status="draft")
        return [AuctionResponseDto.from_entity(auction) for auction in auctions]