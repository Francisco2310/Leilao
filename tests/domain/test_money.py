import pytest
from domain.value_objects.money import Money, Currency
from domain.exceptions.domain_exceptions import NegativeAmountError, CurrencyMismatchError

def test_money_equality():
  money1 = Money(100, Currency.BRL)
  money2 = Money(100, Currency.BRL)

  assert money1 == money2

def test_money_negative_value():
  with pytest.raises(NegativeAmountError):
    Money(-100, Currency.BRL)

def test_money_add():
  money1 = Money(100, Currency.BRL)
  money2 = Money(200, Currency.BRL)

  assert money1.add(money2) == Money(300, Currency.BRL)

def test_money_add_different_currencies():
  money1 = Money(100, Currency.BRL)
  money2 = Money(100, Currency.USD)

  with pytest.raises(CurrencyMismatchError):
    money1.add(money2)

def test_money_sub():
  money1 = Money(100, Currency.BRL)
  money2 = Money(50, Currency.BRL)

  assert money1.sub(money2) == Money(50, Currency.BRL)

def test_money_sub_different_currencies():
  money1 = Money(100, Currency.BRL)
  money2 = Money(50, Currency.USD)

  with pytest.raises(CurrencyMismatchError):
    money1.sub(money2)

def test_money_sub_negative_result():
  money1 = Money(50, Currency.BRL)
  money2 = Money(100, Currency.BRL)

  with pytest.raises(NegativeAmountError):
    money1.sub(money2)


def test_money_less_than():
  money1 = Money(50, Currency.BRL)
  money2 = Money(100, Currency.BRL)

  assert money1 < money2
  assert not (money2 < money1)

def test_money_less_than_different_currencies():
  money1 = Money(50, Currency.BRL)
  money2 = Money(100, Currency.USD)

  with pytest.raises(CurrencyMismatchError):
    _ = money1 < money2
