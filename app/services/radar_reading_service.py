from app.repositories.radar_reading_repository import RadarReadingRepository
from app.schemas.radar_reading_schema import RadarReadingSchema
from app.schemas.ticket_schema import TicketSchema

# TODO: Implementar a lógica de negócio para o serviço de leitura de radar, utilizando o repositório para persistência e consulta dos dados.

class RadarReadingService:
    repository: RadarReadingRepository

    def __init__(self, radar_reading_repository: RadarReadingRepository):
        self.repository = radar_reading_repository

    def _generate_ticket_pdf(self, payload: TicketSchema):
        pass

    def create_radar_reading(self, payload: RadarReadingSchema):
        raise NotImplementedError("Método create_radar_reading ainda não implementado")

    def consult_radar_reading_by_id_aparelho_medidor(self, id_aparelho_medidor: str):
        raise NotImplementedError("Método consult_radar_reading_by_id_aparelho_medidor ainda não implementado")
