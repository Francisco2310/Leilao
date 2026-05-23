from uuid6 import uuid7
from domain.Ports.ports import IdGenerator

class Uuid7IdGenerator(IdGenerator):
    def generate(self) -> str:
        return str(uuid7())