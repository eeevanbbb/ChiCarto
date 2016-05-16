import sys

import main
from models import *

user_email = sys.argv[1]

user = User.query.filter_by(email=user_email)[0]

uchicago_lat = 41.7886
uchicago_long = -87.5987
radius = 1000
url1 = "https://data.cityofchicago.org/resource/6zsd-86xi.json"
# data_source1 = DataSource("Crimes 2001 - Present",url1,[],[])
# search1 = Search([data_source1],uchicago_lat,uchicago_long,radius)

# user.add_search(search1)

# filter1 = Filter("primary_type","THEFT")
# data_source2 = DataSource("Crimes 2001 - Present",url1,[filter1],[])
# search2 = Search([data_source2],uchicago_lat,uchicago_long,radius)

# user.add_search(search2)

data_source1 = DataSource("Crimes 2001 - Present", url1, [])

filter1 = Filter("primary_type", "THEFT")

data_search1 = DataSearch(data_source1, [])
data_search2 = DataSearch(data_source1, [filter1])

search1 = Search([data_search1], uchicago_lat, uchicago_long, radius)
search2 = Search([data_search2], uchicago_lat, uchicago_long, radius)

user.add_search(search1)
user.add_search(search2)

db.session.commit()
