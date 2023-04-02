import websockets
import asyncio
import json
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
import pika

import sys

from settings.db_settings import DBSettings
from settings.rabbit_settings import RabbitSettings

sys.path.insert(1, '../Api')

from models.user import User
from models.short_id import ShortId
from models.change import Change
from models.user_to_session import UserToSession
from models.session import Session


class SessionProcessor:
    def __init__(self):
        self.users_to_ws = {}
        self.active_sessions = {}
        self.users_to_sessions = {}
        self.async_session = None
        rabbit_settings = RabbitSettings()
        credentials = pika.PlainCredentials(rabbit_settings.login, rabbit_settings.password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbit_settings.host, port=rabbit_settings.port, credentials=credentials)
        )
        self.channel = self.connection.channel()
        self.exchanges = set()

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
                self.channel.exchange_declare(exchange=str(data["sid"]), exchange_type='fanout')
            elif data["type"] == "exit_session":
                sid = self.users_to_sessions[data["uid"]]
                async with self.async_session() as session, session.begin():
                    stm = select(UserToSession).filter_by(session_id=sid).filter_by(user_id=data["uid"])
                    res = await session.execute(stm)
                    res = res.one()
                    res[0].cursor_x = data["cursor_x"]
                    res[0].cursor_y = data["cursor_y"]
                    session.add(res[0])
                self.active_sessions[sid].discard(data["uid"])
            else:
                async with self.async_session() as session, session.begin():
                    ch = Change(sid=data["sid"], delta=json.dumps(data["event"]))
                    session.add(ch)
                    smt = select(Session).filter_by(id=data["sid"])
                    res = await session.execute(smt)
                    res = res.one()
                    res[0].text = data["text"]
                    session.add(res[0])
                self.channel.basic_publish(exchange=str(data["sid"]), routing_key='', body=msg)
                for user in self.active_sessions[data["sid"]]:
                    if self.users_to_ws[user] != websocket:
                        await self.users_to_ws[user].send(json.dumps(data["event"]))

    async def run(self):
        db_settings = DBSettings()
        engine = create_async_engine(
            f"postgresql+asyncpg://{db_settings.login}:{db_settings.password}@{db_settings.host}/{db_settings.name}"
        )
        self.async_session = sqlalchemy.orm.sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        async with websockets.serve(self.process, "0.0.0.0", 8080) as websocket:
            await asyncio.Future()


sp = SessionProcessor()
asyncio.run(sp.run())
