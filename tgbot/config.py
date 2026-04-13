from pydantic import BaseModel, Field
from typing import List

class Settings(BaseModel):
    """Класс для хранения конфигурационных переменных через pydantic"""

    BOT_TOKEN: str = Field(...)
    CHAT_IDS: str = Field(...)
    API_HOST: str = Field(default="localhost")
    API_PORT: int = Field(default=8080)
    ADMIN_LOGIN: str = Field(default="admin")
    ADMIN_PASSWORD: str = Field(default="admin123")
    SECRET: str = Field(default="secret")
    
    STATUS_NEW: str = "new"
    STATUS_IN_PROGRESS: str = "in_progress"
    STATUS_DONE: str = "done"
    STATUS_CANCELLED: str = "cancelled"
    
    STATUS_TEXT: dict = {
        "new": "Новый заказ",
        "in_progress": "В обработке",
        "done": "Выполнен",
        "cancelled": "Отменен"
    }
    
    @property
    def API_URL(self) -> str:
        return f"http://{self.API_HOST}:{self.API_PORT}"
    
    @property
    def CHAT_ID_LIST(self) -> List[str]:
        return [chat_id.strip() for chat_id in self.CHAT_IDS.split(",") if chat_id.strip()]

import os
from pathlib import Path

env_path = Path(__file__).parent / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_path)

config = Settings(**{k: v for k, v in os.environ.items()})
