import pytest
from datetime import datetime, timedelta
from application.use_cases.close_auction_use_case import CloseAuctionUseCase
from infrastructure.repositories.in_memory_auction_repository import InMemoryAuctionRepository
from application.exceptions.application_exceptions import AuctionNotFoundError
from domain.Entities.auction import Auction, AuctionStatus
from domain.Ports.ports import Clock, IdGenerator
from domain.ValueObjects.money import Money
from decimal import Decimal

class MockClock(Clock):
    def __init__(self, current_time: datetime):
        self.current_time = current_time
    def now(self) -> datetime:
        return self.current_time

class MockIdGenerator(IdGenerator):
    def __init__(self, fixed_id="mock-id"):
        self.fixed_id = fixed_id
    def generate(self) -> str:
        return self.fixed_id

class TestCloseAuctionUseCase:
    def setup_method(self):
        self.repository = InMemoryAuctionRepository()
        self.clock = MockClock(datetime.now())
        self.use_case = CloseAuctionUseCase(self.repository, self.clock)
        self.id_generator = MockIdGenerator("auction-test-1")
        
    def test_close_auction_success(self):
        auction = Auction(self.id_generator, "seller-id")
        expires = self.clock.now() + timedelta(hours=2)
        auction.start(self.clock, Money(Decimal("10.0"), "BRL"), "product-id", expires, Decimal("0.10"))
        self.repository.save(auction)
        
        self.clock.current_time += timedelta(hours=3)
        
        self.use_case.execute(auction.id)
        
        saved_auction = self.repository.find_by_id_for_update(auction.id)
        assert saved_auction.status == AuctionStatus.CANCELLED
        
    def test_close_auction_not_found(self):
        with pytest.raises(AuctionNotFoundError):
            self.use_case.execute("unexistent-id")
