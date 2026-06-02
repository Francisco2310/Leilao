from datetime import datetime
from domain.value_objects.money import Money
from domain.ports.ports import IdGenerator
from domain.exceptions.domain_exceptions import BidTooLowError

class Bid:
  value: Money
  user_id: str
  id: str
  placed_at: datetime | None

  def __init__(self, value: Money, user_id: str, id_generator: IdGenerator):
    if value.amount <= 0:
      raise BidTooLowError("Bid value must be positive")
    self.value = value
    self.user_id = user_id
    self.id = id_generator.generate()
    self.placed_at = None

  def __eq__(self, other: object) -> bool:
    if not isinstance(other, Bid):
      return NotImplemented
    return self.id == other.id

  @classmethod
  def restore(cls, id: str, user_id: str, value: Money, placed_at: datetime) -> 'Bid':
    bid = cls.__new__(cls)
    bid.id = id
    bid.user_id = user_id
    bid.value = value
    bid.placed_at = placed_at
    return bid


