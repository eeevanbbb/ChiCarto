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

class SearchTestCase(ChiCartoTestCase):
    def test_receive_search_data(self):
        with main.app.test_request_context():
            # Create objects
            uchicago_lat = 41.7886
            uchicago_long = 87.5987
            radius = 1000
            url1 = "https://data.cityofchicago.org/resource/energy-usage-2010.json"
            data_source1 = DataSource("Energy Usage 2010",url1,[])
            search1 = Search([data_source1],uchicago_lat,uchicago_long,radius)
            filter1 = Filter("building_type","Residential")
            data_source2 = DataSource("Energy Usage 2010",url1,[filter1])
            search2 = Search([data_source2],uchicago_lat,uchicago_long,radius)
            filter2 = Filter("community_area_name","Woodlawn")
            data_source3 = DataSource("Energy Usage 2010",url1,[filter1,filter2])
            search3 = Search([data_source3],uchicago_lat,uchicago_long,radius)
            search4 = Search([data_source1,data_source2],uchicago_lat,uchicago_long,radius)

            # Execute the searches
            (status1,text1) = search1.execute() #search w/ no filters
            (status2,text2) = search2.execute() #search w/ one filter
            (status3,text3) = search3.execute() #search w/ two filters
            (status4,text4) = search4.execute() #search w/ two datasources
            # Make sure the requests were successful
            assert status1 == 200
            assert status2 == 200
            assert status3 == 200
            assert status4 == 200

    def test_add_search_to_user(self):
        with main.app.test_request_context():
            # Create a search
            search = Search([],0,0,0)
            # Create a user
            user = main.user_datastore.create_user(email="b@example.com", password="password2")

            # Add the search to the user
            user.add_search(search)
            # Make sure the search was added
            assert len(user.searches) == 1

            # Remove the search from the user
            success = user.remove_search(search)
            # Make sure the search was removed
            assert success == True
            assert len(user.searches) == 0

            # Try to remove a non-existent search
            success = user.remove_search(search)
            # Make sure this results in failure
            assert success == False

if __name__ == '__main__':
    unittest.main()
