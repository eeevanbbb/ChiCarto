from flask import Flask
from database import db_session
from models import User

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()



# Manage users in the database

# Create a new user and add it to the database.
# If the username already exists, return False
# If the operation is successful, return True
def create_user(username,password):
	if username_exists(username):
		return False
	else:
		new_user = User(username,password)
		db_session.add(new_user)
		db_session.commit()
		return True

# Return a list of all users in the databse
def get_all_users():
	return User.query.all()

# Return whether or not the username exists in the database
def username_exists(username):
	return User.query.filter(User.username == username).count() > 0

# Delete the user with the given username from the database
# If the username does not exist, return False
# If the operation is successfull, return True
def delete_user_with_username(username):
	if username_exists(username):
		User.query.filter(User.username == username).delete()
		return True
	else:
		return False




# Run the app
if __name__ == "__main__":
    app.run()