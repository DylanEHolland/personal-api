from linkedin import linkedin
from datetime import datetime
from random import randint
from slugify import slugify
import os
from cloudinary.uploader import upload
import base64
from uuid import uuid4

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, \
    JWTManager, jwt_required, jwt_refresh_token_required

app = Flask(__name__)
jwt = JWTManager(app)
cors = CORS(app, resources={r'*': {'origins': '*'}})
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from backend import routes