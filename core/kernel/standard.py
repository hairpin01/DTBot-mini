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

    def _init_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _init_client(self) -> str | None:
        if self.BOT_TOKEN is None:
            self.logger.error("BOT_TOKEN is not set")
            return None

        self.client = Bot(token=self.BOT_TOKEN)
        self.dp = Dispatcher()

        # Include the router command
        self.dp.include_routers(
            start.router,
            status.router,
            players.router,
            notify.router,
            self.router
        )


    async def run(self):

        self._init_logger()

        try:
            self._init_client()
        except Exception as e:
            self.logger.error(e)
            return None

        notify.init_notifier(self.client, self.config)

        self.logger.info("Bot started")
        await self.dp.start_polling(self.client)
