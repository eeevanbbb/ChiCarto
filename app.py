from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

# DO NOT DO THIS IN PRODUCTION
app.secret_key = 'e6855dcf9df593bd7d53209a95d44dd9'

# Enable user registration
app.config['SECURITY_REGISTERABLE'] = True
# Disable sending emails
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
# Redirect logged in/registered users to the '/me' page
app.config['SECURITY_POST_LOGIN_VIEW'] = '/me'
app.config['SECURITY_POST_REGISTER_VIEW'] = '/me'
# Turn off annoying warning that slows testing
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =  False
