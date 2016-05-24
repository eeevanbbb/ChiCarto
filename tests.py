import os
import json
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
            main.load_meta()
        self.db = main.db
        self.app = main.app.test_client()

    def tearDown(self):
        main.app.config['TESTING'] = False
        with main.app.test_request_context():
            self.db.session.remove()
            self.db.drop_all()

    def register(self, email, password):
        with main.app.test_request_context():
            rv = main.user_datastore.create_user(email=email, password=password)
            return rv

    def login(self, email, password):
        return self.app.post('/login', data=dict(
            email=email,
            password=password,
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout',follow_redirects=True)

class UserAuthTestCase(ChiCartoTestCase):
    # Test if we can register a user, login, and logout
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
            assert b'ChiCarto' in rv.data
            # Test incorrect password doesn't work
            rv = self.login("a@example.com", "passw")
            assert b'Remember Me' in rv.data
            print ("test_login_logout passed")

    # Test if a user can successfully delete their account
    def test_delete_account(self):
        with main.app.test_request_context():
            u = self.register('a@example.com', 'password')
            rv = self.login('a@example.com', 'password')
            assert b'You are logged in as' in rv.data
            rv = self.app.get('/delete-account')
            # Make sure we ask for confirmation
            assert b'Are you sure you want to delete' in rv.data
            rv = self.app.delete('/delete-account', follow_redirects=True)
            assert b'ChiCarto' in rv.data
            # Assert that the account is gone
            assert User.query.get(u.id) is None
            print ("test_delete_account passed")

class SearchTestCase(ChiCartoTestCase):
    # utility function to add a sample search
    def add_sample_search(self):
        uchicago_lat = 41.7886
        uchicago_long = -87.5987
        radius = 1000
        url = "https://data.cityofchicago.org/resource/6zsd-86xi.json"
        data_source1 = DataSource("Crimes 2001 - Present", url, [])
        filter1 = Filter("primary_type", "THEFT")

        data_search1 = DataSearch(data_source1, [])
        data_search2 = DataSearch(data_source1, [filter1])

        search = Search([data_search1, data_search2], uchicago_lat, uchicago_long, radius, "sample")

        main.db.session.add(search)
        main.db.session.flush()
        return search.id

    # Make sure that correctly constructed searches can retrieve the data
    # from their data sources
    def test_receive_search_data(self):
        with main.app.test_request_context():
            # Create objects
            uchicago_lat = 41.7886
            uchicago_long = -87.5987
            radius = 1000
            url1 = "https://data.cityofchicago.org/resource/6zsd-86xi.json"
            data_source1 = DataSource("Crimes 2001 - Present", url1, [])

            filter1 = Filter("primary_type", "THEFT")
            filter2 = Filter("description", "FROM BUILDING")

            data_search1 = DataSearch(data_source1, [])
            data_search2 = DataSearch(data_source1, [filter1])
            data_search3 = DataSearch(data_source1, [filter1, filter2])

            search1 = Search([data_search1], uchicago_lat, uchicago_long, radius, 'search1')
            search2 = Search([data_search2], uchicago_lat, uchicago_long, radius, 'search2')
            search3 = Search([data_search3], uchicago_lat, uchicago_long, radius, 'search3')
            search4 = Search([data_search1, data_search2], uchicago_lat, uchicago_long, radius, 'search3')

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
            print ("test_receive_search_data passed")

    # Test that we can add searches associated with a specific user
    # account
    def test_add_search_to_user(self):
        with main.app.test_request_context():
            # Create a search
            search = Search([],0,0,0,'name')
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
            print ("test_add_search_to_user passed")

    # Make sure that we can get a list of searches from the backend in
    # JSON
    def test_get_search(self):
        with main.app.test_request_context():
            # Add sample search, and attempt to get the JSON
            # representing it
            sid = self.add_sample_search()
            rv = self.app.get("/search/{0}".format(sid))
            d = json.loads(rv.data.decode("utf-8"))
            # Make sure the search data is still good, and
            # and only 1 search is returned
            assert len(d['searches']) == 1
            search = d['searches'][0]
            assert search['id'] == sid
            assert len(search['data_searches']) == 2
            print ("test_get_search passed")

    # Make sure that we can get a list of searches from the backend in
    # JSON
    def test_get_search2(self):
        with main.app.test_request_context():
            # Add sample search, and attempt to get the JSON
            # representing it
            sid = self.add_sample_search()
            sid2 = self.add_sample_search()
            rv = self.app.get("/search")
            d = json.loads(rv.data.decode("utf-8"))
            # Make sure the search data is still good, and
            # and only 1 search is returned
            assert len(d['searches']) == 2
            assert len(d['searches'][1]["data_searches"]) == 2
            print ("test_get_search2 passed")

    # Make sure that we can get the metadata about available data sources
    # to enable users to easily create valid searches
    def test_get_sources(self):
        with main.app.test_request_context():
            rv = self.app.get('/sources')
            d = json.loads(rv.data.decode('utf-8'))
            f = open('sources.json','r')
            canonical = json.load(f)
            f.close()
            sources = d['sources']
            assert len(sources) == len(canonical['sources'])
            assert sources[0]['name'] == 'Crimes 2001 - Present'
            assert len(sources[0]['filters_meta']) == 2
            assert sources[0]['filters_meta'][0]['type'] == 'string'
            print ("test_get_sources passed")

    # Test that you can successfully create a valid search
    # We have defined some samples, in JSON in the sources
    # directory
    def test_create_search_good(self):
        with main.app.test_request_context():
            # register and login a user, checking for success
            self.register('a@example.com', 'password')
            rv = self.login('a@example.com', 'password')
            rv = self.app.get('/me')
            assert (rv.status == '200 OK')
            with open('samples/search-valid.json','r') as f:
                # post a valid test search
                s = f.read()
                rv = self.app.post('/create_search', data=s,content_type='application/json')
                # if search was valid we'll get the results of that search
                # and check if it's good
                js = json.loads(rv.data.decode('utf-8'))
                sz = len(js['search-results'][0]['items'])
                assert sz > 0 and sz <= 10
                assert rv.status == '200 OK'
                print ('test_create_search_good passed')

    # Test that you can successfully create a valid search
    # We have defined some samples, in JSON in the sources
    # directory
    def test_create_search_good2(self):
        with main.app.test_request_context():
            # register and login user
            self.register('a@example.com', 'password')
            rv = self.login('a@example.com', 'password')
            rv = self.app.get('/me')
            assert (rv.status == '200 OK')
            with open('samples/search-valid2.json','r') as f:
                # post valid test search
                s = f.read()
                rv = self.app.post('/create_search', data=s,content_type='application/json')
                # make sure we get results back and they obey the search's params
                js = json.loads(rv.data.decode('utf-8'))
                sz = len(js['search-results'][0]['items'])
                assert sz > 0 and sz <= 10
                assert rv.status == '200 OK'
                print ('test_create_search_good2 passed')

    # Test that a malformed request to create a search fails properly
    def test_create_search_bad(self):
        with main.app.test_request_context():
            # register and login user
            self.register('a@example.com', 'password')
            rv = self.login('a@example.com', 'password')
            rv = self.app.get('/me')
            assert (rv.status == '200 OK')
            with open('samples/search-bad.json','r') as f:
                # post bad test search
                s = f.read()
                rv = self.app.post('/create_search', data=s,content_type='application/json')
                # make sure it was not accepted
                assert rv.status.startswith('422')
                print ('test_create_search_bad passed')

    # Test that a malformed request to create a search fails properly
    def test_create_search_bad2(self):
        with main.app.test_request_context():
            # register and login user
            self.register('a@example.com', 'password')
            rv = self.login('a@example.com', 'password')
            rv = self.app.get('/me')
            assert (rv.status == '200 OK')
            with open('samples/search-bad2.json','r') as f:
                # post bad search
                s = f.read()
                rv = self.app.post('/create_search', data=s,content_type='application/json')
                # assert that it was rejected
                assert rv.status.startswith('422')
                print ('test_create_search_bad2 passed')

    # Test that rating a search functions properly
    def test_rate_search_good(self):
        # make sure that you get the correct response when you give a valid search a valid rating
        with main.app.test_request_context():
            # register a user
            self.register('a@example.com', 'password')
            rv = self.login('a@example.com', 'password')
            rv = self.app.get('/me')
            # check that registration was successful
            assert (rv.status == '200 OK')
            with open('samples/search-valid.json','r') as f:
                s = f.read()
                # send a post message to server to create a search
                rv = self.app.post('/create_search', data=s,content_type='application/json')
                js = json.loads(rv.data.decode('utf-8'))
                sid = js['id']
                rating = 3
                data = {'id': sid, 'rating': rating}
                # send a post message to server to rate the search we just created
                rv = self.app.post('/rate_search', data=json.dumps(data), content_type='application/json')
                js = json.loads(rv.data.decode('utf-8'))['rating']
                # assert that we get the correct response - meaning that the rating was updated
                assert rating == js['val']
                assert rv.status == '200 OK'
                print ('test_rate_search_good passed')

    def test_rate_search_good2(self):
        # make sure that the rating stays with the search, until you change the rating,
        # and then make sure new rating is used
        with main.app.test_request_context():
            # register a user
            self.register('a@example.com', 'password')
            rv = self.login('a@example.com', 'password')
            rv = self.app.get('/me')
            # check that registration was successful
            assert (rv.status == '200 OK')
            with open('samples/search-valid.json','r') as f:
                s = f.read()
                # send a post message to server to create a search
                rv = self.app.post('/create_search', data=s,content_type='application/json')
                js = json.loads(rv.data.decode('utf-8'))
                sid = js['id']
                rating = 3
                data = json.dumps({'id': sid, 'rating': rating})
                # send a post message to server to rate the search we just created
                rv = self.app.post('/rate_search', data=data, content_type='application/json')
                js = json.loads(rv.data.decode('utf-8'))['rating']
                # assert that we get the correct response - meaning that the rating was updated
                assert rating == js['val']
                assert rv.status == '200 OK'

                rating = 5
                data = json.dumps({'id': sid, 'rating': rating})
                # send a post message to server to rate the search with a different rating
                rv = self.app.post('/rate_search', data=data, content_type='application/json')
                js = json.loads(rv.data.decode('utf-8'))['rating']
                # assert that we get the correct response - meaning that the rating was updated

                assert rating == js['val']
                assert rv.status == '200 OK'
                print ('test_rate_search_good2 passed')

    # Test that malformed or unauthorized requests to rate a search fail properly
    def test_rate_search_bad(self):
        # make sure error is returned if you try to rate a non-existent search
        with main.app.test_request_context():
            # register a user
            self.register('a@example.com', 'password')
            rv = self.login('a@example.com', 'password')
            rv = self.app.get('/me')
            # check that registration was successful
            assert (rv.status == '200 OK')
            with open('samples/search-valid.json','r') as f:
                s = f.read()
                # send a post message to server to create a search
                rv = self.app.post('/create_search', data=s,content_type='application/json')
                js = json.loads(rv.data.decode('utf-8'))
                sid = js['id']
                rating = 3
                # try to rate a search that doesn't exist
                data = {'id': sid+12345, 'rating': rating}
                rv = self.app.post('/rate_search', data=json.dumps(data), content_type='application/json')
                # assert that we get the correct response - meaning that the rating was ignored
                assert rv.status.startswith('422')
                print ('test_rate_search_bad passed')

    def test_rate_search_bad2(self):
        # make sure error is returned if you try to rate a search with an invalid rating (i.e. >5 or <0)
        with main.app.test_request_context():
            # register a user
            self.register('a@example.com', 'password')
            rv = self.login('a@example.com', 'password')
            rv = self.app.get('/me')
            # check that registration was successful
            assert (rv.status == '200 OK')
            with open('samples/search-valid.json','r') as f:
                s = f.read()
                # send a post message to server to create a search
                rv = self.app.post('/create_search', data=s,content_type='application/json')
                js = json.loads(rv.data.decode('utf-8'))
                sid = js['id']
                rating = 6
                # try to give an invalid rating for a search
                data = {'id': sid, 'rating': rating}
                rv = self.app.post('/rate_search', data=json.dumps(data), content_type='application/json')
                # assert that we get the correct response - meaning that the rating was ignored
                assert rv.status.startswith('422')
                print ('test_rate_search_bad2 passed')

if __name__ == '__main__':
    unittest.main()
