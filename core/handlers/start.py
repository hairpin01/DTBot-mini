from aiogram import Router
from aiogram import types
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        f"Hi!, {message.from_user.full_name}"
        "\nCommands: /start, /status, /players"
    )
