import json

import flask
from flask import Flask, request, render_template
from flask.ext.security import login_required
import flask.ext.login as flask_login
from flask import abort

from app import db, app
from models import *

@app.route("/")
def hello():
    return render_template('index.html')


@app.route("/me")
@login_required
def me():
    return render_template('user.html',user=flask_login.current_user)

@app.route("/search", defaults = {"sid": None})
@app.route("/search/<sid>")
def search(sid =  None):
    if sid is not None:
        s = Search.query.get(int(sid))
        if s is not None:
            d = dictify_search(s)
            return flask.jsonify(**d)
        else:
            abort(404)
    else:
        s = Search.query.all()
        searches = [dictify_search(search) for search in s]
        json_dict = {'searches': searches }
        return flask.jsonify(**json_dict)

@app.route("/search-results/<sid>")
def search_results(sid):
    s = Search.query.get(int(sid))
    if s is not None:
        (status,json_text) = s.execute()
        results = json.loads(json_text)
        json_dict = {'search-results': results}
        return flask.jsonify(**json_dict)
    else:
        abort(404)

def dictify_search(s):
    d = {"id": s.id,
        "data_sources": [{"id":source.id, "name":source.name}
                        for source in s.data_sources],
        "latitude": s.latitude,
        "longitude": s.longitude,
        "radius": s.radius
    }
    return d
