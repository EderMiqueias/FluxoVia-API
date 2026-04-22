import logging
import sys

def configurar_logger():
    """
    Configura o padrão de logs para toda a aplicação.
    Esta função deve ser chamada apenas uma vez, no ponto de 
    entrada do programa (ex: main.py).
    """
    # Define o formato visual da mensagem. 
    # Exemplo gerado: 2026-04-22 10:15:30 - [INFO] - database - Conexão aberta.
    formato_do_log = "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"

    logging.basicConfig(
        level=logging.INFO, # Define que queremos ver tudo de INFO para cima (WARNING, ERROR)
        format=formato_do_log,
        datefmt="%Y-%m-%d %H:%M:%S", # Formato da data mais limpo
        handlers=[
            logging.StreamHandler(sys.stdout) # Garante que o log saia no terminal/console
        ]
    )
