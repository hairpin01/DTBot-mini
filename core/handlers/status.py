import html
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from core.lib.status import ServerStatus

log = logging.getLogger(__name__)

router = Router()


@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    chat_info = f"chat=%d, user=%d" % (message.chat.id, message.from_user.id if message.from_user else 0)
    log.info("/status requested — %s", chat_info)

    status = ServerStatus()
    await status.update_status()

    if not status.is_online:
        log.info("/status result — offline (%s)", chat_info)
        await message.answer("Server is offline")
        return

    s = status.get_status()
    motd = html.escape(str(s.description))

    log.info(
        "/status result — online | %d/%d players, %.0fms (%s)",
        s.players.online, s.players.max, s.latency,
        chat_info,
    )

    await message.answer(
        f'<tg-emoji emoji-id="6010424470072728569">👑</tg-emoji> <b>Server is online</b>\n'
        f'<blockquote><tg-emoji emoji-id="6010179687001627189">😮</tg-emoji> Players: <code>{s.players.online}/{s.players.max}</code>\n'
        f'<tg-emoji emoji-id="6012525980390791480">😐</tg-emoji> Ping: <code>{s.latency:.0f}ms</code>\n'
        f'<tg-emoji emoji-id="6010570945637392851">🥳</tg-emoji> MOTD: <i>{motd}</i></blockquote>',
        parse_mode="HTML",
    )
