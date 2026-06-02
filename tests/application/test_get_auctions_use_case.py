import pytest
from application.use_cases.get_auctions_use_case import GetAuctionsUseCase
from infrastructure.repositories.in_memory_auction_repository import InMemoryAuctionRepository
from domain.ports.ports import IdGenerator, Clock
from domain.entities.auction import Auction
from domain.value_objects.money import Money
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
        return f"{self.id:04d}"

class TestGetAuctionsUseCase:
    def setup_method(self):
        self.repository = InMemoryAuctionRepository()
        self.use_case = GetAuctionsUseCase(self.repository)
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
        result = self.use_case.execute(limit=100, status="active")
        
        assert len(result) == 10
        for auction_dto in result:
            assert auction_dto.status == "active"

    def test_get_auctions_cursor_pagination(self):
        page_1 = self.use_case.execute(limit=4)
        assert len(page_1) == 4
        
        cursor = page_1[-1].id
        
        page_2 = self.use_case.execute(limit=4, cursor=cursor)
        assert len(page_2) == 4
        
        page_1_ids = [a.id for a in page_1]
        page_2_ids = [a.id for a in page_2]
        
        assert not set(page_1_ids).intersection(page_2_ids)
        assert page_2[0].id < cursor

    def test_get_auctions_cursor_at_end_of_list(self):
        all_auctions = self.use_case.execute(limit=100)
        oldest_id = all_auctions[-1].id
        
        result = self.use_case.execute(limit=5, cursor=oldest_id)
        assert len(result) == 0

    def test_get_auctions_invalid_limit(self):
        from application.exceptions.application_exceptions import ApplicationException
        with pytest.raises(ApplicationException):
            self.use_case.execute(limit=0)

    def test_get_seller_auctions_success(self):
        result = self.use_case.execute(limit=100, seller_id="seller-one")
        
        assert len(result) == 15
        for auction_dto in result:
            assert auction_dto.seller_id == "seller-one"

    def test_get_auctions_combined_filter(self):
        result = self.use_case.execute(limit=100, seller_id="seller-one", status="active")
        
        assert len(result) == 5
        for auction_dto in result:
            assert auction_dto.seller_id == "seller-one"
            assert auction_dto.status == "active"

    def test_get_auctions_non_existent_seller(self):
        result = self.use_case.execute(limit=100, seller_id="ghost")
        assert len(result) == 0

    def test_get_auctions_non_existent_status(self):
        result = self.use_case.execute(limit=100, status="closed")
        assert len(result) == 0
