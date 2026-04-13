import httpx
from typing import Optional, Dict
from config import config
import logging

logger = logging.getLogger(__name__)


class JWTAuthManager:
    """Менеджер JWT токенов с обновлением по 401"""
 
    def __init__(self):
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
 
    async def login(self, client: httpx.AsyncClient) -> bool:
        """Выполнение авторизации и получение токенов"""
        response = await client.post(
            f"{config.API_URL}/api/auth/login",
            json={
                "login": config.ADMIN_LOGIN,
                "password": config.ADMIN_PASSWORD,
            }
        )
 
        if response.status_code != 200:
            logger.error(f"Ошибка авторизации: {response.status_code} {response.text}")
            return False
 
        data = response.json()
        self.access_token = data.get("access_token")
        self.refresh_token = data.get("refresh_token")
        logger.info("Авторизация успешна")
        return True
 
    async def try_refresh(self, client: httpx.AsyncClient) -> bool:
        """Попытка обновить токен через refresh_token"""
        if not self.refresh_token:
            return False
 
        response = await client.post(
            f"{config.API_URL}/api/auth/refresh",
            json={"refresh_token": self.refresh_token}
        )
 
        if response.status_code != 200:
            logger.warning("Refresh токен истёк или невалиден")
            self.refresh_token = None
            return False
 
        data = response.json()
        self.access_token = data.get("access_token")
        logger.info("Токен успешно обновлён")
        return True
 
    async def reauth(self, client: httpx.AsyncClient) -> bool:
        """Полная переавторизация: сначала refresh, потом login"""
        if await self.try_refresh(client):
            return True
        logger.info("Выполняем полный логин...")
        return await self.login(client)
 
    def get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
 
    def is_authenticated(self) -> bool:
        return self.access_token is not None