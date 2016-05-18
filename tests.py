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

    def test_delete_account(self):
        with main.app.test_request_context():
            u = self.register('a@example.com', 'password')
            rv = self.login('a@example.com', 'password')
            assert b'You are logged in as' in rv.data
            rv = self.app.get('/delete-account')
            assert b'Are you sure you want to delete' in rv.data
            rv = self.app.delete('/delete-account', follow_redirects=True)
            assert b'ChiCarto' in rv.data
            assert User.query.get(u.id) is None

class SearchTestCase(ChiCartoTestCase):
    def add_sample_search(self):
        uchicago_lat = 41.7886
        uchicago_long = -87.5987
        radius = 1000
        url = "https://data.cityofchicago.org/resource/6zsd-86xi.json"
        data_source1 = DataSource("Crimes 2001 - Present", url, [])
        filter1 = Filter("primary_type", "THEFT")

        data_search1 = DataSearch(data_source1, [])
        data_search2 = DataSearch(data_source1, [filter1])

        search = Search([data_search1, data_search2], uchicago_lat, uchicago_long, radius)

        main.db.session.add(search)
        main.db.session.flush()
        return search.id

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

            search1 = Search([data_search1], uchicago_lat, uchicago_long, radius)
            search2 = Search([data_search2], uchicago_lat, uchicago_long, radius)
            search3 = Search([data_search3], uchicago_lat, uchicago_long, radius)
            search4 = Search([data_search1, data_search2], uchicago_lat, uchicago_long, radius)

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

    def test_get_search(self):
        with main.app.test_request_context():
            sid = self.add_sample_search()
            rv = self.app.get("/search/{0}".format(sid))
            d = json.loads(rv.data.decode("utf-8"))
            assert len(d['searches']) == 1
            search = d['searches'][0]
            assert search['id'] == sid
            assert len(search['data_searches']) == 2

    def test_get_search2(self):
        with main.app.test_request_context():
            sid = self.add_sample_search()
            sid2 = self.add_sample_search()
            rv = self.app.get("/search")
            d = json.loads(rv.data.decode("utf-8"))
            assert len(d['searches']) == 2
            assert len(d['searches'][1]["data_searches"]) == 2

    def test_get_sources(self):
        with main.app.test_request_context():
            rv = self.app.get('/sources')
            d = json.loads(rv.data.decode('utf-8'))
            sources = d['sources']
            assert len(sources) == 2
            assert sources[0]['name'] == 'Crimes 2001 - Present'
            assert len(sources[0]['filters_meta']) == 2
            assert sources[0]['filters_meta'][0]['type'] == 'string'

    def test_create_search_good(self):
        with main.app.test_request_context():
            # register and login a user, checking for success
            self.register('a@example.com', 'password')
            rv = self.login('a@example.com', 'password')
            rv = self.app.get('/me')
            assert (rv.status == '200 OK')
            with open('samples/source-valid.json','r') as f:
                # post a valid test search
                s = f.read()
                rv = self.app.post('/create_search', data=s,content_type='application/json')
                # if search was valid we'll get the results of that search
                # and check if it's good
                js = json.loads(rv.data.decode('utf-8'))
                sz = len(js['search-results'][0]['items'])
                assert sz > 0 and sz <= 10
                assert rv.status == '200 OK'

    def test_create_search_good2(self):
        with main.app.test_request_context():
            # register and login user
            self.register('a@example.com', 'password')
            rv = self.login('a@example.com', 'password')
            rv = self.app.get('/me')
            assert (rv.status == '200 OK')
            with open('samples/source-valid2.json','r') as f:
                # post valid test search
                s = f.read()
                rv = self.app.post('/create_search', data=s,content_type='application/json')
                # make sure we get results back and they obey the search's params
                js = json.loads(rv.data.decode('utf-8'))
                sz = len(js['search-results'][0]['items'])
                assert sz > 0 and sz <= 10
                assert rv.status == '200 OK'

    def test_create_search_bad(self):
        with main.app.test_request_context():
            # register and login user
            self.register('a@example.com', 'password')
            rv = self.login('a@example.com', 'password')
            rv = self.app.get('/me')
            assert (rv.status == '200 OK')
            with open('samples/source-bad.json','r') as f:
                # post bad test search
                s = f.read()
                rv = self.app.post('/create_search', data=s,content_type='application/json')
                # make sure it was not accepted
                assert rv.status.startswith('422')

    def test_create_search_bad2(self):
        with main.app.test_request_context():
            # register and login user
            self.register('a@example.com', 'password')
            rv = self.login('a@example.com', 'password')
            rv = self.app.get('/me')
            assert (rv.status == '200 OK')
            with open('samples/source-bad2.json','r') as f:
                # post bad search
                s = f.read()
                rv = self.app.post('/create_search', data=s,content_type='application/json')
                # assert that it was rejected
                assert rv.status.startswith('422')

    def test_rate_search_good(self):
        # make sure that you get the correct response when you give a valid search a valid rating
        with main.app.test_request_context():
            # register a user
            self.register('a@example.com', 'password')
            rv = self.login('a@example.com', 'password')
            rv = self.app.get('/me')
            # check that registration was successful
            assert (rv.status == '200 OK')
            with open('samples/source-valid.json','r') as f:
                s = f.read()
                # send a post message to server to create a search
                rv = self.app.post('/create_search', data=s,content_type='application/json')
                js = json.loads(rv.data.decode('utf-8'))
                sid = js['id']
                rating = 3
                data = {'id': sid, 'rating': rating}
                # send a post message to server to rate the search we just created
                rv = self.app.post('/rate_search', data=json.dumps(data), content_type='application/json')
                js = json.loads(rv.data.decode('utf-8'))['searches'][0]
                # assert that we get the correct response - meaning that the rating was updated
                assert sid == js['id']
                assert rating == js['rating']
                assert rv.status == '200 OK'

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
            with open('samples/source-valid.json','r') as f:
                s = f.read()
                # send a post message to server to create a search
                rv = self.app.post('/create_search', data=s,content_type='application/json')
                js = json.loads(rv.data.decode('utf-8'))
                sid = js['id']
                rating = 3
                data = {'id': sid, 'rating': rating}
                # send a post message to server to rate the search we just created
                rv = self.app.post('/rate_search', data=json.dumps(data), content_type='application/json')

                # get data for the search to verify that the rating was actually saved in database
                rv = self.app.get('/search/' + str(sid))
                js = json.loads(rv.data.decode('utf-8'))['searches'][0]
                # assert that we get the correct response - meaning that the rating was updated
                assert sid == js['id']
                assert rating == js['rating']
                assert rv.status == '200 OK'

                rating = 5
                data = {'id': sid, 'rating': rating}
                # send a post message to server to rate the search with a different rating
                rv = self.app.post('/rate_search', data=json.dumps(data), content_type='application/json')

                # get data for the search to verify that the rating was actually saved in database
                rv = self.app.get('/search/' + str(sid))
                js = json.loads(rv.data.decode('utf-8'))['searches'][0]
                # assert that we get the correct response - meaning that the rating was updated

                assert sid == js['id']
                assert rating == js['rating']
                assert rv.status == '200 OK'

    def test_rate_search_bad(self):
        # make sure error is returned if you try to rate a non-existent search
        with main.app.test_request_context():
            # register a user
            self.register('a@example.com', 'password')
            rv = self.login('a@example.com', 'password')
            rv = self.app.get('/me')
            # check that registration was successful
            assert (rv.status == '200 OK')
            with open('samples/source-valid.json','r') as f:
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

    def test_rate_search_bad2(self):
        # make sure error is returned if you try to rate a search with an invalid rating (i.e. >5 or <0)
        with main.app.test_request_context():
            # register a user
            self.register('a@example.com', 'password')
            rv = self.login('a@example.com', 'password')
            rv = self.app.get('/me')
            # check that registration was successful
            assert (rv.status == '200 OK')
            with open('samples/source-valid.json','r') as f:
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


if __name__ == '__main__':
    unittest.main()
