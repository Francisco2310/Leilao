from datetime import datetime
import pytest
from application.use_cases.cancel_auction_use_case import CancelAuctionUseCase
from infrastructure.repositories.in_memory_auction_repository import InMemoryAuctionRepository
from domain.exceptions.domain_exceptions import AuctionInvalidStateTransitionError
from application.exceptions.application_exceptions import AuctionNotFoundError, UnauthorizedActionError
from domain.entities.auction import Auction, AuctionStatus
from domain.ports.ports import Clock

class MockClock(Clock):
    def __init__(self, current_time: datetime):
        self.current_time = current_time
    def now(self) -> datetime:
        return self.current_time

class MockIdGenerator:
    def generate(self) -> str:
        return "mock-id"

class TestCancelAuctionUseCase:
    def setup_method(self):
        self.repository = InMemoryAuctionRepository()
        self.clock = MockClock(datetime.now())
        self.use_case = CancelAuctionUseCase(self.repository, self.clock)
        self.id_generator = MockIdGenerator()
        
    def test_cancel_auction_success(self):
        auction = Auction(self.id_generator, "seller-id")
        self.repository.save(auction)
        
        self.use_case.execute(auction.id, "seller-id")
        assert auction.status == AuctionStatus.CANCELLED
        
    def test_cancel_auction_not_found(self):
        with pytest.raises(AuctionNotFoundError):
            self.use_case.execute("unexistent-id", "seller-id")
            
    def test_cancel_auction_unauthorized(self):
        auction = Auction(self.id_generator, "seller-id")
        self.repository.save(auction)
        
        with pytest.raises(UnauthorizedActionError):
            self.use_case.execute(auction.id, "hacker-id")
