import sqlalchemy

from models.base import Base


class Session(Base):
    __tablename__ = 'sessions'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(30), nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String(10000))
    sid = sqlalchemy.Column(sqlalchemy.String(16), unique=True)
    users = sqlalchemy.orm.relationship(
        'User', secondary='users_to_sessions', back_populates='sessions', lazy=True
    )
    short_id = sqlalchemy.orm.relationship("ShortId", backref="session_id")