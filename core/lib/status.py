import logging
from typing import Any

from mcstatus import JavaServer
from mcstatus.responses import JavaStatusResponse

from .config import Config

log = logging.getLogger(__name__)


class ServerStatus:
    def __init__(self) -> None:
        self.config = Config()

        host: str = self.config.get("SERVER_IP", "localhost")
        port: int = int(self.config.get("SERVER_PORT", "25565"))
        address = f"{host}:{port}"

        log.info("ServerStatus targeting %s", address)
        self.server: JavaServer = JavaServer.lookup(address)
        self._status: Any | None = None

    async def update_status(self) -> JavaStatusResponse | None:
        try:
            self._status = await self.server.async_status()
            log.info(
                "Server status: online | %d/%d players, %.0fms ping",
                self._status.players.online,
                self._status.players.max,
                self._status.latency,
            )
        except Exception as exc:
            log.warning("Server status: offline (%s: %s)", type(exc).__name__, exc)
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
