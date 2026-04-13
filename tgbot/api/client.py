import httpx
from typing import List, Optional, Dict, Any
from config import config
from .auth import JWTAuthManager
import logging

logger = logging.getLogger(__name__)


class OrderAPI:
    """API клиент с автоматическим retry при 401"""
 
    def __init__(self):
        self.base_url = config.API_URL
        self.client: Optional[httpx.AsyncClient] = None
        self.auth = JWTAuthManager()
 
    async def __aenter__(self):
        self.client = httpx.AsyncClient()
        if not await self.auth.login(self.client):
            raise RuntimeError("Не удалось авторизоваться в API")
        return self
 
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
 
    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: Dict = None,
        retry: bool = True
    ) -> httpx.Response:
        """
        Выполняет запрос. При 401 — переавторизуется и повторяет один раз.
        """
        response = await self.client.request(
            method,
            f"{self.base_url}{path}",
            json=json,
            headers=self.auth.get_headers(),
        )
 
        if response.status_code == 401 and retry:
            logger.warning("Получен 401, пробуем переавторизоваться...")
            success = await self.auth.reauth(self.client)
            if not success:
                logger.error("Переавторизация не удалась")
                response.raise_for_status()
            return await self._request(method, path, json=json, retry=False)
 
        response.raise_for_status()
        return response
 
    async def get_orders(self) -> List[Dict[str, Any]]:
        response = await self._request("GET", "/api/admin/orders")
        return response.json()
 
    async def get_order_by_id(self, order_id: int) -> Dict[str, Any]:
        response = await self._request("GET", f"/api/admin/orders/{order_id}")
        return response.json()
 
    async def update_order_status(self, order_id: int, status: str) -> Dict[str, Any]:
        response = await self._request(
            "PATCH",
            f"/api/admin/orders/{order_id}/status",
            json={"status": status}
        )
        return response.json()
 
    async def send_order_notification(self, order_data: Dict[str, Any]) -> bool:
        try:
            response = await self._request("POST", "/api/orders", json=order_data)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления о заказе: {e}")
            return False
