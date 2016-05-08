from flask.ext.security import UserMixin, RoleMixin
from app import db
import requests
from sqlalchemy import DateTime

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


search_data_sources = db.Table('search_data_sources',
        db.Column('search_id', db.Integer(), db.ForeignKey('search.id')),
        db.Column('data_source_id', db.Integer(), db.ForeignKey('data_source.id')))

class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_sources = db.relationship('DataSource',secondary=search_data_sources,
                                    backref=db.backref('searches',lazy='dynamic'))
    latitude = db.Column(db.Float())
    longitude = db.Column(db.Float())
    radius = db.Column(db.Float())

    def __init__(self,data_sources,latitude,longitude,radius):
        self.data_sources = data_sources
        self.latitude = latitude
        self.longitude = longitude
        self.radius = radius

    def __repr__(self):
        name = "Search with data sources: "
        for data_source in self.data_sources:
            name += data_source.name
            if data_source != self.data_sources[-1]:
                name += ", "
        return name

    # Execute the search
    def execute(self):
        loc = self.latitude,self.longitude,self.radius
        for data_source in self.data_sources:
            (status,text) = data_source.make_request(loc)
            #TODO: Do something with this information
            return (status,text) #FIXME: Temporary

data_source_filters = db.Table('data_source_filters',
        db.Column('data_source_id', db.Integer(), db.ForeignKey('data_source.id')),
        db.Column('filter_id', db.Integer(), db.ForeignKey('filter.id')))

data_source_filters_meta = db.Table('data_source_filters_meta',
        db.Column('data_source_id', db.Integer(), db.ForeignKey('data_source.id')),
        db.Column('filter_meta_id', db.Integer(), db.ForeignKey('filter_meta.id')))

class DataSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    url = db.Column(db.String(255))
    title_key = db.Column(db.String(255))
    limit = db.Column(db.Integer)
    filters_meta = db.relationship('FilterMeta', secondary=data_source_filters_meta,
                                backref=db.backref('data_sources', lazy='dynamic'))
    filters = db.relationship('Filter', secondary=data_source_filters,
                                backref=db.backref('data_sources', lazy='dynamic'))

    def __init__(self,name,url,filters,filters_meta,title_key=None, limit=10):
        self.name = name
        self.url = url
        self.filters = filters
        self.filters_meta = filters_meta
        self.title_key = title_key
        self.limit = limit

    def __repr__(self):
        return self.name

    #Make a request for the URL with the applicable filters
    def make_request(self, loc=None):
        lat, lng, rad = loc
        full_url = self.url
        full_url += "?$limit={}".format(self.limit)
        if loc is not None:
          full_url += "&$where=within_circle(location,{},{},{})".format(lat, lng, rad)
        if len(self.filters) > 0:
            full_url += "&"
            for a_filter in self.filters:
                full_url += a_filter.name
                full_url += "="
                full_url += a_filter.value
                #if a_filter != self.filters[-1]:
                    #full_url += "&"            
        print(full_url)
        request = requests.get(full_url, headers={'X-App-Token':COC_app_token})
        return (request.status_code,request.text)

class Filter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    value = db.Column(db.String(255))

    def __init__(self,name,value="True"):
        self.name = name
        self.value = value

    def __repr__(self):
        return self.name + ": " + self.value

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
