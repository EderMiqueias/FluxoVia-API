import contextlib
import abc
import psycopg2

from typing import Tuple
from config import Config


# TODO: usar print é útil para debug, mas para deploy não serve de nada. Que tal um logger?


class Database(abc.ABC):
    """
    Classe base abstrata (ABC) que define o contrato (interface) para implementações
    de banco de dados na aplicação.

    Ao herdar de `abc.ABC`, esta classe não pode ser instanciada diretamente.
    Toda subclasse concreta deve sobrescrever os métodos aqui definidos, garantindo
    um comportamento consistente e intercambiável entre diferentes fornecedores de
    banco de dados (PostgreSQL, MySQL, SQLite, etc.).
    """

    def __init__(self):
        self.config = {
            "host": Config.Database.host,
            "port": Config.Database.port,
            "dbname": Config.Database.dbname,
            "user": Config.Database.user,
            "password": Config.Database.password
        }

    def get_connection(self):
        """
        Cria e retorna um objeto de conexão com o banco de dados.

        Deve ser sobrescrito pela subclasse concreta para fornecer
        uma conexão real ao banco de dados alvo.
        """
        pass

    def connection(self):
        """
        Context manager que gerencia o ciclo de vida de uma conexão com o banco
        de dados, incluindo commit, rollback e encerramento.

        Deve ser sobrescrito pela subclasse concreta.
        """
        pass

    def cursor(self, *args, **kwargs):
        """
        Context manager que fornece um cursor de banco de dados pronto para uso,
        encapsulando a conexão subjacente.

        Deve ser sobrescrito pela subclasse concreta.

        Args:
            *args: Argumentos posicionais repassados ao construtor do cursor.
            **kwargs: Argumentos nomeados repassados ao construtor do cursor.
        """
        pass

    def executar_query(self, query: str, parametros: Tuple = ()):
        """
        Executa uma query SQL parametrizada e retorna o resultado.

        Deve ser sobrescrito pela subclasse concreta.

        Args:
            query (str): String SQL a ser executada.
            parametros (Tuple): Tupla de parâmetros para substituição segura na query,
                                prevenindo SQL Injection. Padrão: tupla vazia.
        """
        pass


