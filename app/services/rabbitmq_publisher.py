import json
import pika
import logging
from config import Config

logger = logging.getLogger(__name__)


class RabbitMQPublisher:
    """
    Serviço dedicado para envio de mensagens ao RabbitMQ.
    A conexão é aberta e fechada por disparo para garantir thread-safety no FastAPI.
    """

    def __init__(self, config: Config = Config):
        self.url = config.RabbitMQ.url
        self.queue = config.RabbitMQ.queue

    def publish_ticket(self, payload: dict) -> bool:
        """
        Converte o payload em JSON e envia para a fila garantindo persistência.
        """
        connection = None
        try:
            # 1. Estabelece conexão
            parameters = pika.URLParameters(self.url)
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            # 2. Garante que a fila existe (caso o Worker ainda não tenha ligado)
            # durable=True garante que a fila sobrevive a reinicializações do RabbitMQ
            channel.queue_declare(queue=self.queue, durable=True)

            # 3. Converte os dados para string JSON
            message_body = json.dumps(payload)

            # 4. Publica a mensagem
            channel.basic_publish(
                exchange='',
                routing_key=self.queue,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                )
            )

            logger.info(f"Multa da placa {payload.get('placa')} enviada para a fila {self.queue}.")
            return True

        except Exception as e:
            logger.error(f"Erro ao enviar mensagem para o RabbitMQ: {e}")
            return False

        finally:
            # 5. Fechamento seguro da conexão
            if connection and connection.is_open:
                connection.close()


# Instância Singleton do serviço para ser importada nos controllers
rabbitmq_publisher = RabbitMQPublisher()
