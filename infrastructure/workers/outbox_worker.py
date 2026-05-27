import time
import json
import os
import pika  # type: ignore[import-untyped]
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from infrastructure.database.database import SessionLocal
from infrastructure.models.outbox_event_model import OutboxEventModel

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://user:password@localhost:5672/")

def get_rabbitmq_channel():
    parameters = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    channel.confirm_delivery()
    
    channel.exchange_declare(
        exchange="auction_events",
        exchange_type="topic",
        durable=True
    )
    
    return connection, channel

def process_single_event(db: Session, channel: pika.adapters.blocking_connection.BlockingChannel, event: OutboxEventModel) -> bool:
    try:
        routing_key = event.event_type.lower()
        payload_data = event.payload

        channel.basic_publish(
            exchange="auction_events",
            routing_key=routing_key,
            body=json.dumps(payload_data),
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent,
                content_type="application/json"
            )
        )
        event.processed = True
        db.merge(event)
        db.commit()
        print(f"[Outbox Worker] Evento '{event.event_type}' publicado com sucesso (ID: {event.id})")
        return True

    except pika.exceptions.UnroutableError:
        print(f"[Outbox Worker] ERRO: Evento {event.id} não pôde ser roteado pelo RabbitMQ.")
        db.rollback()
        return False
    except Exception as e:
        print(f"[Outbox Worker] Erro inesperado ao processar evento {event.id}: {e}")
        db.rollback()
        return False

def main():
    print("[Outbox Worker] Iniciando o background worker do Transactional Outbox...")
    
    connection = None
    channel = None
    
    while True:
        try:
            if connection is None or connection.is_closed or channel is None or channel.is_closed:
                print("[Outbox Worker] Conectando ao RabbitMQ...")
                connection, channel = get_rabbitmq_channel()
                print("[Outbox Worker] Conectado e pronto para publicar eventos.")

            db = SessionLocal()
            try:
                pending_events = (
                    db.query(OutboxEventModel)
                    .filter_by(processed=False)
                    .order_by(OutboxEventModel.id.asc())
                    .limit(50)
                    .all()
                )

                if pending_events:
                    for event in pending_events:
                        process_single_event(db, channel, event)
                else:
                    time.sleep(1)

            finally:
                db.close()

        except (pika.exceptions.AMQPConnectionError, pika.exceptions.AMQPChannelError) as rabbit_err:
            print(f"[Outbox Worker] Falha de conexão com o RabbitMQ: {rabbit_err}. Tentando novamente em 5 segundos...")
            connection = None
            channel = None
            time.sleep(5)
        except Exception as e:
            print(f"[Outbox Worker] Erro geral no loop principal: {e}. Tentando novamente em 5 segundos...")
            time.sleep(5)

if __name__ == "__main__":
    main()
