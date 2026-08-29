from datetime import timedelta, datetime, timezone
from os import getenv
from os.path import abspath, join, dirname

from dotenv import load_dotenv
from flask import Flask, request, jsonify, url_for, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt, decode_token
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

load_dotenv()

# Only for local database & testing

BASE_DIR = abspath(dirname(__file__))
DB_PATH = join(dirname(BASE_DIR), "chat.db")


JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = JWT_ACCESS_TOKEN_EXPIRES


db = SQLAlchemy(app)
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")



@app.route("/")
def index():
    return render_template("index.html")








LAST_CLEANUP_TIME = None

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class TokenBlockList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class ChatRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_group = db.Column(db.Boolean, default=False, nullable=False)
    name = db.Column(db.String(100), nullable=True)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    # User shortcut
    user = db.relationship("User", backref=db.backref("messages", lazy=True))

    room_id = db.Column(db.Integer, db.ForeignKey("chat_room.id"), nullable=False)
    # Room shortcut
    room = db.relationship("ChatRoom", backref=db.backref("messages", lazy=True))









def cleanup_expired_tokens():
    global JWT_ACCESS_TOKEN_EXPIRES

    cutoff_time = datetime.now(timezone.utc) - JWT_ACCESS_TOKEN_EXPIRES

    try:

        deleted_count = db.session.query(TokenBlockList).filter(
            TokenBlockList.created_at < cutoff_time
        ).delete()

        db.session.commit()
        if deleted_count > 0:
            print(f"DATABASE CLEANUP: Removed {deleted_count} expired tokens.")

    except Exception as e:
        db.session.rollback()
        print(f"DATABASE CLEANUP: Failed - {e}")



# API endpoints


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username and not password:
        return jsonify({"msg": "Missing username and password"}), 400
    if not username:
        return jsonify({"msg": "Missing username"}), 400
    if not password:
        return jsonify({"msg": "Missing password"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 400

    new_user = User(username=username)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully"}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username and not password:
        return jsonify({"msg": "Missing username and password"}), 400
    if not username:
        return jsonify({"msg": "Missing username"}), 400
    if not password:
        return jsonify({"msg": "Missing password"}), 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"msg": "User does not exist"}), 401
    elif not user.check_password(password):
        return jsonify({"msg": "Password Incorrect"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": access_token}), 200


@jwt.token_in_blocklist_loader
def check_if_token_revoked(_jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = TokenBlockList.query.filter_by(jti=jti).first()
    return token is not None

@app.route("/api/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]

    revoked_token = TokenBlockList(jti=jti)
    db.session.add(revoked_token)
    db.session.commit()

    return jsonify({"msg": "Access token revoked successfully. Logged out."}), 200


@app.before_request
def auto_prune_blocklist():
    global LAST_CLEANUP_TIME
    now = datetime.now(timezone.utc)

    if LAST_CLEANUP_TIME is None or (now - LAST_CLEANUP_TIME) > timedelta(days=1):
        cleanup_expired_tokens()
        LAST_CLEANUP_TIME = now


# Websocket Event Handlers

@socketio.on("connect")
def handle_connect(auth):

    if auth:
        token = auth.get("token")
    else:
        print("Connection refused: No token provided")
        return False


    try:
        decoded_token = decode_token(token)
        user_id = decoded_token["sub"]

        join_room(f"user_{user_id}")
        print(f"User {user_id} connected successfully and joined room user_{user_id}")

    except Exception as e:
        print(f"Connection refused: Invalid token. Error: {e}")
        return False





def main():
    socketio.run(app, debug=True)
if __name__ == "__main__":
    main()