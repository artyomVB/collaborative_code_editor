import asyncio
import time


async def func(d):
    await asyncio.sleep(d)
    print("Done")

async def main():
    print(time.strftime('%X'))
    await asyncio.Future()
    print(time.strftime('%X'))

asyncio.run(main())
