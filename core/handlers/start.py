import logging

from aiogram import Router, types
from aiogram.filters import CommandStart

log = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message) -> None:
    log.info(
        "/start from %s (id=%d, chat=%d)",
        message.from_user.full_name if message.from_user else "?",
        message.from_user.id if message.from_user else 0,
        message.chat.id,
    )
    await message.answer(
        f"Hi!, {message.from_user.full_name}" "\nCommands: /start, /status, /players"
    )
