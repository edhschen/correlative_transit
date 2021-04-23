""" routes.py - Flask route definitions

Flask requires routes to be defined to know what data to provide for a given
URL. The routes provided are relative to the base hostname of the website, and
must begin with a slash."""
from flaskapp import app
from flask import render_template
from flask import request
import data_proc.load_database as proc
import json
all_data = proc.load_bike()

# The following two lines define two routes for the Flask app, one for just
# '/', which is the default route for a host, and one for '/index', which is
# a common name for the main page of a site.
#
# Both of these routes provide the exact same data - that is, whatever is
# produced by calling `index()` below.

@app.route('/')
@app.route('/index')
def index():

    with open('data/station.json') as f:
        station_data = json.load(f)
    return render_template('bike_trip_vis.html',station_data=station_data)

@app.route('/get_month_year_data')
def get_month_year_data():
    month = int(request.args.get('month'))
    year = int(request.args.get('year'))
    bike_data = proc.get_month_year_data(year,month,all_data)

    return json.dumps(bike_data)

