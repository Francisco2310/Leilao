from domain.ValueObjects.money import Money
from domain.Ports.ports import IdGenerator
from domain.Exceptions.domain_exceptions import BidTooLowError

class Bid:
  value: Money
  user_id: str
  id: str

  def __init__(self, value: Money, user_id: str, id_generator: IdGenerator):
    if value.amount <= 0:
      raise BidTooLowError("Bid value must be positive")
    self.value = value
    self.user_id = user_id
    self.id = id_generator.generate()

  def __eq__(self, other: object) -> bool:
    if not isinstance(other, Bid):
      return NotImplemented
    return self.id == other.id

