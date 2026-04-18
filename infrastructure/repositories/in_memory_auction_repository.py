from domain.Entities.auction import Auction
from application.ports.auction_repository import AuctionRepositoryInterface

class InMemoryAuctionRepository(AuctionRepositoryInterface):
    def __init__(self):
        self._db: dict[str, Auction] = {}

    def save(self, auction: Auction):
        self._db[auction.id] = auction

    def find_by_id(self, auction_id: str):
        return self._db.get(auction_id)

    def find_all(self, start_page: int, total_per_page: int, seller_id: str = None, status: str = None):
        auctions = list(self._db.values())
        
        if seller_id:
            auctions = [a for a in auctions if a.seller_id == seller_id]
        if status:
            auctions = [a for a in auctions if a.status.value == status or a.status == status]
            
        start = (start_page - 1) * total_per_page
        return auctions[start:start + total_per_page]