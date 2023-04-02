import random
import string

from flask import Flask, request, render_template
import json
from datetime import datetime, timedelta
import sqlalchemy

from auth import auth, generate_token
from crud.session import SessionCrud
from crud.user import UserCrud
from db import get_session
from models.change import Change
from models.session import Session
from models.short_id import ShortId
from models.user_to_session import UserToSession
import os


app = Flask(__name__)
os.environ['PYTHONHASHSEED'] = '0'


def generate_sid():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))


def make_response(data, code):
    return json.dumps(data), code, {"Content-Type": "application/json"}


@app.route("/updateToken", methods=["GET"])
def update_token():
    with get_session() as session:
        user_crud = UserCrud(session)
        user = user_crud.get_user_by_filters(id=request.headers.get("Uid"))
        if user and user.refresh_token == request.headers.get("RefreshToken"):
            if user.exp_refresh.timestamp() > datetime.now().timestamp():
                user.token = generate_token()
                user.exp_token = datetime.now() + timedelta(minutes=15)
                user.exp_refresh = datetime.now() + timedelta(minutes=120)
                session.commit()
                return make_response({"err_code": 0, "token": user.token}, 200)
        return make_response({"err_code": 1, "token": ""}, 401)


@app.route("/", methods=["GET"])
def starting_page():
    return render_template("index.html")


@app.route("/login", methods=["GET"])
def login_page():
    return make_response({"body": render_template("starting.html")}, 200)


@app.route("/login", methods=["POST"])
def login():
    data = json.loads(request.data)
    with get_session() as session:
        user_crud = UserCrud(session)
        user = user_crud.get_user_by_filters(login=data["login"])
        if user is None:
            return make_response({"err_code": 1, "text": "Invalid login"}, 401)
        if hash(data["password"] + salt) != user.password:
            return make_response({"err_code": 1, "text": "Invalid password"}, 401)
        timenow = datetime.now()
        user.token = generate_token()
        user.exp_token = timenow + timedelta(minutes=15)
        user.refresh_token = generate_token()
        user.exp_refresh = timenow + timedelta(minutes=120)
        session.commit()
        return make_response(
            {"err_code": 0, "token": user.token, "refresh_token": user.refresh_token, "id": user.id}, 200
        )


@app.route("/signup", methods=["GET"])
def get_sign_up_page():
    return json.dumps({"body": render_template("signup.html")}), 200, {"Content-Type": "application/json"}


@app.route("/signup", methods=["POST"])
def sign_up():
    req = json.loads(request.data)
    with get_session() as session:
        user_crud = UserCrud(session)
        user_crud.create_user(login=req["login"], password=hash(req["password"] + os.getenv("SALT")))
        return make_response({"err_code": 0}, 200)


@app.route("/sessions", methods=["GET"])
@auth
def sessions_choice(session):
    session_crud = SessionCrud(session)
    sessions = session_crud.get_sessions_by_user_id(request.headers.get("Uid"))
    return make_response({
        "err_code": 0,
        "body": render_template("sessions.html", available_sessions=[{"name": s.name, "id": s.sid} for s in sessions])
    }, 200)


@app.route("/sessions", methods=["POST"])
@auth
def session_add(session):
    data = json.loads(request.data)
    user_crud = UserCrud(session)
    user = user_crud.get_user_by_filters(id=int(request.headers.get("Uid")))
    session_ = Session(name=data["name"], sid=generate_sid(), text="")
    user.sessions.append(session_)
    session.commit()
    return make_response({"err_code": 0, "session_id": session_.sid}, 200)


@app.route("/sessions/<session_id>")
@auth
def enter_session(session, session_id):
    session_crud = SessionCrud(session)
    user_crud = UserCrud(session)
    sess = session_crud.get_session_by_id(session_id)
    if not sess:
        return make_response({"err_code": 2, "text": "Not Found"}, 404)
    if not (user := user_crud.get_user_by_filters(id=request.headers.get("Uid"))):
        return make_response({"err_code": 2, "text": "Not Found"}, 404)
    sid = sess.id
    session_with_cursor = session.query(UserToSession).filter_by(user_id=int(request.headers.get("Uid"))).filter_by(session_id=sess.id).one_or_none()
    if session_with_cursor is None:
        user.sessions.append(sess)
        session_with_cursor = session.query(UserToSession).filter_by(user_id=request.headers.get("Uid")).filter_by(session_id=sess.id).one_or_none()
        session_with_cursor.owner = False
        session.commit()
    port = 8080
    if request.headers.get("RO") == "true":
        port = 8081
    resp = {
            "err_code": 0,
            "body": render_template(
                "session.html",
                id=session_id,
                cursor_x=session_with_cursor.cursor_x,
                cursor_y=session_with_cursor.cursor_y
            ),
            "cursor_x": session_with_cursor.cursor_x,
            "cursor_y": session_with_cursor.cursor_y,
            "text": sess.text,
            "sid": sid,
            "port": port
    }
    return make_response(resp, 200)


@app.route("/sessions/<session_id>/shortid")
@auth
def shorten_id(session, session_id):
    short_id = session.query(ShortId).filter_by(long_id=session_id).one_or_none()
    if not short_id:
        # Ищем свободный short_id (у которого в поле long_id - NULL или к которому не обращались более 7 дней)
        # затем закрепляем за ним наш айдишник, если а парлелльной транзакции это же сделалось быстрее
        # и этот short_id уже заняли - откатываем транзакцию
        while True:
            try:
                short_id = session.query(ShortId).filter_by(long_id=None).first()
                if short_id is None:
                    short_id = session.query(ShortId).filter(ShortId.timestamp < datetime.now() - timedelta(days=7)).first()
                short_id.long_id = session_id
                short_id.timestamp = datetime.now()
                session.commit()
                break
            except sqlalchemy.exc.OperationalError:
                session.rollback()
    else:
        short_id.timestamp = datetime.now()
    return make_response({"err_code": 0, "short_id": short_id.short_id}, 200)


@app.route("/sessions/<session_id>/replay", methods=["GET"])
@auth
def replay_session(session, session_id):
    flag = False
    if len(session_id) == 5:
        sh = session.query(ShortId).filter_by(short_id=session_id).one_or_none()
        if sh is None:
            return json.dumps({"err_code": 2, "text": "Not Found"}), 404, {"Content-Type": "application/json"}
        session_id = sh.long_id
        sh.timestamp = datetime.now()
        flag = True
    session_ = session.query(Session).filter_by(sid=session_id).one_or_none()
    if session_ is None:
        return json.dumps({"err_code": 2, "text": "Not Found"}), 404, {"Content-Type": "application/json"}
    if flag and session_.short_id:
        session_.short_id[0].timestamp = datetime.now()
    return make_response({"err_code": 0, "body": render_template("session_replay.html", id=session_id)}, 200)


@app.route("/sessions/<session_id>/replay/<step>", methods=["GET"])
@auth
def replay_session_step(session, session_id, step):
    session_ = session.query(Session).filter_by(sid=session_id).one_or_none()
    if session_ is None:
        return json.dumps({"err_code": 2, "text": "Not Found"}), 404, {"Content-Type": "application/json"}
    changes = session.query(Change).filter_by(sid=session_.id).all()
    if int(step) >= len(changes):
        return json.dumps({"err_code": 3, "text": "Not Found"}), 404, {"Content-Type": "application/json"}
    return make_response({"err_code": 0, "delta": changes[int(step)].delta}, 200)


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
