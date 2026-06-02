import pytest
from domain.ports.ports import Clock
from datetime import datetime, timedelta
from infrastructure.repositories.in_memory_auction_repository import InMemoryAuctionRepository
from application.use_cases.start_auction_use_case import StartAuctionUseCase
from domain.entities.auction import Auction, AuctionStatus
from domain.value_objects.money import Money
from domain.ports.ports import IdGenerator
from decimal import Decimal
from application.exceptions.application_exceptions import AuctionNotFoundError, UnauthorizedActionError

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
        self.use_case.execute(auction_id="1", seller_id="seller-id", reserve_price=Decimal("100.0"), currency="BRL", product_id="1", expires_at=self.clock.now() + timedelta(days=1), minimum_percentage=Decimal("0.10"))
        auction = self.repository.find_by_id_for_update("1")
        assert auction.status == AuctionStatus.ACTIVE
        assert auction.reserve_price == Money(Decimal("100.0"), "BRL")
        assert auction.product_id == "1"
        assert auction.expires_at == self.clock.now() + timedelta(days=1)
        assert auction.minimum_percentage == Decimal("0.10")

    def test_start_auction_not_found(self):
        with pytest.raises(AuctionNotFoundError):
            self.use_case.execute(auction_id="2", seller_id="seller-id", reserve_price=Decimal("100.0"), currency="BRL", product_id="1", expires_at=self.clock.now() + timedelta(days=1), minimum_percentage=Decimal("0.10"))

    def test_start_auction_unauthorized(self):
        with pytest.raises(UnauthorizedActionError):
            self.use_case.execute(auction_id="1", seller_id="invasor-id", reserve_price=Decimal("100.0"), currency="BRL", product_id="1", expires_at=self.clock.now() + timedelta(days=1), minimum_percentage=Decimal("0.10"))