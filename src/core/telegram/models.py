from pydantic import BaseModel


class TelegramMessage(BaseModel):
    name: str
    message: str
    date: str

