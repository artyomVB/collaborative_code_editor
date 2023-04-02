import sqlalchemy

from db import get_session
from setup_db import UserToSession, Session

with get_session() as session:
    sessions = session.query(UserToSession, Session).filter_by(user_id=1, session_id=1, owner=True).join(Session).all()
    print(sessions)
