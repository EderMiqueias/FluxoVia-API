from decimal import Decimal
from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

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
    
    def get_by_id_aparelho_medidor(self, id_aparelho_medidor: str) -> Optional[RadarReading]:
        """
        Recupera o registro mais recente de leitura para um aparelho de medição específico.
        
        Args:
            id_aparelho_medidor: Identificador do aparelho de medição.
            
        Returns:
            RadarReading mais recente para o aparelho, ou None se não encontrado.
            
        Raises:
            SQLAlchemyError: Em caso de erro na execução da query.
        """
        # TODO: Implementar a query para buscar todos os registros a partir do id_aparelho_medidor e remover o raise abaixo
        raise NotImplementedError("Método get_by_id_aparelho_medidor ainda não implementado")
        query = {  }
        result = self.session.execute(query)
        return result.scalars().all()

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
