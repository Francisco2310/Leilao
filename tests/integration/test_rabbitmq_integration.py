import pika  # type: ignore[import-untyped]
import json
import os
import pytest
from datetime import datetime, timedelta
from uuid6 import uuid7
from infrastructure.models.outbox_event_model import OutboxEventModel
from infrastructure.workers.outbox_worker import process_single_event, get_rabbitmq_channel

def test_full_outbox_to_rabbitmq_integration_flow(client, db_session):
    try:
        connection, channel = get_rabbitmq_channel()
    except Exception:
        pytest.skip("RabbitMQ não está ativo no Docker local. Pulando teste de integração de mensageria.")
        return

    try:
        queue_name = "test_rabbitmq_integration_queue"
        channel.queue_declare(queue=queue_name, exclusive=True)
        channel.queue_bind(
            exchange="auction_events", 
            queue=queue_name, 
            routing_key="auctionstartedevent"
        )

        db_session.query(OutboxEventModel).delete()
        db_session.commit()

        seller_id = str(uuid7())
        create_resp = client.post("/auctions", json={"seller_id": seller_id})
        assert create_resp.status_code == 201
        auction_id = create_resp.json()["auction_id"]

        product_id = str(uuid7())
        expires_at = (datetime.now() + timedelta(days=2)).isoformat()
        
        start_resp = client.post(
            f"/auctions/{auction_id}/start",
            json={
                "seller_id": seller_id,
                "reserve_price": 250.0,
                "currency": "BRL",
                "product_id": product_id,
                "expires_at": expires_at,
                "minimum_percentage": 0.10
            }
        )
        assert start_resp.status_code == 200

        event = db_session.query(OutboxEventModel).filter_by(event_type="AuctionStartedEvent").first()
        assert event is not None
        assert event.payload["auction_id"] == auction_id
        assert event.payload["seller_id"] == seller_id

        publish_success = process_single_event(db_session, channel, event)
        assert publish_success is True

        db_session.refresh(event)
        assert event.processed is True


        method_frame, header_frame, body = channel.basic_get(queue=queue_name, auto_ack=True)
        assert method_frame is not None
        assert body is not None

        received_payload = json.loads(body.decode("utf-8"))
        assert received_payload["auction_id"] == auction_id
        assert received_payload["seller_id"] == seller_id
        assert float(received_payload["reserve_price_amount"]) == 250.0
        assert received_payload["reserve_price_currency"] == "BRL"

    finally:
        connection.close()
