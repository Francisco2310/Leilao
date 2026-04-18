from application.ports.auction_repository import AuctionRepositoryInterface
from application.exceptions.application_exceptions import AuctionNotFoundError
from domain.Ports.ports import Clock
from domain.ValueObjects.money import Money
from datetime import datetime
from decimal import Decimal

class StartAuctionUseCase:
    def __init__(self, repository: AuctionRepositoryInterface, clock: Clock):
        self._repository = repository
        self._clock = clock

    def execute(self, auction_id: str, minimum_bid: float, currency: str, product_id: str, expires_at: datetime, minimum_percentage: float):
        auction = self._repository.find_by_id(auction_id)
        if auction is None:
            raise AuctionNotFoundError("Auction not found")
        money = Money(Decimal(str(minimum_bid)), currency)
        auction.start(self._clock, money, product_id, expires_at, Decimal(str(minimum_percentage)))
        self._repository.save(auction)