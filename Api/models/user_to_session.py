import sqlalchemy

from models.base import Base


class UserToSession(Base):
    __tablename__ = 'users_to_sessions'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    session_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('sessions.id'))
    cursor_x = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    cursor_y = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    owner = sqlalchemy.Column(sqlalchemy.Boolean, default=True)