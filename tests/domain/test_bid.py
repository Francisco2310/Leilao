import pytest
from domain.entities.bid import Bid
from domain.value_objects.money import Money, Currency
from domain.exceptions.domain_exceptions import BidTooLowError

class FakeIdGenerator:
  def generate(self) -> str:
    return "1"

def test_bid_creation():
  bid = Bid(Money(100, Currency.BRL), "user1", FakeIdGenerator())

  assert bid.value == Money(100, Currency.BRL)
  assert bid.user_id == "user1"
  assert bid.id == "1"

def test_bid_equality():
  bid1 = Bid(Money(100, Currency.BRL), "user1", FakeIdGenerator())
  bid2 = Bid(Money(100, Currency.BRL), "user1", FakeIdGenerator())

  assert bid1 == bid2

def test_bid_inequality():
  class FakeIdGenerator2:
    def generate(self) -> str:
      return "2"

  bid1 = Bid(Money(100, Currency.BRL), "user1", FakeIdGenerator())
  bid2 = Bid(Money(100, Currency.BRL), "user1", FakeIdGenerator2())

  assert bid1 != bid2

def test_bid_zero_value():
  money = Money(0, Currency.BRL)

  with pytest.raises(BidTooLowError):
    Bid(money, "user1", FakeIdGenerator())

