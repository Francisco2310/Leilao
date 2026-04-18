from abc import ABC, abstractmethod
from domain.Entities.auction import Auction

class AuctionRepositoryInterface(ABC):
    @abstractmethod
    def save(self, auction: Auction) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, auction_id: str) -> Auction | None:
        pass

    @abstractmethod
    def find_all(self, start_page: int, total_per_page: int, seller_id: str = None, status: str = None) -> list[Auction]:
        pass