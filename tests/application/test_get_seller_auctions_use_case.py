import pytest
from domain.Entities.auction import Auction
from application.use_cases.get_seller_auctions_use_case import GetSellerAuctionsUseCase
from infrastructure.repositories.in_memory_auction_repository import InMemoryAuctionRepository
from domain.Ports.ports import IdGenerator
from domain.Entities.auction import AuctionStatus
from domain.ValueObjects.money import Money
from decimal import Decimal
from datetime import datetime, timedelta
from domain.Ports.ports import Clock

class MockClock(Clock):
    def __init__(self, current_time: datetime):
        self.current_time = current_time
    def now(self) -> datetime:
        return self.current_time


class mockIdGenerator(IdGenerator):
    def __init__(self, id: int):
        self.id = id
    def generate(self) -> str:
        self.id += 1
        return str(self.id)

class TestGetSellerAuctionsUseCase:
    def setup_method(self):
        self.repository = InMemoryAuctionRepository()
        self.use_case = GetSellerAuctionsUseCase(self.repository)
        self.id_generator = mockIdGenerator(0)
        self.clock = MockClock(datetime.now())

        for i in range(10):
            self.auction = Auction(self.id_generator, "seller-id")
            self.repository.save(self.auction)
        for i in range(10):
            self.auction = Auction(self.id_generator, "other-seller")
            self.repository.save(self.auction)
        for i in range(10):
            self.auction = Auction(self.id_generator, "seller-id")
            self.auction.start(self.clock, Money(Decimal("100.0"), "BRL"), "product-id", self.clock.now() + timedelta(days=1), Decimal("0.10"))
            self.repository.save(self.auction)

    def test_get_seller_auctions_success(self):
        total_per_page = 10
        start_page = 1
        result = self.use_case.execute(start_page, total_per_page, "seller-id")
        assert len(result) == 10
        for auction in result:
            assert auction.status == "draft"
            assert auction.seller_id == "seller-id"

    def test_get_seller_auctions_pagination(self):
        total_per_page = 5
        start_page = 1
        result = self.use_case.execute(start_page, total_per_page, "seller-id")
        assert len(result) == 5
        for auction in result:
            assert auction.status == "draft"
            assert auction.seller_id == "seller-id"

    def test_get_seller_auctions_empty(self):
        total_per_page = 10
        start_page = 1
        result = self.use_case.execute(start_page, total_per_page, "inactive-seller")
        assert len(result) == 0

    def test_get_seller_auctions_invalid_page(self):
        total_per_page = 10
        start_page = 0
        with pytest.raises(ValueError):
            self.use_case.execute(start_page, total_per_page, "seller-id")

    def test_get_seller_auctions_invalid_total_per_page(self):
        total_per_page = 0
        start_page = 1
        with pytest.raises(ValueError):
            self.use_case.execute(start_page, total_per_page, "seller-id")

    def test_get_seller_auctions_invalid_seller_id(self):
        total_per_page = 10
        start_page = 1
        with pytest.raises(ValueError):
            self.use_case.execute(start_page, total_per_page, "")

    def test_get_seller_auctions_pagination_end_of_list(self):
        total_per_page = 5
        start_page = 3
        result = self.use_case.execute(start_page, total_per_page, "seller-id")
        assert len(result) == 0

    def test_get_seller_auctions_active_only(self):
        total_per_page = 10
        start_page = 1
        result = self.use_case.execute(start_page, total_per_page, "seller-id", status="active")
        
        assert len(result) == 10
        for auction in result:
            assert auction.status == "active"
            assert auction.seller_id == "seller-id"
