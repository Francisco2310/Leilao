from application.ports.auction_repository import AuctionRepositoryInterface
from application.exceptions.application_exceptions import AuctionNotFoundError

class CancelAuctionUseCase:
    def __init__(self, repository: AuctionRepositoryInterface):
        self._repository = repository

    def execute(self, auction_id: str):
        auction = self._repository.find_by_id(auction_id)
        if auction is None:
            raise AuctionNotFoundError("Auction not found")
        auction.cancel()
        self._repository.save(auction)