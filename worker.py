import json
import time
import pika

def run_consumer(app, once: bool = False):
    """Start RabbitMQ consumer; requires Flask app to push context."""
    from extensions import send_email
    url = app.config["RABBITMQ_URL"]
    exchange = app.config["RABBITMQ_EXCHANGE"]
    exchange_type = app.config["RABBITMQ_EXCHANGE_TYPE"]
    routing_key = app.config["RABBITMQ_ROUTING_KEY"]
    queue = f'{exchange}.{routing_key}'

    with app.app_context():
        while True:
            try:
                conn = pika.BlockingConnection(pika.URLParameters(url))
                ch = conn.channel()
                ch.exchange_declare(exchange=exchange, exchange_type=exchange_type, durable=True)
                ch.queue_declare(queue=queue, durable=True)
                ch.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)
                ch.basic_qos(prefetch_count=10)

                def handle(_ch, method, props, body):
                    data = json.loads(body)
                    # expected payload example: {"to":"user@x.com","subject":"...","html":"..."}
                    send_email(data["to"], data.get("subject", "Notification"), data["html"])
                    _ch.basic_ack(method.delivery_tag)

                ch.basic_consume(queue, on_message_callback=handle)
                ch.start_consuming()
            except Exception as e:
                print("Consumer error:", e, "— retrying in 5s")
                time.sleep(5)