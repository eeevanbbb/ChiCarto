from flask import Flask
from flask.ext.security import Security, SQLAlchemyUserDatastore

from app import app, db
from models import *
from views import *

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Run the app
if __name__ == "__main__":
    db.init_app(app)
    try:
        open('/tmp/test.db')
    except IOError:
        db.create_all() 
    app.run(debug=True)
