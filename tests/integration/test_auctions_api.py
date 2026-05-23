from decimal import Decimal
from infrastructure.models.auction_model import AuctionModel
from infrastructure.models.bid_model import BidModel
import pytest
from uuid6 import uuid7
from datetime import datetime, timedelta

def test_create_auction_success(client, db_session):
    seller_id = str(uuid7())
    response = client.post("/auctions", json={"seller_id": seller_id})
    result = db_session.query(AuctionModel).filter_by(seller_id=seller_id).first()
    assert "auction_id" in response.json()
    assert result.seller_id == seller_id
    assert result.status == "draft"
    assert response.status_code == 201

def test_create_auction_missing_body(client, db_session):
    response = client.post("/auctions", json={})
    assert response.status_code == 422

def test_start_auction_success(client, db_session):
    seller_id = str(uuid7())
    create_resp = client.post("/auctions", json={"seller_id": seller_id})
    auction_id = create_resp.json()["auction_id"]
    
    product_id = str(uuid7())
    expires_at = (datetime.now() + timedelta(days=2)).isoformat()
    
    response = client.post(
        f"/auctions/{auction_id}/start",
        json={
            "seller_id": seller_id,
            "reserve_price": 100.0,
            "currency": "BRL",
            "product_id": product_id,
            "expires_at": expires_at,
            "minimum_percentage": 0.10
        }
    )
    assert response.status_code == 200
    auction = db_session.query(AuctionModel).filter_by(id=auction_id).first()
    assert auction.status == "active"
    assert auction.reserve_price_amount == 100.0
    assert auction.reserve_price_currency == "BRL"
    assert auction.minimum_percentage == Decimal('0.10')

def test_start_auction_unauthorized(client, db_session):
    seller_id = str(uuid7())
    other_id = str(uuid7())
    create_resp = client.post("/auctions", json={"seller_id": seller_id})
    auction_id = create_resp.json()["auction_id"]
    
    product_id = str(uuid7())
    expires_at = (datetime.now() + timedelta(days=2)).isoformat()
    
    response = client.post(
        f"/auctions/{auction_id}/start",
        json={
            "seller_id": other_id,
            "reserve_price": 100.0,
            "currency": "BRL",
            "product_id": product_id,
            "expires_at": expires_at,
            "minimum_percentage": 0.10
        }
    )
    assert response.status_code == 403

def test_add_bid_success(client, db_session):
    seller_id = str(uuid7())
    create_resp = client.post("/auctions", json={"seller_id": seller_id})
    auction_id = create_resp.json()["auction_id"]
    
    product_id = str(uuid7())
    expires_at = (datetime.now() + timedelta(days=2)).isoformat()
    client.post(
        f"/auctions/{auction_id}/start",
        json={
            "seller_id": seller_id,
            "reserve_price": 100.0,
            "currency": "BRL",
            "product_id": product_id,
            "expires_at": expires_at,
            "minimum_percentage": 0.10
        }
    )
    
    bidder_id = str(uuid7())
    response = client.post(
        f"/auctions/{auction_id}/bids",
        json={
            "user_id": bidder_id,
            "amount": 50.0,
            "currency": "BRL"
        }
    )
    assert response.status_code == 201

    bid = db_session.query(BidModel).filter_by(auction_id=auction_id).first()
    assert bid is not None
    assert bid.user_id == bidder_id
    assert bid.amount == 50.0

def test_add_bid_self_bidding_fails(client, db_session):
    seller_id = str(uuid7())
    create_resp = client.post("/auctions", json={"seller_id": seller_id})
    auction_id = create_resp.json()["auction_id"]
    
    product_id = str(uuid7())
    expires_at = (datetime.now() + timedelta(days=2)).isoformat()
    client.post(
        f"/auctions/{auction_id}/start",
        json={
            "seller_id": seller_id,
            "reserve_price": 100.0,
            "currency": "BRL",
            "product_id": product_id,
            "expires_at": expires_at,
            "minimum_percentage": 0.10
        }
    )

    response = client.post(
        f"/auctions/{auction_id}/bids",
        json={
            "user_id": seller_id,
            "amount": 50.0,
            "currency": "BRL"
        }
    )
    assert response.status_code == 400

def test_cancel_auction_success(client, db_session):
    seller_id = str(uuid7())
    create_resp = client.post("/auctions", json={"seller_id": seller_id})
    auction_id = create_resp.json()["auction_id"]
    
    response = client.post(
        f"/auctions/{auction_id}/cancel",
        json={"seller_id": seller_id}
    )
    assert response.status_code == 200
    
    auction = db_session.query(AuctionModel).filter_by(id=auction_id).first()
    assert auction.status == "cancelled"

def test_cancel_auction_unauthorized(client, db_session):
    seller_id = str(uuid7())
    other_id = str(uuid7())
    create_resp = client.post("/auctions", json={"seller_id": seller_id})
    auction_id = create_resp.json()["auction_id"]
    
    response = client.post(
        f"/auctions/{auction_id}/cancel",
        json={"seller_id": other_id}
    )
    assert response.status_code == 403

def test_close_auction_fails_not_expired(client, db_session):
    seller_id = str(uuid7())
    create_resp = client.post("/auctions", json={"seller_id": seller_id})
    auction_id = create_resp.json()["auction_id"]
    
    product_id = str(uuid7())
    expires_at = (datetime.now() + timedelta(days=2)).isoformat()
    client.post(
        f"/auctions/{auction_id}/start",
        json={
            "seller_id": seller_id,
            "reserve_price": 100.0,
            "currency": "BRL",
            "product_id": product_id,
            "expires_at": expires_at,
            "minimum_percentage": 0.10
        }
    )
    
    response = client.post(f"/auctions/{auction_id}/close")
    assert response.status_code == 400

def test_list_auctions_filtering(client, db_session):
    seller1 = str(uuid7())
    seller2 = str(uuid7())
    
    client.post("/auctions", json={"seller_id": seller1})
    
    client.post("/auctions", json={"seller_id": seller2})
    
    response = client.get(f"/auctions?seller_id={seller1}")
    assert response.status_code == 200
    auctions = response.json()
    assert len(auctions) == 1
    assert auctions[0]["seller_id"] == seller1
