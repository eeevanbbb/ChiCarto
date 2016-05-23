from flask.ext.security import UserMixin, RoleMixin
from app import db
import requests
from sqlalchemy import DateTime
import json

COC_app_token = "k9JXTWBskVprntg9lMA3ahfoD"

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

user_searches = db.Table('user_searches',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('search_id', db.Integer(), db.ForeignKey('search.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    created_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    searches = db.relationship('Search', secondary=user_searches,
                                backref=db.backref('users', lazy='dynamic'))


    # Add a given search to the list of searches
    def add_search(self,search):
        self.searches.append(search)

    # Remove a given search from the list of searches
    # Return False if the search is not in this user's searches, True otherwise
    def remove_search(self,search):
        if search in self.searches:
            self.searches.remove(search)
            return True
        else:
            return False

#user_searches = db.Table('search_ratings',
#        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
#        db.Column('search_id', db.Integer(), db.ForeignKey('search.id')))

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    val = db.Column(db.Float())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    user = db.relationship('User', foreign_keys='Rating.user_id')

    def __init__(self, user, val):
        if val < 0 or val > 5:
            raise ValueError('rating must be between 0 and 5')
        self.user = user
        self.val = val

    def dictify(self):
        d = {
                'id': self.id,
                'user': self.user.id,
                'val': self.val
            }
        return d

search_data_searches = db.Table('search_data_searches',
        db.Column('search_id', db.Integer(), db.ForeignKey('search.id')),
        db.Column('data_search_id', db.Integer(), db.ForeignKey('data_search.id')))

search_ratings = db.Table('search_ratings',
                          db.Column('search_id', db.Integer(), db.ForeignKey('search.id')),
                          db.Column('rating_id', db.Integer(), db.ForeignKey('rating.id')))

class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_searches = db.relationship('DataSearch',secondary=search_data_searches,
                                    backref=db.backref('searches',lazy='dynamic'))
    latitude = db.Column(db.Float())
    longitude = db.Column(db.Float())
    radius = db.Column(db.Float())
    ratings = db.relationship('Rating',secondary=search_ratings,
                              backref=db.backref('searches',lazy='dynamic'))
    name = db.Column(db.String(255))

    def __init__(self,data_searches,latitude,longitude,radius,rating=None,name=None):
        self.data_searches = data_searches
        self.latitude = latitude
        self.longitude = longitude
        self.radius = radius
        self.rating = rating
        self.name = name

    def __repr__(self):
        name = "Search with data sources: "
        if self.name is not None:
            name = self.name + " - " + name
        for data_search in self.data_searches:
            name += data_search.data_source.name
            if len(data_search.filters) > 0:
                name += " ("
                for filter in data_search.filters:
                    name += filter.name
                    name += " = "
                    name += filter.value
                    if filter != data_search.filters[-1]:
                        name += ", "
                name += ")"
            if data_search != self.data_searches[-1]:
                name += ", "
        return name

    # Execute the search
    def execute(self):
        loc = self.latitude, self.longitude, self.radius
        requested_data = []
        return_status = 200
        for data_search in self.data_searches:
            (status, text) = data_search.make_request(loc)
            if (status != 200):
                return_status = status
                print('Error Loading Data from %s' % (data_search.data_source.name))

            data = {'id': data_search.data_source.id, 'status': status, 'items': json.loads(text)}
            requested_data.append(data)
            # requested_data[data_search.data_source.id] = data

        return (return_status, requested_data)

    # Add rating to this search
    def add_rating(self, rating):
        self.ratings.append(rating)

    # Remove a given rating from the list of ratings
    # Return False if the rating is not in this search's ratings, True otherwise
    def remove_rating(self,rating):
        if rating in self.ratings:
            self.ratings.remove(rating)
            return True
        else:
            return False

    def get_rating(self):
        r = 0
        if len(self.ratings) > 0:
            r = sum([rating.val for rating in self.ratings])/len(self.ratings)
        return r

    # dictify - Create dictionary representation for object
    def dictify(self):
        d = {
            "id": self.id,
            "data_searches": [ds.dictify() for ds in self.data_searches],
            "latitude": self.latitude,
            "longitude": self.longitude,
            "radius": self.radius,
            "rating": self.get_rating(),
            "name": self.name}
        return d

    #Return a string of comma-separated data source names, with filters
    def data_source_names(self):
        string = ""
        for data_search in self.data_searches:
            string += data_search.data_source.name
            if len(data_search.filters) > 0:
                string += " ("
                for filter in data_search.filters:
                    string += filter.name
                    string += " = "
                    string += filter.value
                    if filter != data_search.filters[-1]:
                        string += ", "
                string += ")"
            if data_search != self.data_searches[-1]:
                string += ", "
        return string

data_search_filters = db.Table('data_search_filters',
        db.Column('data_search_id', db.Integer(), db.ForeignKey('data_search.id')),
        db.Column('filter_id', db.Integer(), db.ForeignKey('filter.id')))


class DataSearch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_source_id = db.Column(db.Integer(), db.ForeignKey('data_source.id'))
    data_source = db.relationship('DataSource', foreign_keys='DataSearch.data_source_id')
    filters = db.relationship('Filter', secondary=data_search_filters,
                              backref=db.backref('data_searches', lazy='dynamic'))
    limit = db.Column(db.Integer())

    def __init__(self, data_source, filters, limit=None):
        self.data_source = data_source
        self.filters = filters
        self.limit = limit

    def __repr__(self):
        return "id: {}, data_source: {}, limit: {}, filters: {}".\
            format(repr(self.id), repr(self.data_source), self.limit, repr(self.filters))

    #Make a request for the URL with the applicable filters
    def make_request(self, loc=None):
        lat, lng, rad = loc
        full_url = self.data_source.url + '?'
        if (self.limit is not None):
            full_url += "&$limit={}".format(self.limit)
        if loc is not None:
            full_url += "&$where=within_circle(location,{},{},{})".format(lat, lng, rad)
        if len(self.filters) > 0:
            for a_filter in self.filters:
                full_url += "&"
                full_url += a_filter.name
                full_url += "="
                full_url += a_filter.value
        # print(full_url)
        request = requests.get(full_url, headers={'X-App-Token': COC_app_token})
        return (request.status_code, request.text)

    # dictify - Create dictionary representation for object
    def dictify(self):
        d = {
            "id": self.id,
            "data_source": self.data_source.dictify(),
            "limit": self.limit,
            "filters": [f.dictify() for f in self.filters]}
        return d


data_source_filters_meta = db.Table('data_source_filters_meta',
        db.Column('data_source_id', db.Integer(), db.ForeignKey('data_source.id')),
        db.Column('filter_meta_id', db.Integer(), db.ForeignKey('filter_meta.id')))


class DataSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    url = db.Column(db.String(255))
    title_key = db.Column(db.String(255))
    filters_meta = db.relationship('FilterMeta', secondary=data_source_filters_meta,
                                backref=db.backref('data_sources', lazy='dynamic'))

    def __init__(self,name,url,filters_meta,title_key=None):
        self.name = name
        self.url = url
        self.filters_meta = filters_meta
        self.title_key = title_key

    def __repr__(self):
        return self.name

    # dictify - Create dictionary representation for object
    def dictify(self):
        d = {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "title_key": self.title_key,
            "filters_meta": [fm.dictify() for fm in self.filters_meta]}
        return d


class Filter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    value = db.Column(db.String(255))

    def __init__(self,name,value="True"):
        self.name = name
        self.value = value

    def __repr__(self):
        return self.name + ": " + self.value

    # dictify - Create dictionary representation for object
    def dictify(self):
        d = {
            "id": self.id,
            "name": self.name,
            "value": self.value}
        return d


class FilterMeta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    type_ = db.Column(db.String(255))
    choose_from = db.Column(db.Text)

    def __init__(self,name,type_, choose_from=None):
        self.name = name
        self.type_ = type_
        self.choose_from = choose_from

    def __repr__(self):
        return "{{name: {}, type_: {}, choose_from: {}}}".format(self.name, self.type_, self.choose_from)

    # dictify - Create dictionary representation for object
    def dictify(self):
        d = {
            'id': self.id,
            'name': self.name,
            'type': self.type_}
        if self.choose_from is not None:
            d['choose_from'] = self.choose_from.split(',')
        return d
