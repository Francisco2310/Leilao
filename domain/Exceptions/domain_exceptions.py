class DomainException(Exception):
    """Base exception for all domain errors."""
    pass

class NegativeAmountError(DomainException):
    """Raised when a monetary amount is negative."""
    pass

class CurrencyMismatchError(DomainException):
    """Raised when operations are attempted between different currencies."""
    pass

class BidTooLowError(DomainException):
    """Raised when a bid value is not strictly positive."""
    pass

class AuctionNotActiveError(DomainException):
    """Raised when an operation requires an active auction but it is not."""
    pass

class AuctionInvalidStateTransitionError(DomainException):
    """Raised when attempting an invalid state transition on an auction."""
    pass

class AuctionExpiredError(DomainException):
    """Raised when an operation is attempted on an auction that has already expired."""
    pass

class InvalidAuctionConfigurationError(DomainException):
    """Raised when attempting to start an auction with missing or invalid configuration data."""
    pass

class SelfBidError(DomainException):
    """Raised when a seller attempts to place a bid on their own auction."""
    pass

class AuctionNotExpiredError(DomainException):
    """Raised when attempting to close an auction that has not expired yet."""
    pass
