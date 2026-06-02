import datetime
from domain.ports.ports import Clock

class SystemClock(Clock):
    def now(self) -> datetime.datetime:
        return datetime.datetime.now()