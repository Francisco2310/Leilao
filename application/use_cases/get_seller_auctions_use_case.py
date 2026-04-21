
from domain.Entities.auction import Auction
from application.ports.auction_repository import AuctionRepositoryInterface
from application.dtos.auction_dtos import AuctionResponseDto

class GetSellerAuctionsUseCase:
    def __init__(self, repository: AuctionRepositoryInterface):
        self._repository = repository

    def execute(self, start_page: int, total_per_page: int, seller_id: str, status: str = "draft") -> list[AuctionResponseDto]:
        if not seller_id:
            raise ValueError("Seller ID is required to fetch seller auctions")
        if start_page <= 0:
            raise ValueError("Start page must be greater than 0")
        if total_per_page <= 0:
            raise ValueError("Total per page must be greater than 0")
            
        auctions = self._repository.find_all(start_page, total_per_page, seller_id=seller_id, status=status)
        return [AuctionResponseDto.from_entity(auction) for auction in auctions]