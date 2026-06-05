import logging

from aiogram import Bot, Dispatcher, Router

from core.lib.cache import TTLCache
from core.lib.config import Config

# Bot modules
from core.handlers import (
    start,
    status,
    players,
    notify,
)

log = logging.getLogger(__name__)


class Kernel:
    """
    Kernel class for the DTBot.
    """

    def __init__(self) -> None:
        self.logger: logging.Logger | None = None
        self.cache: TTLCache = TTLCache(max_size=10, ttl=60)
        self.config: Config = Config()
        self.BOT_TOKEN: str | None = self.config.get("BOT_TOKEN")
        self.router: Router = Router()
        self.client: Bot | None = None
        self.dp: Dispatcher | None = None

    def _init_logger(self) -> None:
        self.logger = log
        # basicConfig is already called in __main__.py — no extra handlers needed

    def _init_client(self) -> str | None:
        if self.BOT_TOKEN is None:
            self.logger.error("BOT_TOKEN is not set — cannot start bot")
            return None

        token_preview = self.BOT_TOKEN[:6] + "..." if len(self.BOT_TOKEN) > 6 else "?"
        self.logger.info("Initialising bot (token=%s)", token_preview)

        self.client = Bot(token=self.BOT_TOKEN)
        self.dp = Dispatcher()

        routers = [start.router, status.router, players.router, notify.router, self.router]
        for r in routers:
            self.logger.debug("Including router: %s", r)
        self.dp.include_routers(*routers)
        self.logger.info("Registered %d routers", len(routers))

        return self.BOT_TOKEN

    async def run(self) -> None:
        self._init_logger()
        log.info("Kernel boot sequence started")

        try:
            self._init_client()
        except Exception as e:
            log.exception("Client initialisation failed")
            return

        notifier = notify.init_notifier(self.client, self.config)
        if notifier and notifier.enabled:
            log.info(
                "Notifier enabled (chat=%s, interval=%ds)",
                notifier.chat_id,
                notifier.interval,
            )
        else:
            log.info("Notifier disabled")

        log.info("Bot started — entering polling loop")
        try:
            await self.dp.start_polling(self.client)
        finally:
            log.info("Bot polling stopped")
