# ChiCarto
ChiCarto is a gateway into geo-specific location data about the city of Chicago. ChiCarto provides an easy-to-use interface to view, collate, and browse information about the city. Users can create accounts associated with their email to allow them to log into the site. Once logged in, users can create a "Search." A "Search" maps one or more dataset about the city of Chicago onto a google maps interface. For example, a user could create a map displaying information about criminal incidents, reported tree trims, and building violations within their neighborhood. Additional datapoint information can be viewed by clicking on the red pinpoints on the map. Once the search is created, it will automatically be stored in the users' personal list of created searches, as well as on a list of searches created by all users accessing the site. Users can also rate each other's searches out of five stars, as well as delete their account if desired. 

## Installation
0. Make sure you have [Python](https://www.python.org/downloads/) installed
1. Install [pip](https://pip.pypa.io/en/stable/installing/)
2. From the root folder, run `pip install -r requirements.text`

## Usage
1. From the root folder, run `python main.py`
2. In your browser, navigate to http://127.0.0.1:5000/

## Testing
1. From the root folder, run `python tests.py`

## What is Implemented and Where (Roughly)
* Display a front page with a map of the city (views.py, templates/index.html, mapping.js)
* Register an account (views.py, models.py)
* Log in (views.py, models.py)
* Log out (views.py, models.py)
* Delete your account (views.py, models.py, templates/delete-account.html)
* Create a search (views.py, models.py, templates/create.html, static/create.js)
* View your searches by name (views.py, models.py, templates/user.html)
* View each search on a map (views.py, models.py, templates/index.html, static/mapping.js)
* Rate a search and view averaged search rating (views.py, models.py, templates/user.html, templates/searches.html, static/rate.js)
* Browse a list of all searches created by all users (views.py, models.py, templates/searches.html)

## Teams
* Backend models, logic, and tests = Mark, Evan, and Sam
* Frontend html, javascript, google maps = Evan, Michelle, Tyler, and Alex
* Project Coordinator = Michelle

## Usage Tutorial
#### Register an account
  1. From main page: Select "Register"
  2. Enter an email address, password of at least 6 characters, and retype the password, then select "Register"
  3. Expected result: You will be taken to a page that says "Welcome to your account! You are logged in as (your email)," with an empty table entitled "Your Searches"

#### Log out, then log back in
  1. From user page of logged in user: Select "Log out"
  2. Expected result: You will be taken back to the home page
  3. From the home page: Select "Log In"
  4. Enter your email address and password, then select Login
  5. Expected result: You will be taken to a page that says "Welcome to your account! You are logged in as (your email)", with a table entitled "Your Searches"

#### Create a search
  1. From user page of logged in user: Select "Create Search"
  2. Select data source "Crimes 2001-Present", click "add"
  3. A new box "Limit: 10" should pop up. click "set"
  4. Under "Filter", a box should read "primary_type." Click "Add"
  5. Type "THEFT" into the text box below that says "Value:". Click "Add"
  6. Into Latitude, type "41.78", and click "Set"
  7. Into Longitude, type -87.60, and click "Set"  
  8. Into Radius, type "100000" and click "Set"
  9. Under Metadata, find the text box that says "Search Name", and type "MySearch". Click "Set"
  10. Under Search Category, type "crime", and click "Set"
  11. Go back up to "Data Source". Select data source "Building Violations". Click "Add"
  12. A new box "Limit: 10" should pop up. click "set"
  13. Under "Filter", select "violation_status", and click "Add"
  14. Under "Value", select "OPEN"
  15. On the right side of the page, under "Output", select "Submit"
  16. Expected result: Map showing red points should be displayed. It should look something like this:
![alt text] (https://github.com/eeevanbbb/ChiCarto/blob/master/img1ForReadme.png "Create a Search Example")

#### View your searches
  1. Click "My Account"
  2. Expected result: All searches you have created will be displayed in a table

#### Rate a search
  1. Click "My Account"
  2. For an unrated search listed on your table, there should be five empty stars next to it. Choose a search with a current rating of 0.  Select two and a half stars, then click submit
  3. Refresh the page
  4. Expected result: The five star widget will disappear. Upon refreshing, the page should show 2.5 in the rating column next to the search you rated

#### View a search on the map (_i.e. load a search_)
  1. Click "My Account"
  2. If you have previously created a search, it will be in the table. Click the name of a search you previously created
  3. Expected result: a map will load displaying the search

#### Get datapoint information while viewing a search
  1. Display a search
  2. Click on one of the red markers
  3. Expected result: A small textbox should appear displaying additional data

#### View a list of all searches
  1. From the main page: Click "Browse All Searches"
  2. Expected result: You will be taken to a page that says "All Searches" and shows a table displaying all searches created by all users

#### Delete your account
  1. Log in to your account
  2. Select "Delete Account"
  3. You will be taken to a page that says: "We're sorry to see you go! You are logged in as (your email). Are you sure you want to delete your account?"
  4. Select "Delete Account"
  5. Expected result: Your account will be deleted. You will no longer be able to log in using your email and password. However, the searches you have created will still exist and will not be deleted

## Miscellaneous
* The Google Maps API we are using is free until exceeding 25,000 map loads per day for 90 consecutive days.
* ChiCarto uses open data about the city of Chicago. Although it is possible to create a search centered in areas of the world other than Chicago, there is no data for areas outside of Chicago.
* It is possible for two searches to have the same name.
* It is not possible for a person to register two accounts with the same email.
* Maps may take a while to load, especially when loading a lot of data.