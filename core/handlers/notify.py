import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message

from core.lib.config import Config
from core.lib.status import ServerStatus

router = Router()
log = logging.getLogger(__name__)

_ENV_FILE = Path(".env")
_DEFAULT_INTERVAL = 30

_E_ONLINE = '<tg-emoji emoji-id="6010424470072728569">👑</tg-emoji>'
_E_OFFLINE = '<tg-emoji emoji-id="6012525980390791480">😐</tg-emoji>'
_E_OK = '<tg-emoji emoji-id="6012562513382612008">☺️</tg-emoji>'
_E_WARN = '<tg-emoji emoji-id="6010394680179562842">😶</tg-emoji>'
_E_INFO = '<tg-emoji emoji-id="6010053926064232198">🐱</tg-emoji>'
_E_SET = '<tg-emoji emoji-id="6010179991944305029">☺️</tg-emoji>'


def _to_int(val) -> int | None:
    try:
        return int(val) if val is not None else None
    except (ValueError, TypeError):
        return None


def _env_write(key: str, value: str) -> None:
    """Update an existing key in .env or append it."""
    try:
        if _ENV_FILE.exists():
            lines = _ENV_FILE.read_text().splitlines()
            for i, line in enumerate(lines):
                if line.lstrip().startswith(f"{key}="):
                    lines[i] = f"{key}={value}"
                    _ENV_FILE.write_text("\n".join(lines) + "\n")
                    return
            # Key absent — append under a blank line
            with _ENV_FILE.open("a") as f:
                f.write(f"\n{key}={value}\n")
        else:
            _ENV_FILE.write_text(f"{key}={value}\n")
    except Exception as e:
        log.error("env_write(%s) failed: %s", key, e)


class Notifier:
    def __init__(self, bot: Bot, config: Config) -> None:
        self.bot = bot
        self._task: asyncio.Task | None = None
        self._last_online: bool | None = None

        self.admin_id: int | None = _to_int(config.get("ADMIN_ID"))
        self.chat_id: int | None = _to_int(config.get("NOTIFY_CHAT_ID"))
        self.topic_id: int | None = _to_int(config.get("NOTIFY_TOPIC_ID"))
        self.interval: int = (
            _to_int(config.get("NOTIFY_POLL_INTERVAL")) or _DEFAULT_INTERVAL
        )
        self.enabled: bool = (config.get("NOTIFY_ENABLED") or "").lower() == "true"

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._poll())
            log.info(
                "Notifier: started (interval=%ds, chat=%s, topic=%s)",
                self.interval,
                self.chat_id,
                self.topic_id,
            )

    def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
        self._task = None
        self._last_online = None
        log.info("Notifier: stopped")

    def _save_chat(self) -> None:
        _env_write("NOTIFY_CHAT_ID", str(self.chat_id or ""))

    def _save_topic(self) -> None:
        _env_write("NOTIFY_TOPIC_ID", str(self.topic_id or ""))

    def _save_enabled(self) -> None:
        _env_write("NOTIFY_ENABLED", "true" if self.enabled else "false")

    async def _send(self, text: str) -> None:
        if not self.chat_id:
            return
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                message_thread_id=self.topic_id,
                text=text,
                parse_mode="HTML",
            )
        except Exception as e:
            log.error("Notifier: send failed: %s", e)

    async def _poll(self) -> None:
        while True:
            try:
                srv = ServerStatus()
                await srv.update_status()
                online = srv.is_online

                if self._last_online is None:
                    self._last_online = online
                    log.info(
                        "Notifier: initial state — %s",
                        "online" if online else "offline",
                    )

                elif online != self._last_online:
                    if online:
                        s = srv.get_status()
                        await self._send(
                            f"{_E_ONLINE} <b>Server is back online</b>\n"
                            f"<blockquote>"
                            f"Players: <code>{s.players.online}/{s.players.max}</code>\n"
                            f"Ping:    <code>{s.latency:.0f}ms</code>"
                            f"</blockquote>"
                        )
                    else:
                        await self._send(
                            f"{_E_OFFLINE} <b>Server went offline</b>\n"
                            f"<blockquote>"
                            f"Next check in <code>{self.interval}s</code>"
                            f"</blockquote>"
                        )
                    self._last_online = online

            except asyncio.CancelledError:
                break
            except Exception as e:
                log.error("Notifier poll error: %s", e)

            await asyncio.sleep(self.interval)

    def is_admin(self, user_id: int) -> bool:
        return self.admin_id is not None and user_id == self.admin_id

    def status_text(self) -> str:
        state = "✅ enabled" if self.enabled else "❌ disabled"
        running = "🔄 running" if self._task and not self._task.done() else "⏹ idle"
        chat = f"<code>{self.chat_id}</code>" if self.chat_id else "—"
        topic = f"<code>{self.topic_id}</code>" if self.topic_id else "—"
        admin = f"<code>{self.admin_id}</code>" if self.admin_id else "—"
        return (
            f"{_E_INFO} <b>Notifier</b>\n"
            f"<blockquote>"
            f"State:    {state}\n"
            f"Task:     {running}\n"
            f"Interval: <code>{self.interval}s</code>"
            f"</blockquote>\n"
            f"<blockquote expandable>"
            f"Chat ID:  {chat}\n"
            f"Topic ID: {topic}\n"
            f"Admin ID: {admin}"
            f"</blockquote>"
        )


