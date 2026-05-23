from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Uuid, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from infrastructure.database.database import Base

if TYPE_CHECKING:
    from infrastructure.models.auction_model import AuctionModel


class BidModel(Base):
    __tablename__ = "bids"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, index=True)
    auction_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("auctions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)

    auction: Mapped[AuctionModel] = relationship(back_populates="bids")
