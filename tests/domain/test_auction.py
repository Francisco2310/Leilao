import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from domain.Entities.auction import Auction, AuctionStatus
from domain.ValueObjects.money import Money, Currency
from domain.Entities.bid import Bid
from domain.Exceptions.domain_exceptions import AuctionNotActiveError, InvalidAuctionConfigurationError, SelfBidError, BidTooLowError, NegativeAmountError, AuctionExpiredError, AuctionInvalidStateTransitionError, AuctionNotExpiredError
from domain.Ports.ports import IdGenerator, Clock

class MockIdGenerator(IdGenerator):
    def __init__(self, fix_id="mock-id"):
        self.fix_id = fix_id
    def generate(self) -> str:
        return self.fix_id

class MockClock(Clock):
    def __init__(self, current_time: datetime):
        self.current_time = current_time
    def now(self) -> datetime:
        return self.current_time

def test_auction_initial_state():
    id_generator = MockIdGenerator()
    clock = MockClock(datetime.now())
    auction = Auction(id_generator, "seller-id")
    assert auction.status == AuctionStatus.DRAFT
    assert auction.seller_id == "seller-id"
    assert auction.bids == []
    assert auction.reserve_price is None
    assert auction.minimum_percentage is None
    assert auction.product_id is None
    assert auction.winner_id is None
    assert auction.started_at is None
    assert auction.closed_at is None
    assert auction.expires_at is None

def test_auction_start_valid_configuration():
    id_generator = MockIdGenerator()
    clock = MockClock(datetime.now())
    now = clock.now()
    auction = Auction(id_generator, "seller-id")
    auction.start(clock, Money(100, Currency.BRL), "product-id", now + timedelta(days=1), Decimal('0.1'))
    assert auction.status == AuctionStatus.ACTIVE
    assert auction.reserve_price == Money(100, Currency.BRL)
    assert auction.minimum_percentage == Decimal('0.1')
    assert auction.product_id == "product-id"
    assert auction.expires_at == now + timedelta(days=1)
    assert auction.started_at == now

def test_auction_start_invalid_configuration_expired_date():
    id_generator = MockIdGenerator()
    clock = MockClock(datetime.now())
    now = clock.now()
    auction = Auction(id_generator, "seller-id")
    with pytest.raises(InvalidAuctionConfigurationError):
        auction.start(clock, Money(100, Currency.BRL), "product-id", now, Decimal('0.1'))

def test_auction_start_invalid_configuration_minimum_bid():
    id_generator = MockIdGenerator()
    clock = MockClock(datetime.now())
    now = clock.now()
    auction = Auction(id_generator, "seller-id")
    with pytest.raises(InvalidAuctionConfigurationError):
        auction.start(clock, Money(0, Currency.BRL), "product-id", now + timedelta(days=1), Decimal('0.1'))

def test_auction_start_invalid_configuration_minimum_percentage():
    id_generator = MockIdGenerator()
    clock = MockClock(datetime.now())
    now = clock.now()
    auction = Auction(id_generator, "seller-id")
    with pytest.raises(InvalidAuctionConfigurationError):
        auction.start(clock, Money(100, Currency.BRL), "product-id", now + timedelta(days=1), Decimal('0'))
    with pytest.raises(InvalidAuctionConfigurationError):
        auction.start(clock, Money(100, Currency.BRL), "product-id", now + timedelta(days=1), Decimal('2'))


def test_double_activate():
    id_generator = MockIdGenerator()
    clock = MockClock(datetime.now())
    now = clock.now()
    auction = Auction(id_generator, "seller-id")
    auction.start(clock, Money(100, Currency.BRL), "product-id", now + timedelta(days=1), Decimal('0.1'))
    with pytest.raises(AuctionInvalidStateTransitionError):
        auction.start(clock, Money(100, Currency.BRL), "product-id", now + timedelta(days=1), Decimal('0.1'))


def test_bid_add_draft_state():
    id_generator = MockIdGenerator()
    clock = MockClock(datetime.now())
    auction = Auction(id_generator, "seller-id")
    with pytest.raises(AuctionNotActiveError):
        auction.add_bid(Bid(Money(100, Currency.BRL), "user-id", id_generator), clock)

def test_bid_add_active_state():
    id_generator = MockIdGenerator()
    clock = MockClock(datetime.now())
    now = clock.now()
    auction = Auction(id_generator, "seller-id")
    auction.start(clock, Money(100, Currency.BRL), "product-id", now + timedelta(days=1), Decimal('0.1'))
    auction.add_bid(Bid(Money(100, Currency.BRL), "user-id", id_generator), clock)
    
    assert len(auction.bids) == 1
    assert auction.bids[0].value.amount == 100
    assert auction.bids[0].user_id == "user-id"

def test_bid_seller_add_bid():
    id_generator = MockIdGenerator()
    clock = MockClock(datetime.now())
    now = clock.now()
    auction = Auction(id_generator, "seller-id")
    auction.start(clock, Money(100, Currency.BRL), "product-id", now + timedelta(days=1), Decimal('0.1'))
    with pytest.raises(SelfBidError):
        auction.add_bid(Bid(Money(110, Currency.BRL), "seller-id", id_generator), clock)

def test_bid_lower_than_minimum_bid():
    id_generator = MockIdGenerator()
    clock = MockClock(datetime.now())
    now = clock.now()
    auction = Auction(id_generator, "seller-id")
    auction.start(clock, Money(100, Currency.BRL), "product-id", now + timedelta(days=1), Decimal('0.1'))
    
    with pytest.raises(BidTooLowError):
        auction.add_bid(Bid(Money(Decimal('0.50'), Currency.BRL), "user-id", id_generator), clock)

