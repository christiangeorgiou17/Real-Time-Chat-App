from os import getenv

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

load_dotenv()
app.config["JWT_SECRET_KEY"] = getenv("JWT_SECRET_KEY")

jwt = JWTManager(app)


