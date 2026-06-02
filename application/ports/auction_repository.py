from abc import ABC, abstractmethod
from domain.entities.auction import Auction

class AuctionRepositoryInterface(ABC):
    @abstractmethod
    def save(self, auction: Auction) -> None:
        pass
    
    @abstractmethod
    def find_by_id_for_update(self, auction_id: str) -> Auction | None:
        pass

    @abstractmethod
    def find_all(self, limit: int, cursor: str | None = None, seller_id: str | None = None, status: str | None = None) -> list[Auction]:
        pass