def test_bid_second_bid_higher_than_first_bid():
    id_generator = MockIdGenerator()
    clock = MockClock(datetime.now())
    now = clock.now()
    auction = Auction(id_generator, "seller-id")
    auction.start(clock, Money(100, Currency.BRL), "product-id", now + timedelta(days=1), Decimal('0.1'))
    
    auction.add_bid(Bid(Money(100, Currency.BRL), "user-1", id_generator), clock)
    auction.add_bid(Bid(Money(110, Currency.BRL), "user-2", id_generator), clock)
    
    assert len(auction.bids) == 2
    assert auction.bids[-1].user_id == "user-2"

def test_bid_second_bid_lower_than_first_bid():
    id_generator = MockIdGenerator()
    clock = MockClock(datetime.now())
    now = clock.now()
    auction = Auction(id_generator, "seller-id")
    auction.start(clock, Money(100, Currency.BRL), "product-id", now + timedelta(days=1), Decimal('0.1'))
    
    auction.add_bid(Bid(Money(100, Currency.BRL), "user-1", id_generator), clock)
    
    with pytest.raises(BidTooLowError):
        auction.add_bid(Bid(Money(105, Currency.BRL), "user-2", id_generator), clock)

def test_bid_expirated_auction():
    id_generator = MockIdGenerator()
    clock = MockClock(datetime.now())
    now = clock.now()
    auction = Auction(id_generator, "seller-id")
    
    auction.start(clock, Money(100, Currency.BRL), "product-id", now + timedelta(hours=2), Decimal('0.1'))
    
    clock.current_time = now + timedelta(hours=3)
    
    with pytest.raises(AuctionExpiredError):
        auction.add_bid(Bid(Money(150, Currency.BRL), "user-id", id_generator), clock)


def test_close_valid_configuration():
    id_generator = MockIdGenerator()
    clock = MockClock(datetime.now())
    now = clock.now()
    auction = Auction(id_generator, "seller-id")
    auction.start(clock, Money(100, Currency.BRL), "product-id", now + timedelta(days=1), Decimal('0.1'))
    auction.add_bid(Bid(Money(100, Currency.BRL), "user-id", id_generator), clock)
    clock.current_time = now + timedelta(days=2)
    auction.close(clock)
    assert auction.status == AuctionStatus.CLOSED
    assert auction.winner_id == "user-id"


def test_close_auction_active_no_bids():
    id_generator = MockIdGenerator()
    clock = MockClock(datetime.now())
    now = clock.now()
    auction = Auction(id_generator, "seller-id")
    auction.start(clock, Money(100, Currency.BRL), "product-id", now + timedelta(days=1), Decimal('0.1'))
    clock.current_time = now + timedelta(days=2)
    auction.close(clock)
    assert auction.status == AuctionStatus.CANCELLED
    assert auction.winner_id is None
    assert auction.closed_at is None

def test_close_auction_active_with_bids_below_reserve_price():
    id_generator = MockIdGenerator()
    clock = MockClock(datetime.now())
    now = clock.now()
    auction = Auction(id_generator, "seller-id")
    auction.start(clock, Money(500, Currency.BRL), "product-id", now + timedelta(days=1), Decimal('0.1'))
    auction.add_bid(Bid(Money(100, Currency.BRL), "user-id", id_generator), clock)
    clock.current_time = now + timedelta(days=2)
    auction.close(clock)
    assert auction.status == AuctionStatus.CANCELLED
    assert auction.winner_id is None
    assert auction.closed_at is None

def test_close_auction_before_expiration():
    id_generator = MockIdGenerator()
    clock = MockClock(datetime.now())
    now = clock.now()
    auction = Auction(id_generator, "seller-id")
    auction.start(clock, Money(100, Currency.BRL), "product-id", now + timedelta(days=1), Decimal('0.1'))
    with pytest.raises(AuctionNotExpiredError):
        auction.close(clock)


def test_cancel_auction_draft():
    id_generator = MockIdGenerator()
    auction = Auction(id_generator, "seller-id")
    auction.cancel()
    assert auction.status == AuctionStatus.CANCELLED

def test_cancel_auction_active():
    id_generator = MockIdGenerator()
    clock = MockClock(datetime.now())
    now = clock.now()
    auction = Auction(id_generator, "seller-id")
    auction.start(clock, Money(100, Currency.BRL), "product-id", now + timedelta(days=1), Decimal('0.1'))
    auction.cancel()
    assert auction.status == AuctionStatus.CANCELLED

def test_cancel_auction_closed():
    id_generator = MockIdGenerator()
    clock = MockClock(datetime.now())
    now = clock.now()
    auction = Auction(id_generator, "seller-id")
    auction.start(clock, Money(100, Currency.BRL), "product-id", now + timedelta(days=1), Decimal('0.1'))
    auction.add_bid(Bid(Money(100, Currency.BRL), "user-id", id_generator), clock)
    clock.current_time = now + timedelta(days=2)
    auction.close(clock)

    with pytest.raises(AuctionInvalidStateTransitionError):
        auction.cancel()

def test_cancel_auction_cancelled():
    id_generator = MockIdGenerator()
    auction = Auction(id_generator, "seller-id")
    auction.cancel()
    with pytest.raises(AuctionInvalidStateTransitionError):
        auction.cancel()



def test_bid_snipe():
    id_generator = MockIdGenerator()
    clock = MockClock(datetime.now())
    expiration = clock.now() + timedelta(hours=2)
    
    auction = Auction(id_generator, "seller-id")
    auction.start(clock, Money(100, Currency.BRL), "product-id", expiration, Decimal('0.1'))

    clock.current_time = expiration - timedelta(seconds=15)
    auction.add_bid(Bid(Money(100, Currency.BRL), "user-id", id_generator), clock)
    
    assert auction.expires_at == expiration + timedelta(minutes=2)
