from typing import Any

from mcstatus import JavaServer

from .config import Config

class ServerStatus:
    def __init__(self):
        self.config = Config()

        host: str = self.config.get("SERVER_IP", "localhost")
        port: int = int(self.config.get("SERVER_PORT", "25565"))

        self.server: JavaServer = JavaServer.lookup(f"{host}:{port}")
        self._status: Any | None = None

    async def update_status(self) -> JavaStatusResponse | None:
        try:
            self._status = await self.server.async_status()
        except Exception:
            self._status = None

        return self._status

    def get_status(self) -> JavaStatusResponse | None:
        return self._status

    @property
    def is_online(self) -> bool:
        return self._status is not None

    @property
    def players_online(self) -> int:
        if self._status is None:
            return 0
        return self._status.players.online
