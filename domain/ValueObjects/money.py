from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from domain.Exceptions.domain_exceptions import NegativeAmountError, CurrencyMismatchError, InvalidCurrencyError

class Currency(Enum):
  BRL = "BRL"
  USD = "USD"

  @classmethod
  def _missing_(cls, value):
      raise InvalidCurrencyError(f"'{value}' is not a valid currency. Allowed: BRL, USD")

@dataclass(frozen=True)
class Money:
  amount: Decimal
  currency: Currency

  def __post_init__(self):
    if not isinstance(self.amount, Decimal):
      object.__setattr__(self, 'amount', Decimal(str(self.amount)))

    if isinstance(self.currency, str):
      object.__setattr__(self, 'currency', Currency(self.currency))

    if self.amount < 0:
      raise NegativeAmountError("Amount must be positive")

  def add(self, other: 'Money') -> 'Money':
    if self.currency != other.currency:
      raise CurrencyMismatchError("Currencies must match")
    return Money(self.amount + other.amount, self.currency)

  def sub(self, other: 'Money') -> 'Money':
    if self.currency != other.currency:
      raise CurrencyMismatchError("Currencies must match")
    if self.amount < other.amount:
      raise NegativeAmountError("Resulted amount must be positive")
    return Money(self.amount - other.amount, self.currency)

  def __lt__(self, other: 'Money') -> bool:
    if not isinstance(other, Money):
      return NotImplemented
    if self.currency != other.currency:
      raise CurrencyMismatchError("Currencies must match")
    return self.amount < other.amount