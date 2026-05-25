from sqlalchemy import JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.database.database import Base
from datetime import datetime
from uuid6 import uuid7

class OutboxEventModel(Base):
    __tablename__ = "outbox_events"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid7()), index=True)
    event_type: Mapped[str] = mapped_column(nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    processed: Mapped[bool] = mapped_column(default=False, index=True)