_notifier: Notifier | None = None


def init_notifier(bot: Bot, config: Config) -> Notifier:
    global _notifier
    _notifier = Notifier(bot, config)
    if _notifier.enabled and _notifier.chat_id:
        _notifier.start()
    return _notifier


def _n() -> Notifier | None:
    return _notifier


def _admin(message: Message) -> Notifier | None:
    n = _n()
    if n is None or not n.is_admin(message.from_user.id):
        return None
    return n


@router.message(Command("notify"))
async def cmd_notify(message: Message):
    n = _n()
    if n is None:
        return

    if not n.is_admin(message.from_user.id):
        await message.answer(
            f"{_E_WARN} <b>Not allowed</b>",
            parse_mode="HTML",
        )
        return

    args = message.text.split(maxsplit=1)
    sub = args[1].strip().lower() if len(args) > 1 else ""

    match sub:
        case "on":
            if not n.chat_id:
                await message.answer(
                    f"{_E_WARN} <b>No target chat</b>\n"
                    f"<blockquote>Use /setchat first</blockquote>",
                    parse_mode="HTML",
                )
                return
            n.enabled = True
            n._save_enabled()
            n.start()
            await message.answer(
                f"{_E_OK} <b>Notifications enabled</b>\n"
                f"<blockquote>"
                f"Chat:     <code>{n.chat_id}</code>\n"
                f"Topic:    <code>{n.topic_id}</code>\n"
                f"Interval: <code>{n.interval}s</code>"
                f"</blockquote>",
                parse_mode="HTML",
            )

        case "off":
            n.enabled = False
            n._save_enabled()
            n.stop()
            await message.answer(
                f"{_E_OK} <b>Notifications disabled</b>",
                parse_mode="HTML",
            )

        case "status":
            await message.answer(n.status_text(), parse_mode="HTML")

        case _:
            await message.answer(
                f"{_E_INFO} <b>Usage</b>\n"
                f"<blockquote>"
                f"/notify on\n"
                f"/notify off\n"
                f"/notify status"
                f"</blockquote>",
                parse_mode="HTML",
            )


@router.message(Command("setchat"))
async def cmd_setchat(message: Message):
    n = _admin(message)
    if n is None:
        await message.answer(
            f"{_E_WARN} <b>Not allowed</b>",
            parse_mode="HTML",
        )
        return

    old = n.chat_id
    n.chat_id = message.chat.id
    n._save_chat()
    await message.answer(
        f"{_E_SET} <b>Chat updated</b>\n"
        f"<blockquote>"
        f"New: <code>{n.chat_id}</code>\n"
        f"Old: <code>{old}</code>"
        f"</blockquote>",
        parse_mode="HTML",
    )


@router.message(Command("settopic"))
async def cmd_settopic(message: Message):
    n = _admin(message)
    if n is None:
        await message.answer(
            f"{_E_WARN} <b>Not allowed</b>",
            parse_mode="HTML",
        )
        return

    tid = message.message_thread_id
    if tid is None:
        await message.answer(
            f"{_E_WARN} <b>Not a topic thread</b>\n"
            f"<blockquote>Send this command inside a topic</blockquote>",
            parse_mode="HTML",
        )
        return

    old = n.topic_id
    n.topic_id = tid
    n._save_topic()
    await message.answer(
        f"{_E_SET} <b>Topic updated</b>\n"
        f"<blockquote>"
        f"New: <code>{n.topic_id}</code>\n"
        f"Old: <code>{old}</code>"
        f"</blockquote>",
        parse_mode="HTML",
    )
