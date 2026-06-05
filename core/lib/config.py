import logging
import os
from pathlib import Path

from dotenv import load_dotenv

log = logging.getLogger(__name__)


class Config:

    def __init__(self) -> None:
        env_path = Path(".env")
        loaded = load_dotenv(dotenv_path=env_path, verbose=False)
        if loaded:
            log.info("Loaded environment from %s", env_path.resolve())
        else:
            log.warning("No .env file found at %s, falling back to system env", env_path.resolve())
        self.config = os.getenv

    def get(self, key: str, default: str | None = None) -> str | None:
        value = os.environ.get(key, default)
        if value is None:
            log.debug("Config key '%s' not set, using default=%r", key, default)
        return value

    def set(self, key: str, value: str) -> None:
        os.environ[key] = value
        log.debug("Config key '%s' set", key)

    def unset(self, key: str) -> None:
        os.environ.pop(key, None)
        log.debug("Config key '%s' unset", key)

