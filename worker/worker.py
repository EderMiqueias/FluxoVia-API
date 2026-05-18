import os
import json
import time
import pika
import requests
from dotenv import load_dotenv

# Carrega as variáveis de ambiente locais do .env
load_dotenv()


class Config:
    RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672//")
    QUEUE_NAME = os.getenv("RABBITMQ_QUEUE", "tickets_queue")
    API_BASE_URL = os.getenv("API_BASE_URL")
    AUTH_EMAIL = os.getenv("API_AUTH_EMAIL")
    AUTH_PASSWORD = os.getenv("API_AUTH_PASSWORD")


class TicketWorker:
    def __init__(self, config=Config):
        self.config = config
        self.token = None

    def authenticate(self):
        """Efetua a autenticação na API NestJS e atualiza o token em memória"""
        print("[Worker] Solicitando novo token JWT à API...")
        url = f"{self.config.API_BASE_URL}/auth"
        payload = {
            "email": self.config.AUTH_EMAIL,
            "password": self.config.AUTH_PASSWORD
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code in [200, 201]:
                self.token = response.json().get("access_token")
                print("[Worker] Token JWT obtido e armazenado em memória com sucesso.")
                return True
            else:
                print(f"[Worker] Falha na autenticação: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"[Worker] Erro crítico de conexão ao tentar autenticar: {e}")
            return False

    def send_ticket(self, ticket_data):
        """Envia a requisição de multa à API com tratamento de expiração de token (401)"""
        if not self.token:
            if not self.authenticate():
                return False

        url = f"{self.config.API_BASE_URL}/tickets"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=ticket_data, headers=headers, timeout=15)
            
            # Se receber 401, renova o token e tenta exatamente mais uma vez
            if response.status_code == 401:
                print("[Worker] Token expirado ou inválido (401). Renovando...")
                if self.authenticate():
                    headers["Authorization"] = f"Bearer {self.token}"
                    print("[Worker] Retentando envio com o novo token...")
                    response = requests.post(url, json=ticket_data, headers=headers, timeout=15)
                else:
                    return False

            if response.status_code in [200, 201]:
                print(f"[Worker] Multa enviada com sucesso! Placa: {ticket_data.get('placa')} | Radar: {ticket_data.get('id_aparelho_medidor')}")
                return True
            else:
                print(f"[Worker] API recusou a requisição [{response.status_code}]: {response.text}")
                return False

        except Exception as e:
            print(f"[Worker] Erro de rede/indisponibilidade da API: {e}")
            return False

def callback(ch, method, properties, body):
    print(f"\n[Worker] Nova mensagem capturada da fila.")
    try:
        # Decodifica o payload recebido do RabbitMQ
        ticket_data = json.loads(body.decode('utf-8'))
        worker = ch.worker_instance
        
        # Processa o envio
        success = worker.send_ticket(ticket_data)
        
        if success:
            # Confirma o processamento e remove da fila permanentemente
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print("[Worker] Mensagem finalizada com sucesso (ACK enviado).")
        else:
            # Em caso de falhas temporárias (API fora, banco fora), devolvemos para a fila
            print("[Worker] Falha temporária detectada. Reenfileirando mensagem para nova tentativa em 5s...")
            time.sleep(5)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
    except Exception as e:
        print(f"[Worker] Erro de processamento interno ou JSON inválido: {e}")
        # Se for erro estrutural do JSON, dá ACK para não travar a fila com lixo
        ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    worker = TicketWorker()
    
    # Loop de tolerância para aguardar o RabbitMQ inicializar por completo no container
    connection = None
    while not connection:
        try:
            print("[Worker] Tentando conectar ao RabbitMQ...")
            parameters = pika.URLParameters(worker.config.RABBITMQ_URL)
            connection = pika.BlockingConnection(parameters)
        except pika.exceptions.AMQPConnectionError:
            print("[Worker] RabbitMQ indisponível no momento. Aguardando 5 segundos para tentar novamente...")
            time.sleep(5)

    channel = connection.channel()
    
    # Garante a existência da fila persistente (durable)
    channel.queue_declare(queue=worker.config.QUEUE_NAME, durable=True)

    # REQUISITO CRUCIAL: Distribuição justa (Worker processa apenas 1 por vez)
    channel.basic_qos(prefetch_count=1)
    
    # Vincula a instância do worker ao canal para uso no callback global
    channel.worker_instance = worker

    channel.basic_consume(queue=worker.config.QUEUE_NAME, on_message_callback=callback)

    print(f"[Worker] Sistema operacional e escutando a fila '{worker.config.QUEUE_NAME}'. Para sair pressione CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("[Worker] Encerrando graciosamente...")
        channel.stop_consuming()
        connection.close()

if __name__ == "__main__":
    main()
