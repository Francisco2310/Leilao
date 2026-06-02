import pytest
from application.use_cases.create_auction_use_case import CreateAuctionUseCase
from domain.ports.ports import IdGenerator
from infrastructure.repositories.in_memory_auction_repository import InMemoryAuctionRepository
from domain.entities.auction import AuctionStatus

class MockIdGenerator(IdGenerator):
    def __init__(self, fix_id="mock-id"):
        self.fix_id = fix_id
    def generate(self) -> str:
        return self.fix_id

class TestCreateAuctionUseCase:
    def setup_method(self):
        self.repository = InMemoryAuctionRepository()
        self.id_generator = MockIdGenerator("1")
        self.use_case = CreateAuctionUseCase(self.repository, self.id_generator)

    def test_create_auction_success(self):
        self.use_case.execute(seller_id="seller-id")
        auction = self.repository.find_by_id_for_update("1")
        assert auction.id == "1"
        assert auction.seller_id == "seller-id"
        assert auction.status == AuctionStatus.DRAFT
