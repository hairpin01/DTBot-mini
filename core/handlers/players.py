import html
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from core.lib.status import ServerStatus

log = logging.getLogger(__name__)

router = Router()

_E_HEAD = '<tg-emoji emoji-id="6010053926064232198">🐱</tg-emoji>'
_E_COUNT = '<tg-emoji emoji-id="6012473147998084083">🙏</tg-emoji>'
_E_EMPTY = '<tg-emoji emoji-id="6010394680179562842">😶</tg-emoji>'
_E_ROW = '<tg-emoji emoji-id="6010179991944305029">☺️</tg-emoji>'


@router.message(Command("players"))
async def cmd_players(message: Message) -> None:
    chat_info = f"chat=%d, user=%d" % (message.chat.id, message.from_user.id if message.from_user else 0)
    log.info("/players requested — %s", chat_info)

    status = ServerStatus()
    await status.update_status()

    if not status.is_online:
        log.info("/players result — server offline (%s)", chat_info)
        await message.answer("Server is offline")
        return

    s = status.get_status()
    sample = s.players.sample or []
    online, maximum = s.players.online, s.players.max

    log.info(
        "/players result — %d/%d online, %d in sample (%s)",
        online, maximum, len(sample),
        chat_info,
    )

    if not sample:
        if online > 0:
            msg = (
                f"{_E_HEAD} <b>Players online</b>\n"
                f"{_E_COUNT} Total: <code>{online}/{maximum}</code>\n"
                f"<blockquote>Nicknames hidden (server proxy)</blockquote>"
            )
        else:
            msg = (
                f"{_E_EMPTY} <b>No players online</b> "
                f"(<code>{online}/{maximum}</code>)"
            )
        await message.answer(msg, parse_mode="HTML")
        return

    rows = "\n".join(f"{_E_ROW} <code>{html.escape(p.name)}</code>" for p in sample)

    await message.answer(
        f"{_E_HEAD} <b>Players online</b>\n"
        f"{_E_COUNT} Total: <code>{online}/{maximum}</code>\n"
        f"<blockquote expandable>{rows}</blockquote>",
        parse_mode="HTML",
    )
