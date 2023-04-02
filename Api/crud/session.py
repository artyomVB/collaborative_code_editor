from datetime import datetime

from models.session import Session
from models.short_id import ShortId
from models.user_to_session import UserToSession


class SessionCrud:
    def __init__(self, session):
        self.session = session

    def get_sessions_by_user_id(self, user_id):
        sessions = self.session.query(UserToSession, Session).filter_by(user_id=user_id, owner=True).join(Session).all()
        return [session[1] for session in sessions]

    def get_session_by_id(self, session_id):
        if len(session_id) == 5:
            short_id = self.session.query(ShortId).filter_by(short_id=session_id).one_or_none()
            if not short_id:
                return None
            session_id = short_id.long_id
            short_id.timestamp = datetime.now()
            session = self.session.query(Session).filter_by(sid=session_id).one_or_none()
        else:
            session = self.session.query(Session).filter_by(sid=session_id).one_or_none()
            if not session:
                return None
            if session.short_id:
                session.short_id[0].timestamp = datetime.now()
        self.session.commit()
        return session
