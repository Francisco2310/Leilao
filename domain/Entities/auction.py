from domain.Entities.bid import Bid
from enum import Enum
from domain.Ports.ports import IdGenerator, Clock
from domain.ValueObjects.money import Money
from domain.Exceptions.domain_exceptions import AuctionNotActiveError, AuctionInvalidStateTransitionError, BidTooLowError, SelfBidError, AuctionExpiredError, InvalidAuctionConfigurationError
from datetime import datetime, timedelta
from decimal import Decimal

class AuctionStatus(Enum):
  CANCELLED = "cancelled"
  DRAFT = "draft"
  ACTIVE = "active"
  CLOSED = "closed"

class Auction:
  id: str
  bids: list[Bid]
  status: AuctionStatus
  minimum_bid: Money | None
  minimum_percentage: Decimal | None
  product_id: str | None
  seller_id: str
  winner_id: str | None
  started_at: datetime | None
  closed_at: datetime | None
  expires_at: datetime | None
  MINIMUM_DURATION = timedelta(hours=1)
  MINIMUM_BID_VALUE = 1

  def __init__(self, id: IdGenerator, seller_id: str):
    self.id = id.generate()
    self.seller_id = seller_id
    self.status = AuctionStatus.DRAFT
    self.bids = []
    self.minimum_bid = None
    self.minimum_percentage = None
    self.product_id = None
    self.winner_id = None
    self.started_at = None
    self.closed_at = None
    self.expires_at = None


  @property
  def highest_bid(self) -> Bid | None:
    if not self.bids:
      return None
    return max(self.bids, key=lambda b: b.value.amount)

  def add_bid(self, bid: Bid, clock: Clock):
    now = clock.now()
    
    if self.status != AuctionStatus.ACTIVE:
      raise AuctionNotActiveError("Auction must be active to add bids")

    if self.expires_at < now:
      raise AuctionExpiredError("Auction has expired")
      
    time_left = self.expires_at - now
      
    if bid.user_id == self.seller_id:
      raise SelfBidError("Seller cannot bid on their own auction")

    if self.bids:
      minimo_para_bater = self.highest_bid.value.amount * (Decimal('1') + self.minimum_percentage)
      if bid.value.amount < minimo_para_bater:
        raise BidTooLowError("Bid value must be greater than current highest bid plus minimum percentage")
    else:
      if bid.value.amount < self.MINIMUM_BID_VALUE:
        raise BidTooLowError("Bid value must be greater than minimum bid value")

    self.bids.append(bid)
    
    if time_left <= timedelta(seconds=30):
      self.expires_at += timedelta(minutes=2)

  def cancel(self):
    if self.status not in (AuctionStatus.DRAFT, AuctionStatus.ACTIVE):
      raise AuctionInvalidStateTransitionError("Auction must be in draft or active to be cancelled")
    self.status = AuctionStatus.CANCELLED

  def close(self, clock: Clock):
    if self.status != AuctionStatus.ACTIVE:
      raise AuctionInvalidStateTransitionError("Auction must be active to be closed")
    if not self.bids:
      self.cancel()
      return
    
    if self.highest_bid.value < self.minimum_bid:
      self.cancel()
      return
    
    self.winner_id = self.highest_bid.user_id
    self.status = AuctionStatus.CLOSED
    self.closed_at = clock.now()

  def start(self, clock: Clock, minimum_bid: Money, product_id: str, expires_at: datetime, minimum_percentage: Decimal):
    if self.status != AuctionStatus.DRAFT:
      raise AuctionInvalidStateTransitionError("Auction must be in draft to be started")
      
    if product_id is None:
      raise InvalidAuctionConfigurationError("Product ID must be provided")
    if expires_at is None:
      raise InvalidAuctionConfigurationError("Expires at must be provided")
    if minimum_percentage is None:
      raise InvalidAuctionConfigurationError("Minimum percentage must be provided")
    if minimum_bid is None:
      raise InvalidAuctionConfigurationError("Minimum bid must be provided")

    if expires_at < clock.now() + Auction.MINIMUM_DURATION:
      raise InvalidAuctionConfigurationError("Auction must last at least 1 hour")
    if minimum_bid.amount <= 0:
      raise InvalidAuctionConfigurationError("Minimum bid must be positive")
    if minimum_percentage <= 0 or minimum_percentage > 1:
      raise InvalidAuctionConfigurationError("Minimum percentage must be between 0 and 1")

    self.minimum_percentage = minimum_percentage
    self.status = AuctionStatus.ACTIVE
    self.minimum_bid = minimum_bid
    self.product_id = product_id
    self.started_at = clock.now()
    self.expires_at = expires_at