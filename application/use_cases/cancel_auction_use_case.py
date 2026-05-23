from application.ports.auction_repository import AuctionRepositoryInterface
from application.exceptions.application_exceptions import AuctionNotFoundError, UnauthorizedActionError

class CancelAuctionUseCase:
    def __init__(self, repository: AuctionRepositoryInterface):
        self._repository = repository

    def execute(self, auction_id: str, seller_id: str):
        auction = self._repository.find_by_id_for_update(auction_id)
        if auction is None:
            raise AuctionNotFoundError("Auction not found")
        if auction.seller_id != seller_id:
            raise UnauthorizedActionError("Only the seller can cancel the auction")
        auction.cancel()
        self._repository.save(auction)