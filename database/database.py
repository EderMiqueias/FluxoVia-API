from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import Config

# 1. O ENGINE (Singleton Natural): Criado em nível de módulo.
# O SQLAlchemy se encarrega de gerenciar o Pool de conexões de forma segura aqui.
engine = create_engine(
    Config.Database.url,
    pool_size=Config.Database.pool_size,                # Quantidade de conexões a manter no pool
    max_overflow=Config.Database.max_overflow,          # Quantas conexões extras podem ser criadas além do pool_size
    pool_pre_ping=Config.Database.pool_pre_ping         # Testa a conexão antes de usar
)

# 2. O gerador de Sessions (Fábrica)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os Models herdarem
Base = declarative_base()

# 3. A DEPENDÊNCIA DO FASTAPI (Gerencia o ciclo de vida da Session)
def get_db():
    """
    Função geradora (yield) para injeção de dependência.
    Cria uma session única para cada requisição HTTP e garante 
    o fechamento dela ao final do ciclo.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