class PostgresDatabase(Database):
    """
    Implementação concreta de `Database` para o banco de dados PostgreSQL.

    Utiliza a biblioteca `psycopg2` para estabelecer conexões e executar queries.
    Herda os parâmetros de configuração de `Database.__init__` e implementa
    todos os métodos com a lógica específica do PostgreSQL.
    """

    def get_connection(self):
        """
        Cria e retorna uma nova conexão direta com o banco de dados PostgreSQL.

        Lê os parâmetros de conexão diretamente de `Config.Database` (variáveis de
        ambiente) e utiliza `psycopg2.connect` para estabelecer a conexão. Imprime
        mensagens de status no console para fins de debug.

        Returns:
            psycopg2.extensions.connection: Objeto de conexão ativa com o PostgreSQL.

        Raises:
            psycopg2.OperationalError: Se não for possível estabelecer a conexão
                                       (host inválido, credenciais incorretas, etc.).
        """
        print("Requesting database connection")

        conn = psycopg2.connect(
            host=Config.Database.host,
            port=Config.Database.port,
            dbname=Config.Database.dbname,
            user=Config.Database.user,
            password=Config.Database.password
        )

        print("got connection")
        return conn

    # O decorator `@contextlib.contextmanager` transforma esta função geradora em um
    # context manager compatível com a instrução `with`. Isso permite controlar o
    # ciclo de vida da conexão de forma estruturada:
    #   - O código antes do `yield` é executado na entrada do bloco `with` (__enter__).
    #   - O valor passado ao `yield` é disponibilizado via `as` no bloco `with`.
    #   - Os blocos except/else/finally após o `yield` são executados na saída (__exit__).
    @contextlib.contextmanager
    def connection(self):
        """
        Context manager que gerencia o ciclo de vida completo de uma conexão PostgreSQL.

        Garante que:
        - A conexão seja aberta e cedida ao bloco `with`.
        - Em caso de exceção, a transação seja revertida (rollback) e a exceção
          seja re-lançada para o chamador.
        - Em caso de sucesso (sem exceção), a transação seja confirmada (commit).
        - A conexão seja sempre encerrada ao final, independente do resultado (finally).

        Yields:
            psycopg2.extensions.connection: Objeto de conexão ativa com transação gerenciada.
        """
        conn = self.get_connection()
        try:
            yield conn
        except Exception as e:
            print("PGSQL Exception: {}".format(e))
            conn.rollback()
            raise e
        else:
            # O bloco `else` é executado somente quando nenhuma exceção ocorre no `try`.
            # Confirma permanentemente todas as operações da transação no banco de dados.
            conn.commit()
        finally:
            # O bloco `finally` é sempre executado, garantindo que a conexão
            # seja encerrada e os recursos liberados, mesmo em caso de erro.
            conn.close()

    @contextlib.contextmanager
    def cursor(self, *args, **kwargs):
        """
        Context manager que fornece um cursor PostgreSQL pronto para execução de queries.

        Reutiliza o context manager `self.connection()` para garantir que a conexão
        e a transação sejam gerenciadas corretamente. O cursor é criado a partir da
        conexão ativa e cedido ao bloco `with`.

        Args:
            *args: Argumentos posicionais repassados ao `conn.cursor()` do psycopg2
                   (ex: `cursor_factory` para cursores especializados).
            **kwargs: Argumentos nomeados repassados ao `conn.cursor()` do psycopg2.

        Yields:
            psycopg2.extensions.cursor: Cursor ativo associado à conexão gerenciada.
        """
        with self.connection() as conn:
            yield conn.cursor(*args, **kwargs)

    def fetchall_cursor(self, *args, **kwargs):
        """
        Executa uma query SQL através de um cursor gerenciado e retorna todos os
        resultados como uma lista de dicionários.

        Obtém um cursor via `self.cursor()`, executa a query com os parâmetros
        fornecidos e, se houver resultados, mapeia cada linha para um dicionário
        usando os nomes das colunas como chaves.

        Args:
            *args: Argumentos posicionais repassados ao `cursor.execute()`.
                   Normalmente: (query_string,) ou (query_string, parametros_tupla).
            **kwargs: Argumentos nomeados repassados ao context manager `self.cursor()`.

        Returns:
            list[dict] | None: Lista de dicionários onde cada dicionário representa
                               uma linha do resultado com o formato {nome_coluna: valor}.
                               Retorna `None` se a query não produzir linhas de resultado
                               (ex: INSERT, UPDATE, DELETE sem cláusula RETURNING).
        """
        with self.cursor(**kwargs) as cursor:
            cursor.execute(*args)

            # Queries que não retornam linhas (INSERT, UPDATE, DELETE) possuem
            # `cursor.description` como None. Nesse caso, retornamos None explicitamente.
            if cursor.description is None:
                return None

            # Extrai os nomes das colunas a partir dos metadados do cursor.
            columns = [value.name for value in cursor.description]

            # Combina cada linha de resultado com os nomes das colunas via `zip`,
            # convertendo para dicionário. A list comprehension constrói a lista final.
            query_result = [
                dict(zip(columns, row))
                for row in cursor
            ]

            return query_result

    def execute_query(self, query, data_tuples=None):
        """
        Ponto de entrada público para execução de queries SQL.

        Delega a execução para `fetchall_cursor`, encapsulando a lógica de decisão
        entre queries com ou sem parâmetros. Captura exceções, registra o erro no
        console e re-lança para que o chamador possa tratá-lo adequadamente.

        Args:
            query (str): String SQL a ser executada.
            data_tuples (tuple | None): Tupla de parâmetros para substituição segura
                                       na query (prevenção de SQL Injection via psycopg2).
                                       Se `None`, a query é executada sem parâmetros.

        Returns:
            list[dict] | None: Resultado da query como lista de dicionários,
                               ou `None` para queries sem retorno de linhas.

        Raises:
            Exception: Re-lança qualquer exceção ocorrida durante a execução da query.
        """
        try:
            # Se parâmetros foram fornecidos, repassa-os ao cursor para substituição
            # segura (parametrização), prevenindo SQL Injection.
            if data_tuples is not None:
                return self.fetchall_cursor(query, data_tuples)

            return self.fetchall_cursor(query)

        except Exception as e:
            print('Erro durante execução da query:', str(e))
            raise e
