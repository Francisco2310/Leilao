from __future__ import annotations
from decimal import Decimal
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Uuid, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from infrastructure.database.database import Base

if TYPE_CHECKING:
    from infrastructure.models.bid_model import BidModel

class AuctionModel(Base):
    __tablename__ = "auctions"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, index=True)
    seller_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    reserve_price_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    reserve_price_currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    minimum_percentage: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    product_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), nullable=True)
    winner_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
    bids: Mapped[list["BidModel"]] = relationship(back_populates="auction", cascade="all, delete-orphan")
