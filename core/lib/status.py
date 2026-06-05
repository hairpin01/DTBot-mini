import asyncio
import logging
from typing import Any

from mcstatus import JavaServer
from mcstatus.responses import JavaStatusResponse

from .config import Config

log = logging.getLogger(__name__)

_RETRIES: int = 3
_RETRY_DELAYS: tuple[float, ...] = (1.0, 3.0, 5.0)
_ATTEMPT_TIMEOUT: int = 8


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
        last_exc: Exception | None = None

        for attempt in range(1, _RETRIES + 1):
            try:
                self._status = await asyncio.wait_for(
                    self.server.async_status(),
                    timeout=_ATTEMPT_TIMEOUT,
                )
                log.info(
                    "Server status: online | %d/%d players, %.0fms ping",
                    self._status.players.online,
                    self._status.players.max,
                    self._status.latency,
                )
                return self._status
            except asyncio.TimeoutError:
                last_exc = None  # don't log timeout as error
                log.warning(
                    "Status attempt %d/%d timed out after %ds",
                    attempt, _RETRIES, _ATTEMPT_TIMEOUT,
                )
            except Exception as exc:
                last_exc = exc
                log.warning(
                    "Status attempt %d/%d failed: %s: %s",
                    attempt, _RETRIES, type(exc).__name__, exc,
                )

            self._status = None

            if attempt < _RETRIES:
                delay = _RETRY_DELAYS[min(attempt - 1, len(_RETRY_DELAYS) - 1)]
                log.debug("Retrying in %.1fs...", delay)
                await asyncio.sleep(delay)

        log.error(
            "Server unreachable after %d attempts (last: %s)",
            _RETRIES,
            type(last_exc).__name__ if last_exc else "timeout",
        )
        return None

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
