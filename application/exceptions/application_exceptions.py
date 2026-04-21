class ApplicationException(Exception):
    pass

class AuctionNotFoundError(ApplicationException):
    pass

class UnauthorizedActionError(ApplicationException):
    pass
