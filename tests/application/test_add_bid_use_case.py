import pytest
from domain.Ports.ports import IdGenerator
from domain.Ports.ports import Clock
from datetime import datetime, timedelta
from application.use_cases.add_bid_use_case import AddBidUseCase
from infrastructure.repositories.in_memory_auction_repository import InMemoryAuctionRepository
from application.exceptions.application_exceptions import AuctionNotFoundError
from domain.Entities.auction import Auction
from domain.ValueObjects.money import Money
from decimal import Decimal

class MockClock(Clock):
    def __init__(self, current_time: datetime):
        self.current_time = current_time
    def now(self) -> datetime:
        return self.current_time


class MockIdGenerator(IdGenerator):
    def __init__(self, fix_id="mock-id"):
        self.fix_id = fix_id
    def generate(self) -> str:
        return self.fix_id

  
class TestAddBidUseCase:
    def setup_method(self):
        self.repository = InMemoryAuctionRepository()
        self.id_generator = MockIdGenerator("1")
        self.clock = MockClock(datetime.now())
        self.auction = Auction(self.id_generator, "seller-id")
        self.auction.start(self.clock, Money(Decimal("100.0"), "BRL"), "product-id", self.clock.now() + timedelta(days=1), Decimal("0.10"))
        self.repository.save(self.auction)
        self.use_case = AddBidUseCase(self.repository, self.id_generator, self.clock)

    def test_add_bid_success(self):
        self.use_case.execute("1", "user-id", 100.0, "BRL")
        auction = self.repository.find_by_id("1")
        assert auction.bids[0].value == Money(Decimal("100.0"), "BRL")
        assert auction.bids[0].user_id == "user-id"
        assert auction.bids[0].id == "1"

    def test_add_bid_not_found(self):
        with pytest.raises(AuctionNotFoundError):
            self.use_case.execute("2", "user-id", 100.0, "BRL")
