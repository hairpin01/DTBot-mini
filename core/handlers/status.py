
import html

from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router

from core.lib.status import ServerStatus

router = Router() 

@router.message(Command('status'))
async def status(message: Message):
    status = ServerStatus() 

    await status.update_status()

    if not status.is_online:
        await message.answer('Server is offline')
        return 

    s = status.get_status()
    
    motd = html.escape(str(s.description))

    await message.answer(
        f"<tg-emoji emoji-id=\"6010424470072728569\">👑</tg-emoji> <b>Server is online</b>\n"
        f"<blockquote><tg-emoji emoji-id=\"6010179687001627189\">😮</tg-emoji> Players: <code>{s.players.online}/{s.players.max}</code>\n"
        f"<tg-emoji emoji-id=\"6012525980390791480\">😐</tg-emoji> Ping: <code>{s.latency:.0f}ms</code>\n"
        f"<tg-emoji emoji-id=\"6010570945637392851\">🥳</tg-emoji> MOTD: <i>{motd}</i></blockquote>", parse_mode='HTML'
    )

