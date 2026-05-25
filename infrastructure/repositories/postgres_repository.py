from application.ports.auction_repository import AuctionRepositoryInterface
from domain.Entities.auction import Auction
from domain.ValueObjects.money import Currency
from infrastructure.models.auction_model import AuctionModel
from infrastructure.models.bid_model import BidModel
from infrastructure.models.outbox_event_model import OutboxEventModel
from sqlalchemy.orm import Session

class AuctionRepository(AuctionRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, auction: Auction) -> None:
        auction_model = AuctionModel(
            id=auction.id,
            seller_id=auction.seller_id,
            status=auction.status.value,
            reserve_price_amount=auction.reserve_price.amount if auction.reserve_price else None,
            reserve_price_currency=auction.reserve_price.currency.value if auction.reserve_price else None,

            minimum_percentage=auction.minimum_percentage,
            product_id=auction.product_id,
            winner_id=auction.winner_id,
            started_at=auction.started_at,
            closed_at=auction.closed_at,
            expires_at=auction.expires_at
        )
        
        auction_model.bids = [
            BidModel(
                id=bid.id,
                user_id=bid.user_id,
                amount=bid.value.amount,
                currency=bid.value.currency.value if bid.value.currency else None,
                placed_at=bid.placed_at
            ) for bid in auction.bids
        ]
        
        events = [
            OutboxEventModel(
                event_type=event.__class__.__name__,
                payload=event.to_dict()
            ) for event in auction.events
        ]
        
        self.session.merge(auction_model)
        self.session.add_all(events)
        auction.clear_events()
    
    def find_by_id_for_update(self, auction_id: str) -> Auction | None:
        
        from sqlalchemy.orm import joinedload
        from domain.ValueObjects.money import Money
        from domain.Entities.auction import AuctionStatus
        from domain.Entities.bid import Bid

        auction_model = (
            self.session.query(AuctionModel)
            .options(joinedload(AuctionModel.bids))
            .filter_by(id=auction_id)
            .with_for_update(of=AuctionModel)
            .first()
        )

        if not auction_model:
            return None

        domain_bids = []
        for bid_model in auction_model.bids:
            bid = Bid.restore(
                id=bid_model.id,
                user_id=bid_model.user_id,
                value=Money(amount=bid_model.amount, currency=Currency(bid_model.currency)),
                placed_at=bid_model.placed_at
            )
            domain_bids.append(bid)

        reserve_price = None
        if auction_model.reserve_price_amount is not None and auction_model.reserve_price_currency is not None:
            reserve_price = Money(amount=auction_model.reserve_price_amount, currency=Currency(auction_model.reserve_price_currency))
        return Auction.restore(
            id=auction_model.id,
            seller_id=auction_model.seller_id,
            status=AuctionStatus(auction_model.status),
            reserve_price=reserve_price,
            minimum_percentage=auction_model.minimum_percentage,
            product_id=auction_model.product_id,
            winner_id=auction_model.winner_id,
            started_at=auction_model.started_at,
            closed_at=auction_model.closed_at,
            expires_at=auction_model.expires_at,
            bids=domain_bids
        )

    def find_all(self, limit: int, cursor: str | None = None, seller_id: str | None = None, status: str | None = None) -> list[Auction]:
      
        from sqlalchemy.orm import joinedload
        from domain.ValueObjects.money import Money
        from domain.Entities.auction import AuctionStatus
        from domain.Entities.bid import Bid

        query = self.session.query(AuctionModel).options(joinedload(AuctionModel.bids))

        if seller_id:
            query = query.filter(AuctionModel.seller_id == seller_id)
        if status:
            query = query.filter(AuctionModel.status == status)
        if cursor:
            query = query.filter(AuctionModel.id < cursor)

        auction_models = query.order_by(AuctionModel.id.desc()).limit(limit).all()
        
        if not auction_models:
            return []

        auctions = []
        for auction_model in auction_models:
          reserve_price = None
          if auction_model.reserve_price_amount is not None and auction_model.reserve_price_currency is not None:
              reserve_price = Money(amount=auction_model.reserve_price_amount, currency=Currency(auction_model.reserve_price_currency))

          domain_bids = []
          for bid_model in auction_model.bids:
            bid = Bid.restore(
              id=bid_model.id,
              user_id=bid_model.user_id,
              value=Money(amount=bid_model.amount, currency=Currency(bid_model.currency)),
              placed_at=bid_model.placed_at
            )
            domain_bids.append(bid)
            
          auctions.append(Auction.restore(
            id=auction_model.id,
            seller_id=auction_model.seller_id,
            status=AuctionStatus(auction_model.status),
            reserve_price=reserve_price,
            minimum_percentage=auction_model.minimum_percentage,
            product_id=auction_model.product_id,
            winner_id=auction_model.winner_id,
            started_at=auction_model.started_at,
            closed_at=auction_model.closed_at,
            expires_at=auction_model.expires_at,
            bids=domain_bids
          ))
        return auctions