import json

from flask import Flask
from flask.ext.security import Security, SQLAlchemyUserDatastore

from app import app, db
from models import *
from views import *

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Initialize DataSource metadata
def load_meta():
  with open('sources.json','r') as f:
    js = json.load(f)
    for source in js['sources']:
      #print (str(s))
      name = source['name']
      url = source['url']
      tk = source['title_key']
      fm = []
      for fil_met in source['filters']:
        fname = fil_met['name']
        type_ = fil_met['type']
        ch_fr = None
        if type_ == 'choice':
          ch_fr = ",".join(fil_met['choose_from'])
        _filter = FilterMeta(fname, type_, ch_fr)
        fm.append(_filter)
      ds = DataSource(name,url,fm, title_key=tk)
      db.session.add(ds)
    db.session.commit()
      

# Run the app
if __name__ == "__main__":
    db.init_app(app)
    try:
        open('/tmp/test.db')
    except IOError:
        db.create_all()
        load_meta()
    app.run(debug=True)
