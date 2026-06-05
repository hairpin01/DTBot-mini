
import asyncio
import sys
from pathlib import Path

# Ensure the project root is on sys.path so 'core' package is always importable
# (handles direct execution like `python core/__main__.py` in Pterodactyl)
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

async def main():
    print('Stating kernel...')

    try:
        from core.kernel.standard import Kernel
    except Exception as e:
        print(f"Failed to import kernel: {e}")
        return
    print('starting...')
    kernel = Kernel()
    
    await kernel.run()


if __name__ == '__main__':
    asyncio.run(main())
