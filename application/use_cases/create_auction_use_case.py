from application.ports.auction_repository import AuctionRepositoryInterface
from domain.Ports.ports import IdGenerator
from domain.Entities.auction import Auction

class CreateAuctionUseCase:
    def __init__(self, repository: AuctionRepositoryInterface, id_generator: IdGenerator):
        self._repository = repository
        self._id_generator = id_generator

    def execute(self, seller_id: str):
        auction = Auction(self._id_generator, seller_id)
        self._repository.save(auction)
        return auction.id