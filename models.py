from flask.ext.security import UserMixin, RoleMixin
from app import db
import requests

COC_app_token = "k9JXTWBskVprntg9lMA3ahfoD"

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

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

    def execute(self):
        for data_source in self.data_sources:
            (status,text) = data_source.make_request() #TODO: Pass in the location parameters
            #TODO: Do something with this information
            return (status,text) #FIXME: Temporary

data_source_filters = db.Table('data_source_filters',
        db.Column('data_source_id', db.Integer(), db.ForeignKey('data_source.id')),
        db.Column('filter_id', db.Integer(), db.ForeignKey('filter.id')))

class DataSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    url = db.Column(db.String(255))
    filters = db.relationship('Filter', secondary=data_source_filters,
                                backref=db.backref('data_sources', lazy='dynamic'))

    def __init__(self,name,url,filters):
        self.name = name
        self.url = url
        self.filters = filters

    def __repr__(self):
        return self.name

    #Make a request for the URL with the applicable filters
    def make_request(self):
        full_url = self.url
        if len(self.filters) > 0:
            full_url += "?"
            for a_filter in self.filters:
                full_url += a_filter.name
                full_url += "="
                full_url += a_filter.value
                if a_filter != self.filters[-1]:
                    full_url += "&"
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
