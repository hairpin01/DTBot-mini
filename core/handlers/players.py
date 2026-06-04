import html

from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router

from core.lib.status import ServerStatus

router = Router()

_E_HEAD  = '<tg-emoji emoji-id="6010053926064232198">🐱</tg-emoji>'
_E_COUNT = '<tg-emoji emoji-id="6012473147998084083">🙏</tg-emoji>'
_E_EMPTY = '<tg-emoji emoji-id="6010394680179562842">😶</tg-emoji>'
_E_ROW   = '<tg-emoji emoji-id="6010179991944305029">☺️</tg-emoji>'


@router.message(Command('players'))
async def cmd_players(message: Message):
    status = ServerStatus()
    await status.update_status()

    if not status.is_online:
        await message.answer('Server is offline')
        return

    s = status.get_status()
    sample = s.players.sample or []
    online, maximum = s.players.online, s.players.max

    if not sample:
        await message.answer(
            f"{_E_EMPTY} <b>No players online</b> "
            f"(<code>{online}/{maximum}</code>)",
            parse_mode='HTML',
        )
        return

    rows = "\n".join(
        f"{_E_ROW} <code>{html.escape(p.name)}</code>"
        for p in sample
    )

    await message.answer(
        f"{_E_HEAD} <b>Players online</b>\n"
        f"{_E_COUNT} Total: <code>{online}/{maximum}</code>\n"
        f"<blockquote expandable>{rows}</blockquote>",
        parse_mode='HTML',
    )
