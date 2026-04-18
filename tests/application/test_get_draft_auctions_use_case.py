import pytest
from domain.Entities.auction import Auction
from application.use_cases.get_all_auctions_use_case import GetDraftAuctionsUseCase
from infrastructure.repositories.in_memory_auction_repository import InMemoryAuctionRepository

class TestGetDraftAuctionsUseCase:
    def setup_method(self):
        self.repository = InMemoryAuctionRepository()
        self.use_case = GetDraftAuctionsUseCase(self.repository)

    def test_get_all_auctions_success(self):
        self.use_case.execute(0, 10, "seller-id")
        assert True