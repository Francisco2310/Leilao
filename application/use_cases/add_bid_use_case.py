from application.ports.auction_repository import AuctionRepositoryInterface
from domain.Ports.ports import IdGenerator
from domain.Entities.bid import Bid
from domain.ValueObjects.money import Money, Currency
from application.exceptions.application_exceptions import AuctionNotFoundError
from domain.Ports.ports import Clock
from decimal import Decimal


class AddBidUseCase:
    def __init__(self, repository: AuctionRepositoryInterface, id_generator: IdGenerator, clock: Clock):
        self._repository = repository
        self._id_generator = id_generator
        self._clock = clock

    def execute(self, auction_id: str, user_id: str, amount: Decimal, currency: str):
        auction = self._repository.find_by_id_for_update(auction_id)
        if auction is None:
            raise AuctionNotFoundError("Auction not found")
        bid = Bid(Money(amount, Currency(currency)), user_id, self._id_generator)
        auction.add_bid(bid, self._clock)
        self._repository.save(auction)