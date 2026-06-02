from domain.entities.bid import Bid
from enum import Enum
from domain.ports.ports import IdGenerator, Clock
from domain.value_objects.money import Money
from domain.exceptions.domain_exceptions import AuctionNotActiveError, AuctionInvalidStateTransitionError, BidTooLowError, SelfBidError, AuctionExpiredError, InvalidAuctionConfigurationError, AuctionNotExpiredError
from datetime import datetime, timedelta
from decimal import Decimal
from domain.events.domain_event import DomainEvent, AuctionStartedEvent, BidPlacedEvent, AuctionClosedEvent, AuctionCancelledEvent


class AuctionStatus(Enum):
  CANCELLED = "cancelled"
  DRAFT = "draft"
  ACTIVE = "active"
  CLOSED = "closed"

class Auction:
  id: str
  bids: list[Bid]
  status: AuctionStatus
  reserve_price: Money | None
  minimum_percentage: Decimal | None
  product_id: str | None
  seller_id: str
  winner_id: str | None
  started_at: datetime | None
  closed_at: datetime | None
  expires_at: datetime | None
  events: list[DomainEvent]
  
  MINIMUM_DURATION = timedelta(hours=1)
  MINIMUM_BID_VALUE = 1

  def __init__(self, id: IdGenerator, seller_id: str):
    self.id = id.generate()
    self.seller_id = seller_id
    self.status = AuctionStatus.DRAFT
    self.bids = []
    self.reserve_price = None
    self.minimum_percentage = None
    self.product_id = None
    self.winner_id = None
    self.started_at = None
    self.closed_at = None
    self.expires_at = None
    self.events = []

  def clear_events(self):
    self.events = []

  def __eq__(self, other: object) -> bool:
    if not isinstance(other, Auction):
      return NotImplemented
    return self.id == other.id

  def __hash__(self) -> int:
    return hash(self.id)

  @property
  def highest_bid(self) -> Bid | None:
    if not self.bids:
      return None
    return max(self.bids, key=lambda b: b.value.amount)

  def add_bid(self, bid: Bid, clock: Clock):
    now = clock.now()
    
    if self.status != AuctionStatus.ACTIVE:
      raise AuctionNotActiveError("Auction must be active to add bids")

    if self.expires_at is None:
      raise AuctionNotActiveError("Auction expiration time is not set")
    if self.minimum_percentage is None:
      raise AuctionNotActiveError("Auction minimum percentage is not configured")

    if self.expires_at <= now:
      raise AuctionExpiredError("Auction has expired")
      
    time_left = self.expires_at - now
      
    if bid.user_id == self.seller_id:
      raise SelfBidError("Seller cannot bid on their own auction")

    if self.bids:
      if self.highest_bid is None:
        raise AuctionNotActiveError("Expected highest bid but none found")
      min_outbid_amount = self.highest_bid.value.amount * (Decimal('1') + self.minimum_percentage)
      if bid.value.amount < min_outbid_amount:
        raise BidTooLowError("Bid value must be greater than current highest bid plus minimum percentage")
    else:
      min_starting_amount = Decimal(str(self.MINIMUM_BID_VALUE)) * (Decimal('1') + self.minimum_percentage)
      if bid.value.amount < min_starting_amount:
        raise BidTooLowError("Bid value must be greater than or equal to the minimum starting bid")

    bid.placed_at = now
    self.bids.append(bid)
    self.events.append(
      BidPlacedEvent(
        bid_id=bid.id,
        auction_id=self.id,
        user_id=bid.user_id,
        amount=bid.value.amount,
        currency=bid.value.currency.value,
        placed_at=bid.placed_at,
        occurred_at=bid.placed_at
      )
    )
    
    if time_left <= timedelta(seconds=30):
      self.expires_at += timedelta(minutes=2)

  def cancel(self, clock: Clock):
    if self.status not in (AuctionStatus.DRAFT, AuctionStatus.ACTIVE):
      raise AuctionInvalidStateTransitionError("Auction must be in draft or active to be cancelled")
    now = clock.now()
    self.status = AuctionStatus.CANCELLED
    self.events.append(
      AuctionCancelledEvent(
        auction_id=self.id,
        cancelled_at=now,
        occurred_at=now
      )
    )

  def close(self, clock: Clock):
    if self.status != AuctionStatus.ACTIVE:
      raise AuctionInvalidStateTransitionError("Auction must be active to be closed")

    if self.expires_at is None:
      raise AuctionNotActiveError("Auction expiration time is not set")
    if self.reserve_price is None:
      raise AuctionNotActiveError("Auction reserve price is not set")

    if self.expires_at > clock.now():
      raise AuctionNotExpiredError("Auction has not expired yet")
    if not self.bids:
      self.cancel(clock)
      return
    
    if self.highest_bid is None:
      raise AuctionNotActiveError("Expected highest bid but none found")
    if self.highest_bid.value < self.reserve_price:
      self.cancel(clock)
      return
    
    self.winner_id = self.highest_bid.user_id
    self.status = AuctionStatus.CLOSED
    self.closed_at = clock.now()
    self.events.append(
      AuctionClosedEvent(
        auction_id=self.id,
        winner_id=self.winner_id,
        closed_at=self.closed_at,
        status=str(self.status),
        occurred_at=self.closed_at
      )
    )

  def start(self, clock: Clock, reserve_price: Money, product_id: str, expires_at: datetime, minimum_percentage: Decimal):
    if self.status != AuctionStatus.DRAFT:
      raise AuctionInvalidStateTransitionError("Auction must be in draft to be started")
      
    if product_id is None:
      raise InvalidAuctionConfigurationError("Product ID must be provided")
    if expires_at is None:
      raise InvalidAuctionConfigurationError("Expires at must be provided")
    if minimum_percentage is None:
      raise InvalidAuctionConfigurationError("Minimum percentage must be provided")
    if reserve_price is None:
      raise InvalidAuctionConfigurationError("Reserve price must be provided")

    if expires_at < clock.now() + Auction.MINIMUM_DURATION:
      raise InvalidAuctionConfigurationError("Auction must last at least 1 hour")
    if reserve_price.amount <= 0:
      raise InvalidAuctionConfigurationError("Reserve price must be positive")
    if minimum_percentage <= 0 or minimum_percentage > 1:
      raise InvalidAuctionConfigurationError("Minimum percentage must be between 0 and 1")

    self.minimum_percentage = minimum_percentage
    self.status = AuctionStatus.ACTIVE
    self.reserve_price = reserve_price
    self.product_id = product_id
    self.started_at = clock.now()
    self.expires_at = expires_at
    self.events.append(
      AuctionStartedEvent(
        auction_id=self.id,
        seller_id=self.seller_id,
        product_id=self.product_id,
        reserve_price_amount=self.reserve_price.amount,
        reserve_price_currency=self.reserve_price.currency.value,
        started_at=self.started_at,
        expires_at=self.expires_at,
        occurred_at=self.started_at
      )
    )


  @classmethod
  def restore(cls, id: str, seller_id: str, status: AuctionStatus, reserve_price: Money | None, minimum_percentage: Decimal | None, product_id: str | None, winner_id: str | None, started_at: datetime | None, closed_at: datetime | None, expires_at: datetime | None, bids: list[Bid] | None = None):

    auction = cls.__new__(cls)
    auction.id = id
    auction.seller_id = seller_id
    auction.status = status
    auction.reserve_price = reserve_price
    auction.minimum_percentage = minimum_percentage
    auction.product_id = product_id
    auction.winner_id = winner_id
    auction.started_at = started_at
    auction.closed_at = closed_at
    auction.expires_at = expires_at
    auction.bids = bids if bids is not None else []
    auction.events = []
    
    return auction

