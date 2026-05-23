import datetime
from domain.Ports.ports import Clock

class SystemClock(Clock):
    def now(self) -> datetime.datetime:
        return datetime.datetime.now()