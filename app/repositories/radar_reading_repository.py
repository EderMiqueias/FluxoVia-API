from decimal import Decimal
from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import Session

from app.models.radar_reading import RadarReading


class RadarReadingRepository:
    """
    Repositório para operações de persistência da entidade RadarReading.
    
    Implementa o padrão Repository, isolando a lógica de acesso a dados
    e fornecendo uma interface limpa e type-safe para operações no banco.
    
    Atributos:
        session: Sessão do SQLAlchemy para comunicação com o banco.
    """

    def __init__(self, session: Session) -> None:
        """
        Inicializa o repositório com uma sessão do banco de dados.
        
        Args:
            session: Uma instância de Session do SQLAlchemy.
        """
        self.session: Session = session

    def create_reading(
        self,
        id_aparelho_medidor: str,
        placa: str,
        velocidade_registrada: Decimal,
    ) -> RadarReading:
        """
        Cria e persiste um novo registro de leitura de radar.
        
        Args:
            id_aparelho_medidor: Identificador do aparelho de medição.
            placa: Placa do veículo.
            velocidade_registrada: Velocidade registrada em km/h.
            
        Returns:
            RadarReading: O objeto criado com o ID gerado pelo banco.
            
        Raises:
            SQLAlchemyError: Em caso de erro na execução da query.
        """
        reading = RadarReading(
            id_aparelho_medidor=id_aparelho_medidor,
            placa=placa,
            velocidade_registrada=velocidade_registrada,
        )
        self.session.add(reading)
        self.session.flush()  # Flush para gerar o ID sem commitar
        self.session.refresh(reading)  # Recarrega para obter os dados do servidor
        return reading

    def get_by_id(self, reading_id: int) -> Optional[RadarReading]:
        """
        Recupera um registro de leitura por seu ID.
        
        Args:
            reading_id: Identificador único da leitura.
            
        Returns:
            RadarReading se encontrado, None caso contrário.
            
        Raises:
            SQLAlchemyError: Em caso de erro na execução da query.
        """
        query = select(RadarReading).where(RadarReading.id == reading_id)
        result = self.session.execute(query)
        return result.scalars().first()

    def get_by_placa(
        self,
        placa: str,
        limit: int = 50,
    ) -> list[RadarReading]:
        """
        Recupera registros de leitura filtrando por placa do veículo.
        
        Os resultados são ordenados pela data de criação em ordem decrescente
        (mais recentes primeiro).
        
        Args:
            placa: Placa do veículo a filtrar.
            limit: Número máximo de registros a retornar (padrão: 50).
            
        Returns:
            Lista de RadarReading encontrados, ordenados por data decrescente.
            
        Raises:
            SQLAlchemyError: Em caso de erro na execução da query.
        """
        query = (
            select(RadarReading)
            .where(RadarReading.placa == placa)
            .order_by(desc(RadarReading.created_at))
            .limit(limit)
        )
        result = self.session.execute(query)
        return result.scalars().all()

    def get_latest_by_aparelho(
        self,
        id_aparelho_medidor: str,
        limit: int = 100,
    ) -> list[RadarReading]:
        """
        Recupera os registros mais recentes de um aparelho de medição específico.
        
        Os resultados são ordenados pela data de criação em ordem decrescente
        (mais recentes primeiro).
        
        Args:
            id_aparelho_medidor: Identificador do aparelho de medição.
            limit: Número máximo de registros a retornar (padrão: 100).
            
        Returns:
            Lista de RadarReading do aparelho, ordenados por data decrescente.
            
        Raises:
            SQLAlchemyError: Em caso de erro na execução da query.
        """
        query = (
            select(RadarReading)
            .where(RadarReading.id_aparelho_medidor == id_aparelho_medidor)
            .order_by(desc(RadarReading.created_at))
            .limit(limit)
        )
        result = self.session.execute(query)
        return result.scalars().all()
