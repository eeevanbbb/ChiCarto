import json

import flask
from flask import Flask, request, render_template, abort,\
    redirect, url_for
from flask.ext.security import login_required
from flask_security.utils import logout_user
import flask.ext.login as flask_login

from app import db, app
from models import *

@app.route("/")
def hello():
    loggedIn = False
    if flask_login.current_user.is_authenticated:
        loggedIn = True
    return render_template('index.html',loggedIn=loggedIn)


@app.route("/me")
@login_required
def me():
    user = flask_login.current_user
    rated = set()
    for search in user.searches:
        for rating in search.ratings:
            if rating.user_id == user.id:
                rated.add(search.id)
                break
    return render_template('user.html',user=user, rated=rated)


# Look at file 'sample_json_search_request.json' to see sample json data in post request this function accepts
# Though it wouldn't be difficult to change the format of the json data if needed to interact with the front-end
@app.route('/create_search', methods=['GET','POST'])
@login_required
def create_search():
    if request.method == "POST":
        try:
            data = request.get_json(force=True)

            lat = data['latitude']
            lon = data['longitude']
            radius = data['radius']
            sources = data['sources']
            name = data['name']

            data_searches = []

            for source in sources:
                source_id = source['id']
                data_source = db.session.query(DataSource).filter(DataSource.id == source_id).one()
                limit = source['limit']
                filters_dict = source['filters']
                filters = []

                for filter_temp in filters_dict:
                    # Check to see if this filter value is valid for this filter and DataSource
                    new_filter = Filter(filter_temp['name'], filter_temp['value'])
                    filters.append(new_filter)

                data_search = DataSearch(data_source, filters, limit)
                db.session.add(data_search)
                data_searches.append(data_search)

            search = Search(data_searches, lat, lon, radius, name)
            db.session.add(search)

            flask_login.current_user.add_search(search)

            db.session.commit()

            # return search_results(search.id)
            json_dict = {"id": search.id}
            return flask.jsonify(**json_dict) #Save time not fetching results

        except (Exception) as e:
            #print("Exception: ")
            #print(e)
            abort (422)
    elif request.method == "GET":
        return render_template('create.html')


@app.route('/rate_search', methods=['POST'])
@login_required
def rate_search():
        try:
            # FIXME: Verify user has yet to rate the entry
            # Using back button on front-end gets around front-end validation
            data = request.get_json(force=True) #request.form
            sid = data['id']
            s = Search.query.get(int(sid))
            user = flask_login.current_user
            if s is not None:
                rate_val = float(data['rating'])
                rating = Rating(user, rate_val)
                db.session.add(rating)
                json_dict = {'rating': rating.dictify() }
                s.add_rating(rating)
                db.session.commit()
                return flask.jsonify(**json_dict)
            else:
                abort(404)
        except (Exception) as e:
            print("EXCEPTION: "+str(e))
            abort(422)

@app.route('/ratings/<sid>', methods=['GET'])
def ratings(sid):
    s = Search.query.get(int(sid))
    if s is None:
      abort(404)
    ratings = s.ratings
    js_dict = {'ratings': [r.dictify() for r in ratings]}
    return flask.jsonify(**js_dict)

@app.route("/search", defaults = {"sid": None})
@app.route("/search/<sid>")
def search(sid =  None):
    if sid is not None:
        s = Search.query.get(int(sid))
        if s is not None:
            d = s.dictify()
            json_dict = {'searches': [d]}
            return flask.jsonify(**json_dict)
        else:
            abort(404)
    else:
        s = Search.query.all()
        searches = [search.dictify() for search in s]
        # print(searches)
        json_dict = {'searches': searches}
        return flask.jsonify(**json_dict)


@app.route("/search-results/<sid>")
def search_results(sid):
    s = Search.query.get(int(sid))
    if s is not None:
        (status, results) = s.execute()
        json_dict = {'search-results': results, 'id': sid, 'name': s.name}
        return flask.jsonify(**json_dict)
    else:
        abort(404)

@app.route('/sources')
def sources():
    ss = DataSource.query.all()
    sources = [s.dictify() for s in ss]
    json_dict = {'sources': sources}
    return flask.jsonify(**json_dict)

@app.route('/delete-account', methods=['GET','DELETE'])
@login_required
def delete_account():
    user = flask_login.current_user
    if request.method == 'GET':
        return render_template('delete-account.html',
                               user=user)
    else:
        dbu = User.query.get(user.id)
        logout_user()
        db.session.delete(dbu)
        db.session.commit()
        return redirect('/', code=303)

@app.route('/searches')
def searches():
    searches = Search.query.all()
    # searches = [s.dictify() for s in query]
    return render_template('searches.html',searches=searches)
