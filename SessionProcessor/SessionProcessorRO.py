import websockets
import asyncio
import json
from aio_pika import connect, ExchangeType

from settings.rabbit_settings import RabbitSettings


class SessionProcessorRO:
    def __init__(self):
        self.users_to_ws = {}
        self.active_sessions = {}
        self.users_to_sessions = {}
        self.async_session = None

        self.connection = None
        self.channel = None
        self.queue = None

    async def set_up(self):
        rabbit_settings = RabbitSettings()
        self.connection = await connect(
            f"amqp://{rabbit_settings.login}:{rabbit_settings.password}@{rabbit_settings.host}/"
        )
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue(exclusive=True)

    async def callback(self, message):
        async with message.process():
            print(message.body)
            data = json.loads(message.body)
            for user in self.active_sessions[data["sid"]]:
                await self.users_to_ws[user].send(json.dumps(data["event"]))

    async def process(self, websocket):
        while True:
            msg = await websocket.recv()
            data = json.loads(msg)
            print(data)
            if data["type"] == "enter":
                self.users_to_ws[data["uid"]] = websocket
            elif data["type"] == "enter_session":
                self.users_to_sessions[data["uid"]] = data["sid"]
                self.active_sessions[data["sid"]] = self.active_sessions.get(data["sid"], set())
                self.active_sessions[data["sid"]].add(data["uid"])
                exch = await self.channel.declare_exchange(str(data["sid"]), ExchangeType.FANOUT)
                await self.queue.bind(exch)
            elif data["type"] == "exit_session":
                sid = self.users_to_sessions[data["uid"]]
                self.active_sessions[sid].discard(data["uid"])

    async def run(self):
        async with websockets.serve(self.process, "0.0.0.0", 8081) as websocket:
            await asyncio.Future()

    async def queue_handler(self):
        await self.queue.consume(self.callback)
        await asyncio.Future()


async def main():
    sp = SessionProcessorRO()
    await sp.set_up()
    t1 = asyncio.create_task(sp.run())
    t2 = asyncio.create_task(sp.queue_handler())
    await t1
    await t2

asyncio.run(main())