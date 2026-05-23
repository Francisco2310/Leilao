from dataclasses import dataclass
from decimal import Decimal

@dataclass
class AuctionResponseDto:
    id: str
    seller_id: str
    product_id: str
    current_price: Decimal | None
    status: str
    expires_at: str | None

    @staticmethod
    def from_entity(auction) -> 'AuctionResponseDto':
        return AuctionResponseDto(
            id=auction.id,
            seller_id=auction.seller_id,
            product_id=auction.product_id,
            current_price=auction.highest_bid.value.amount if auction.highest_bid else auction.reserve_price.amount if auction.reserve_price else Decimal('0.0'),
            status=auction.status.value,
            expires_at=auction.expires_at.isoformat() if auction.expires_at else None
        )

