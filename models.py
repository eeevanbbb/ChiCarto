from flask.ext.security import UserMixin, RoleMixin
from app import db

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

data_source_filters = db.Table('data_source_filters',
        db.Column('data_source_id', db.Integer(), db.ForeignKey('data_source.id')),
        db.Column('filter_id', db.Integer(), db.ForeignKey('filter.id')))

class DataSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    url = db.Column(db.String(255))
    filters = db.relationship('Filter', secondary=data_source_filters,
                                backref=db.backref('data_sources', lazy='dynamic'))

class Filter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
