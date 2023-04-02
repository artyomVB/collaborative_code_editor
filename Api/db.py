from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker

from settings.db_settings import DBSettings


@lru_cache(maxsize=1, typed=True)
def get_engine_singleton() -> Engine:
    db_settings = DBSettings()
    engine = create_engine(
        f"postgresql://{db_settings.login}:{db_settings.password}@{db_settings.host}/{db_settings.name}",
        echo=True,
        isolation_level='REPEATABLE READ'
    )
    return engine


@contextmanager
def get_session():
    engine = get_engine_singleton()
    with scoped_session(sessionmaker(bind=engine))() as session:
        yield session
