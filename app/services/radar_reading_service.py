from app.repositories.radar_reading_repository import RadarReadingRepository

# TODO: Implementar a lógica de negócio para o serviço de leitura de radar, utilizando o repositório para persistência e consulta dos dados.

class RadarReadingService:
    radar_reading_repository: RadarReadingRepository

    def __init__(self, radar_reading_repository: RadarReadingRepository):
        self.radar_reading_repository = radar_reading_repository

    def create_radar_reading(self, payload: dict):
        raise NotImplementedError("Método create_radar_reading ainda não implementado")

    def consult_radar_reading_by_id_aparelho_medidor(self, id_aparelho_medidor: str):
        raise NotImplementedError("Método consult_radar_reading_by_id_aparelho_medidor ainda não implementado")
