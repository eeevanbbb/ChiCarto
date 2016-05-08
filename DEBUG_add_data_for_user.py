import sys

import main
from models import *

user_email = sys.argv[1]

user = User.query.filter_by(email=user_email)[0]

uchicago_lat = 41.7886
uchicago_long = -87.5987
radius = 1000
url1 = "https://data.cityofchicago.org/resource/6zsd-86xi.json"
data_source1 = DataSource("Crimes 2001 - Present",url1,[],[])
search1 = Search([data_source1],uchicago_lat,uchicago_long,radius)

user.add_search(search1)
db.session.commit()
