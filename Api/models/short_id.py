import sqlalchemy

from models.base import Base


class ShortId(Base):
    __tablename__ = "short_ids"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    short_id = sqlalchemy.Column(sqlalchemy.String(5))
    long_id = sqlalchemy.Column(sqlalchemy.String(16), sqlalchemy.ForeignKey('sessions.sid'))
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True))