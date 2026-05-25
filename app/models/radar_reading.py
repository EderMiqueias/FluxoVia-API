from datetime import datetime
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base


class RadarReading(Base):
    """
    Modelo SQLAlchemy 2.0+ para a tabela radar_readings.
    
    Representa um registro de leitura de velocidade capturada por um aparelho de medição,
    incluindo informações do veículo e timestamp do registro.
    
    Atributos:
        id: Identificador único da leitura (auto-incrementado).
        id_aparelho_medidor: Identificador do aparelho de medição.
        placa: Placa do veículo.
        velocidade_registrada: Velocidade em km/h com precisão de 2 casas decimais.
        created_at: Timestamp de criação do registro (gerado automaticamente pelo servidor).
    """

    __tablename__ = "radar_readings"
    __table_args__ = {"schema": "fluxovia"}

    # Usando as anotações modernas do SQLAlchemy 2.0: Mapped e mapped_column
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    id_aparelho_medidor: Mapped[str] = mapped_column(
        nullable=False,
        comment="Identificador único do aparelho de medição"
    )
    
    placa: Mapped[str] = mapped_column(
        nullable=False,
        comment="Placa do veículo (formato: ABC-1234)"
    )
    
    velocidade_registrada: Mapped[Decimal] = mapped_column(
        nullable=False,
        comment="Velocidade registrada em km/h"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
        comment="Timestamp de criação do registro"
    )

    def __repr__(self) -> str:
        """Representação em string do objeto RadarReading."""
        return (
            f"<RadarReading(id={self.id}, "
            f"id_aparelho_medidor={self.id_aparelho_medidor}, "
            f"placa={self.placa}, "
            f"velocidade_registrada={self.velocidade_registrada}, "
            f"created_at={self.created_at})>"
        )
