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
