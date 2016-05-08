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

## Acceptance Tests
* Register an account
* Log out, then log back in
* View searches for your account
  * To populate sample data for a user, from the root folder, run `python DEBUG_add_data_for_user.py [email]` where `[email]` represents the email address you registered with
* View each search on a map

## What is Implemented
Items from iteration 1 have been implemented. This includes account creation and management, logging in and out, browsing saved searches, and viewing these searches on a map.

## Teams
* Backend models = Mark and Evan
* Other roles to be added here when code is committed...

## Changes
* The model for `DataSource` has changed to include metadata about available filters. The tests have been changed accordingly to account for the additional requirements of the constructor. We have also made changes to the data contained in user-facing pages as well as the sources available for searching, so the tests have been altered to accommodate these changes.

## Miscellaneous
* Add any miscellaneous items here...
