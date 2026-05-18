import os
import json
import time
import pika
import requests
from dotenv import load_dotenv

load_dotenv()


class Config:
    RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672//")
    QUEUE_NAME = os.getenv("RABBITMQ_QUEUE", "tickets_queue")
    API_BASE_URL = os.getenv("API_BASE_URL")
    AUTH_EMAIL = os.getenv("API_AUTH_EMAIL")
    AUTH_PASSWORD = os.getenv("API_AUTH_PASSWORD")


class TicketWorker:
    def __init__(self, config=Config):
        """
        Inicializa a instância do TicketWorker com as configurações necessárias.
        
        Este método configura a classe com os parâmetros de conexão, autenticação
        e endpoints da API. O token é inicializado como None e será preenchido
        na primeira chamada a authenticate().
        
        Args:
            config: Classe de configuração contendo URLs, credenciais e endpoints.
                   Padrão: Config (classe definida no módulo).
        """
        self.config = config
        self.token = None

    def authenticate(self):
        """
        Realiza autenticação junto à API NestJS e armazena o token JWT em memória.
        
        Este método envia uma requisição POST para o endpoint /auth com email e senha,
        obtém o token JWT retornado, e o armazena no atributo self.token para uso
        em requisições subsequentes. Em caso de falha, tenta novamente na próxima
        chamada de send_ticket() que detectar falta de token.
        
        Returns:
            bool: True se a autenticação foi bem-sucedida e o token foi obtido;
                  False em caso de erro HTTP, timeout ou exceção de conexão.
        """
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
        """
        Envia os dados da multa de trânsito para a API externa via HTTP POST.
        
        Este método valida a presença de um token válido (autenticando se necessário),
        constrói o header com autenticação Bearer, e envia a requisição para o endpoint
        /tickets. Implementa retry automático em caso de recebimento do status 401
        (token expirado), renovando o token e retentando exatamente uma vez. Qualquer
        outro status de erro é retornado sem retry.
        
        Args:
            ticket_data (dict): Dicionário contendo os dados da multa a enviar.
                               Tipicamente inclui: placa, id_aparelho_medidor, etc.
        
        Returns:
            bool: True se a requisição foi aceita pela API (status 200 ou 201);
                  False em caso de erro HTTP, falha de autenticação persistente,
                  timeout ou exceção de conexão.
        """
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
    """
    Callback executado a cada mensagem recebida pela fila RabbitMQ.
    
    Este callback desserializa o payload JSON da mensagem, processa o envio do ticket
    via send_ticket(), e em seguida executa a lógica apropriada de confirmação ou
    refilagem. Se o envio for bem-sucedido, envia ACK (confirmando a remoção da fila).
    Em caso de falha (API indisponível, erro temporário), envia NACK com requeue=True
    para devolver a mensagem à fila e tentar novamente após delay de 5 segundos.
    Erros de desserialização JSON são silenciados com ACK para evitar que mensagens
    malformadas travem a fila indefinidamente.
    
    Args:
        ch: Objeto de canal (connection channel) do pika para interagir com RabbitMQ.
        method: Metadados do frame/mensagem (delivery_tag, etc.).
        properties: Propriedades da mensagem (headers, content_type, etc.).
        body (bytes): Conteúdo bruto da mensagem codificada em UTF-8 (JSON).
    """
    print(f"\n[Worker] Nova mensagem capturada da fila.")
    try:
        ticket_data = json.loads(body.decode('utf-8'))
        worker = ch.worker_instance
        
        success = worker.send_ticket(ticket_data)
        
        if success:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print("[Worker] Mensagem finalizada com sucesso (ACK enviado).")
        else:
            print("[Worker] Falha temporária detectada. Reenfileirando mensagem para nova tentativa em 5s...")
            time.sleep(5)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
    except Exception as e:
        print(f"[Worker] Erro de processamento interno ou JSON inválido: {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    """
    Ponto de entrada principal do worker de processamento de multas.
    
    Este método inicializa a instância do TicketWorker, estabelece conexão
    com o RabbitMQ (com retry automático em caso de indisponibilidade),
    declara a fila persistente de tickets, configura o prefetch count para
    garantir processamento justo (apenas 1 mensagem por worker), e inicia
    o consumo de mensagens indefinidamente até interrupção manual (CTRL+C).
    
    A conexão é robusta e tolerante a falhas temporárias do RabbitMQ durante
    startup, tentando reconectar a cada 5 segundos até sucesso.
    """
    worker = TicketWorker()
    
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
    
    channel.queue_declare(queue=worker.config.QUEUE_NAME, durable=True)

    channel.basic_qos(prefetch_count=1)
    
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
