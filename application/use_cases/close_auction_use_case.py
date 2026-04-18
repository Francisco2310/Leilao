from application.ports.auction_repository import AuctionRepositoryInterface
from application.exceptions.application_exceptions import AuctionNotFoundError
from domain.Ports.ports import Clock

class CloseAuctionUseCase:
    def __init__(self, repository: AuctionRepositoryInterface, clock: Clock):
        self._repository = repository
        self._clock = clock

    def execute(self, auction_id: str):
        auction = self._repository.find_by_id(auction_id)
        if auction is None:
            raise AuctionNotFoundError("Auction not found")
        auction.close(self._clock)
        self._repository.save(auction)