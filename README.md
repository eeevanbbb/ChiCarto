# ChiCarto
ChiCarto is a gateway into geo-specific location data about the city of Chicago.

## Installation
0. Make sure you have [Python](https://www.python.org/downloads/) installed
1. Install [pip](https://pip.pypa.io/en/stable/installing/)
2. From the root folder, run `pip install -r requirements.text`

## Usage
1. From the root folder, run `python main.py`
2. In your browser, navigate to http://127.0.0.1:5000/

## Testing
1. From the root folder, run `python tests.py`

## What is Implemented and Roughly in Which Files
* Display a front page with a map of the city (implemented in python files, templates/index.html)
* Register an account (implemented in python files)
* Log in (implemented in python files)
* Log out (implemented in python files)
* Delete your account (implemented in python files, templates/delete-account.html)
* Create a search (implemented in python files, templates/create.html, static/create.js)
* View your searches by name (implemented in python files, templates/user.html, static/table.css, static/table.js)
* View each search on a map (implemented in python files, templates/index.html, static/mapping.js)
* Rate a search and view averaged search rating (implemented in python files, templates/user.html, templates/searches.html, static/rate.js, static/style.css)
* Browse a list of all searches created by all users (implemented in python files, templates/searches.html, static/table.css, static/table.js)

## Teams
* Backend models, logic, and tests = Mark, Evan, and Sam
* Frontend html, javascript, google maps = Evan, Michelle, Tyler, and Alex
* Project Coordinator = Michelle

## Changes from Proposal
* The project proposal described the ability for logged-in users to save other users' searches to their own profile. This was not implemented, because we decided it made more sense for users to only have their own searches that they created displayed on their own profile page. 
* Instead of using React.js framework as proposed for the front end, we used a combination of html, css, and javascript.
* Our Use Case diagram gave unregistered users the ability to create a search. We decided in our actual implementation to only allow registered users to create a search, although unregistered users can still browse all of the searches. 
* "Create Account" activity diagram is implemented exactly as proposed, except instead of a username, an email is used. 
* "Saving a Search" activity diagram was not implemented as proposed. Instead, the user only has the ability to save searches they create to their profile, and this occurs automatically.
* "Loading A Search" is implemented as proposed in the activity diagram, but with an additional ability for users that are not logged in to load searches.
* "Delete Account" was implemented more simply than proposed, skipping the proposed steps of seleting "Settings" and "Manage Account".
* "Rate Saved Search" was implemented as proposed in the activity diagram, except users _are_ allowed to rate their own searches.
* "Create Search" was implemented as proposed in the activity diagram, but with the ability to name the search and associate a category with a search. Also note that created searches are automatically saved, without the user having to select "save" functionality.
* "Browse Searches" was not implemented as proposed, due to a lack of time, the ability to "Sort by category," "Sort by rating," and "Search by name" were not implemented.

## Suggested Acceptance Tests and Expected Results
### Register an account
  1. From main page: Select "Register"
  2. Enter an email address, password of at least 6 characters, and retype the password, then select "Register" 
  3. Expected result: You will be taken to a page that says "Welcome to your account! You are logged in as (your email)", with an empty table entitled "Your Searches"
### Log out, then log back in
  1. From user page of logged in user: Select "Log out" 
  2. Expected result: You will be taken back to the home page
  3. From the home page: Select "Log In"
  4. Enter your email address and password, then select Login
  5. Expected result: You will be taken to a page that says "Welcome to your account! You are logged in as (your email)", with a table entitled "Your Searches"
### Create a search
  1. From user page of logged in user: Select "Create Search"
  2. Select data source "Crimes 2001-Present", click "add"
  3. A new box "Limit: 10" should pop up. click "set"
  4. Under "Filter", a box should read "primary_type". Click "Add".
  5. Type "THEFT" into the text box below that says "Value:". Click "Add". 
  6. Into Latitude, type "41.78", and click "Set". 
  7. Into Longitude, type -87.60, and click "Set".  
  8. Into Radius, type "100000" and click "Set". 
  9. Under Metadata, find the text box that says "Search Name", and type "MySearch". Click "Set".
  10. Under Search Category, type "crime", and click "Set". 
  11. Go back up to "Data Source". Select data source "Building Violations". Click "Add".
  12. A new box "Limit: 10" should pop up. click "set".
  13. Under "Filter", select "violation_status", and click "Add". 
  14. Under "Value", select "OPEN". 
  15. On the right side of the page, under "Output", select "Submit". 
  16. Expected result: CURRENTLY NOT AS IT SHOULD BE: TODO
### View your searches
  1. Click "My Account"
  2. Expected result: All searches you have created will be displayed in a table
### Rate a search
  1. Click "My Account"
  2. For an unrated search listed on your table, there should be five empty stars next to it. Choose a search with a current rating of 0.  Select two and a half stars, then click submit.
  3. Refresh the page.
  4. Expected result: The five star widget will disappear. Upon refreshing, the page should show 2.5 in the rating column next to the search you rated. 
### View a search on the map (_i.e. load a search_)
  1. Click "My Account"
  2. If you have previously created a search, it will be in the table. Click the name of a search you previously created.
  3. Expected result: a map will load displaying the search.
### Get datapoint information while viewing a search
  1. Display a search.
  2. Click on one of the red markers. 
  3. Expected result: A small textbox should appear displaying additional data.
### View a list of all searches
  1. From the main page: Click "Browse All Searches"
  2. Expected result: You will be taken to a page that says "All Searches" and shows a table displaying all searches created by all users.
### Delete your account
  1. Log in to your account
  2. Select "Delete Account"
  3. You will be taken to a page that says: "We're sorry to see you go! You are logged in as (your email). Are you sure you want to delete your account?" 
  4. Select "Delete Account"
  5. Expected result: Your account will be deleted. You will no longer be able to log in using your email and password. However, the searches you have created will still exist and will not be deleted. 

## Miscellaneous
* The Google Maps API we are using is free until exceeding 25,000 map loads per day for 90 consecutive days.
* ChiCarto uses open data about the city of Chicago. Although it is possible to create a search centered in areas of the world other than Chicago, there is no data for areas outside of Chicago. 
* It is possible for two searches to have the same name.
* It is not possible for a person to register two accounts with the same email.
* Maps may take a while to load, especially when loading a lot of data.
* Given more time, we would add more searches, and create "delete search" functionality. 