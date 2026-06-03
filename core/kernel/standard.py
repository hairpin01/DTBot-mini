
import os
import logging

from mcstatus import JavaServer 
from aiogram import Bot, Dispatcher, Router

from core.lib.cache import TTLCache

class Kernel:
    """
    Kernel class for the DTBot.
    """

    def __init__(self) -> None:
        self.cache: TTLCache = TTLCache(max_size=10, ttl=60)
        self.BOT_TOKEN: str = os.environ.get("BOT_TOKEN") 
        self.router: Router = Router()
        self.logger: logging.Logger | None = None
        self.client: Bot | None = None
        self.dp: Dispatcher | None = None
   
    async def init_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    async def init_client(self) -> str | None:
        if self.BOT_TOKEN is None:
            self.logger.error("BOT_TOKEN is not set")
            return None

        self.client = Bot(token=self.BOT_TOKEN)
        self.dp = Dispatcher(self.client)
        self.dp.include_router(self.router)
        
        await dp.start_polling()

    async def run(self):
        
        try:
            await self.init_logger()
            await self.init_client()
        except Exception as e:
            self.logger.error(e)
            return None



