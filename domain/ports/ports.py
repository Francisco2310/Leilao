from abc import ABC, abstractmethod
from datetime import datetime

class IdGenerator(ABC):
    @abstractmethod
    def generate(self) -> str:
        pass

class Clock(ABC):
    @abstractmethod
    def now(self) -> datetime:
        pass
