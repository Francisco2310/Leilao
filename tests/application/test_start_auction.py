import pytest
from domain.Ports.ports import Clock
from datetime import datetime, timedelta
from infrastructure.repositories.in_memory_auction_repository import InMemoryAuctionRepository
from application.use_cases.start_auction_use_case import StartAuctionUseCase
from domain.Entities.auction import Auction, AuctionStatus
from domain.ValueObjects.money import Money
from domain.Ports.ports import IdGenerator
from decimal import Decimal
from application.exceptions.application_exceptions import AuctionNotFoundError

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


class TestStartAuctionUseCase:
    def setup_method(self):
        self.repository = InMemoryAuctionRepository()
        self.id_generator = MockIdGenerator("1")
        self.auction = Auction(self.id_generator, "seller-id")
        self.repository.save(self.auction)
        self.clock = MockClock(datetime.now())
        self.use_case = StartAuctionUseCase(self.repository, self.clock)

    def test_start_auction_success(self):
        self.use_case.execute(auction_id="1", minimum_bid=100.0, currency="BRL", product_id="1", expires_at=self.clock.now() + timedelta(days=1), minimum_percentage=0.10)
        auction = self.repository.find_by_id("1")
        assert auction.status == AuctionStatus.ACTIVE
        assert auction.minimum_bid == Money(Decimal("100.0"), "BRL")
        assert auction.product_id == "1"
        assert auction.expires_at == self.clock.now() + timedelta(days=1)
        assert auction.minimum_percentage == Decimal("0.10")

    def test_start_auction_not_found(self):
        with pytest.raises(AuctionNotFoundError):
            self.use_case.execute(auction_id="2", minimum_bid=100.0, currency="BRL", product_id="1", expires_at=self.clock.now() + timedelta(days=1), minimum_percentage=0.10)