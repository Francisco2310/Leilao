import pytest
from application.use_cases.get_active_auctions_use_case import GetActiveAuctionsUseCase
from infrastructure.repositories.in_memory_auction_repository import InMemoryAuctionRepository
from domain.Ports.ports import IdGenerator, Clock
from domain.Entities.auction import Auction
from domain.ValueObjects.money import Money
from decimal import Decimal
from datetime import datetime, timedelta

class MockClock(Clock):
    def __init__(self, current_time: datetime):
        self.current_time = current_time
    def now(self) -> datetime:
        return self.current_time

class MockIdGenerator(IdGenerator):
    def __init__(self, id: int):
        self.id = id
    def generate(self) -> str:
        self.id += 1
        return str(self.id)

class TestGetActiveAuctionsUseCase:
    def setup_method(self):
        self.repository = InMemoryAuctionRepository()
        self.use_case = GetActiveAuctionsUseCase(self.repository)
        self.id_generator = MockIdGenerator(0)
        self.clock = MockClock(datetime.now())

        for i in range(10):
            auction = Auction(self.id_generator, "seller-one")
            self.repository.save(auction)
            
        for i in range(5):
            auction = Auction(self.id_generator, "seller-one")
            auction.start(self.clock, Money(Decimal("100"), "USD"), "product-1", self.clock.now() + timedelta(days=2), Decimal("0.1"))
            self.repository.save(auction)
            
        for i in range(5):
            auction = Auction(self.id_generator, "seller-two")
            auction.start(self.clock, Money(Decimal("100"), "USD"), "product-2", self.clock.now() + timedelta(days=2), Decimal("0.1"))
            self.repository.save(auction)

    def test_get_active_auctions_success(self):
        result = self.use_case.execute(start_page=1, total_per_page=100)
        
        assert len(result) == 10
        for auction_dto in result:
            assert auction_dto.status == "active"
            assert auction_dto.seller_id in ["seller-one", "seller-two"]

    def test_get_active_auctions_pagination(self):
        result = self.use_case.execute(start_page=1, total_per_page=4)
        assert len(result) == 4
        for auction_dto in result:
            assert auction_dto.status == "active"

    def test_get_active_auctions_end_of_list(self):
        result = self.use_case.execute(start_page=5, total_per_page=10)
        assert len(result) == 0

    def test_get_active_auctions_invalid_page(self):
        with pytest.raises(ValueError):
            self.use_case.execute(start_page=0, total_per_page=10)

    def test_get_active_auctions_invalid_limit(self):
        with pytest.raises(ValueError):
            self.use_case.execute(start_page=1, total_per_page=0)
