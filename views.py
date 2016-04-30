from flask import Flask, request
from flask.ext.security import login_required
import flask.ext.login as flask_login

from app import db, app
from models import User

@app.route("/")
def hello():
    return "Hello World!"


@app.route("/me")
@login_required
def me():
    return 'You are logged in as \"{0}\"'.format(flask_login.current_user.email)
