"""
Módulo de modelos SQLAlchemy da aplicação.

Contém as definições de todos os modelos de banco de dados utilizados pela API.
"""

from app.models.radar_reading import Base, RadarReading

__all__ = ["Base", "RadarReading"]
