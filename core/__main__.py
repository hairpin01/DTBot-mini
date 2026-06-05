
import asyncio
import logging
import sys
from pathlib import Path

# Ensure the project root is on sys.path so 'core' package is always importable
# (handles direct execution like `python core/__main__.py` in Pterodactyl)
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

log = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True,
    )
    log.info("Starting kernel...")

    try:
        from core.kernel.standard import Kernel
    except Exception as e:
        log.exception("Failed to import kernel")
        return

    log.info("Kernel import successful, booting...")
    kernel = Kernel()

    await kernel.run()


if __name__ == "__main__":
    asyncio.run(main())
