
import asyncio

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
