import os
import main
import unittest
import tempfile
from flask.ext.sqlalchemy import SQLAlchemy
from models import *
from views import *

class ChiCartoTestCase(unittest.TestCase):

    def setUp(self):
        main.app.config['TESTING'] = True
        main.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test_testing.db'
        main.app.config['WTF_CSRF_ENABLED'] = False
        main.db.init_app(main.app)
        with main.app.test_request_context():
            main.db.create_all()
        self.db = main.db
        self.app = main.app.test_client()
        
        print("SETUP")

    def tearDown(self):
        main.app.config['TESTING'] = False
        with main.app.test_request_context():
            self.db.session.remove()
            self.db.drop_all()
        
    def register(self, email, password):
        with main.app.test_request_context():
            rv = main.user_datastore.create_user(email=email, password=password)
    
    def login(self, email, password):
        return self.app.post('/login', data=dict(
            email=email,
            password=password,
        ), follow_redirects=True)
    
    def logout(self):
        return self.app.get('/logout',follow_redirects=True)
    
class UserAuthTestCase(ChiCartoTestCase):
    def test_login_logout(self):
        with main.app.test_request_context():
            # Test registration and Login
            rv = self.register("a@example.com", "password1")
            rv = self.login("a@example.com", "password1")
            assert b'You are logged in as' in rv.data
            rv = self.app.get('/me')
            assert b'You are logged in as' in rv.data
            # Should return to homepage
            rv = self.logout()
            assert b'Apparently' in rv.data
            # Test incorrect password doesn't work
            rv = self.login("a@example.com", "passw")
            assert b'Remember Me' in rv.data
        
if __name__ == '__main__':
    unittest.main()
