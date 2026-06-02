from domain.entities.auction import Auction
from application.ports.auction_repository import AuctionRepositoryInterface

class InMemoryAuctionRepository(AuctionRepositoryInterface):
    def __init__(self):
        self._db: dict[str, Auction] = {}

    def save(self, auction: Auction):
        self._db[auction.id] = auction

    def find_by_id_for_update(self, auction_id: str):
        return self._db.get(auction_id)

    def find_all(self, limit: int, cursor: str | None = None, seller_id: str | None = None, status: str | None = None):
        auctions = sorted(self._db.values(), key=lambda a: a.id, reverse=True)
        
        if cursor:
            auctions = [a for a in auctions if a.id < cursor]
        if seller_id:
            auctions = [a for a in auctions if a.seller_id == seller_id]
        if status:
            auctions = [a for a in auctions if a.status.value == status or a.status == status]
            
        return auctions[:limit]