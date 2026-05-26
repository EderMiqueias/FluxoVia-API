from pydantic import BaseModel, EmailStr


class TicketSchema(BaseModel):
    placa: str
    velocidade_registrada: int
    limite_permitido: int
    id_aparelho_medidor: str
    proprietario: str
    uf: str
    email_condutor: EmailStr

    class Config:
        from_attributes = True

