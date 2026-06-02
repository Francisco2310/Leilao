from datetime import datetime
from abc import ABC
from decimal import Decimal

class DomainEvent(ABC):
    occurred_at: datetime

    def __init__(self, occurred_at: datetime):
        self.occurred_at = occurred_at

    def to_dict(self) -> dict:
        data = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, Decimal):
                data[key] = str(value)
            else:
                data[key] = value
        return data


class AuctionStartedEvent(DomainEvent):
    def __init__(self, auction_id: str, seller_id: str, product_id: str, reserve_price_amount: Decimal, reserve_price_currency: str, started_at: datetime, expires_at: datetime, occurred_at: datetime):
        super().__init__(occurred_at)
        self.auction_id = auction_id
        self.seller_id = seller_id
        self.product_id = product_id
        self.reserve_price_amount = reserve_price_amount
        self.reserve_price_currency = reserve_price_currency
        self.started_at = started_at
        self.expires_at = expires_at


class BidPlacedEvent(DomainEvent):
    def __init__(self, bid_id: str, auction_id: str, user_id: str, amount: Decimal, placed_at: datetime, currency: str, occurred_at: datetime):
        super().__init__(occurred_at)
        self.bid_id = bid_id
        self.auction_id = auction_id
        self.user_id = user_id
        self.amount = amount
        self.placed_at = placed_at
        self.currency = currency


class AuctionClosedEvent(DomainEvent):
    def __init__(self, auction_id: str, winner_id: str | None, closed_at: datetime, status: str, occurred_at: datetime):
        super().__init__(occurred_at)
        self.auction_id = auction_id
        self.winner_id = winner_id
        self.closed_at = closed_at
        self.status = status


class AuctionCancelledEvent(DomainEvent):
    def __init__(self, auction_id: str, cancelled_at: datetime, occurred_at: datetime):
        super().__init__(occurred_at)
        self.auction_id = auction_id
        self.cancelled_at = cancelled_at
