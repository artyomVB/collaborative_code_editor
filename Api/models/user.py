import sqlalchemy

from models.base import Base


class User(Base):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    login = sqlalchemy.Column(sqlalchemy.String(30), nullable=False)
    password = sqlalchemy.Column(sqlalchemy.BigInteger, nullable=False)
    token = sqlalchemy.Column(sqlalchemy.String(30))
    exp_token = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True))
    refresh_token = sqlalchemy.Column(sqlalchemy.String(30))
    exp_refresh = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True))
    sessions = sqlalchemy.orm.relationship(
        'Session', secondary='users_to_sessions', back_populates='users', lazy=True
    )
