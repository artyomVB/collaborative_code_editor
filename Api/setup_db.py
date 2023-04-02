import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy_utils import create_database, database_exists

from models.base import Base
from models.change import Change
from models.short_id import ShortId
from models.user import User
from models.user_to_session import UserToSession
from models.session import Session
from settings.db_settings import DBSettings


if __name__ == "__main__":
    db_settings = DBSettings()
    db_conn_str = f"postgresql://{db_settings.login}:{db_settings.password}@{db_settings.host}/{db_settings.name}"
    if not database_exists(db_conn_str):
        create_database(db_conn_str)
    engine = sqlalchemy.create_engine(db_conn_str)
    Base.metadata.create_all(bind=engine)
    Session = scoped_session(sessionmaker(bind=engine))
    s = "ABCde"
    with Session() as session, session.begin():
        for i1 in range(5):
            for i2 in range(5):
                for i3 in range(5):
                    for i4 in range(5):
                        for i5 in range(5):
                            short_id = ShortId(short_id=s[i1] + s[i2] + s[i3] + s[i4] + s[i5], long_id=None, timestamp=None)
                            session.add(short_id)
