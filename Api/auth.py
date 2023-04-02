import json
import random
import string
from datetime import datetime
from functools import wraps

from flask import request

from crud.user import UserCrud
from db import get_session


def generate_token():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with get_session() as session:
            user = UserCrud(session).get_user_by_filters(id=request.headers.get("Uid"))
            if user and user.token == request.headers.get("Token"):
                if user.exp_token.timestamp() > datetime.now().timestamp():
                    return func(session, *args, **kwargs)
                else:
                    data = request.data
                    return json.dumps({"err_code": 1, "body": ""}), 401, {"Content-Type": "application/json"}
            else:
                data = request.data
                return json.dumps({"err_code": 1, "body": ""}), 401, {"Content-Type": "application/json"}
    return wrapper
