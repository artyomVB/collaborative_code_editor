import sqlalchemy

from models.base import Base


class Change(Base):
    __tablename__ = "changes"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    sid = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('sessions.id'))
    delta = sqlalchemy.Column(sqlalchemy.String(1000))
