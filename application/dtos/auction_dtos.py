from dataclasses import dataclass

@dataclass
class AuctionResponseDto:
    id: str
    seller_id: str
    product_id: str
    current_price: float
    status: str
    expires_at: str

    @staticmethod
    def from_entity(auction) -> 'AuctionResponseDto':
        return AuctionResponseDto(
            id=auction.id,
            seller_id=auction.seller_id,
            product_id=auction.product_id,
            current_price=float(auction.highest_bid.value.amount if auction.highest_bid else auction.minimum_bid.amount),
            status=auction.status.value,
            expires_at=auction.expires_at.isoformat()
        )

