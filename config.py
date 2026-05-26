from dotenv import load_dotenv

# Carrega as variáveis de ambiente definidas no arquivo `.env` para o `os.environ`,
# tornando-as acessíveis via `os.environ.get()` ao longo de toda a aplicação.
# Deve ser chamado antes de qualquer leitura de variáveis de ambiente.
load_dotenv()

import os


class Config:
    """
    Classe de configuração centralizada da aplicação.

    Agrupa as configurações por contexto em classes aninhadas,
    facilitando o acesso organizado às variáveis de ambiente sem
    expor credenciais diretamente no código-fonte.
    """

    class Database:
        host: str = os.environ.get('DB_HOST')
        port: str = os.environ.get('DB_PORT')
        dbname: str = os.environ.get('DB_NAME')
        user: str = os.environ.get('DB_USER')
        password: str = os.environ.get('DB_PASSWORD')
        url: str = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

        pool_size: int = int(os.environ.get('DB_POOL_SIZE', 10))
        max_overflow: int = int(os.environ.get('DB_MAX_OVERFLOW', 20))
        pool_pre_ping: bool = os.environ.get('DB_POOL_PRE_PING', 'True').lower() == 'true'

    class RabbitMQ:
        url: str = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672//')
        queue: str = os.environ.get('RABBITMQ_QUEUE', 'tickets')
