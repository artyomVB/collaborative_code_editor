from models.user import User


class UserCrud:
    def __init__(self, session):
        self.session = session

    def get_user_by_filters(self, **kwargs):
        return self.session.query(User).filter_by(**kwargs).one_or_none()

    def create_user(self, **kwargs):
        with self.session.begin():
            user = User(**kwargs)
            self.session.add(user)
