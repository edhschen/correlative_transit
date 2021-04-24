""" routes.py - Flask route definitions

Flask requires routes to be defined to know what data to provide for a given
URL. The routes provided are relative to the base hostname of the website, and
must begin with a slash."""
from flaskapp import app
from flask import render_template
from flask import request
import data_proc.load_database as proc
import json

import pandas as pd
import numpy as np
transit_data_2019 = proc.load_transit('New York', 2019)
transit_data_2020 = proc.load_transit('New York', 2020)
transit_data_2021 = proc.load_transit('New York', 2021)
all_data = proc.load_bike()
cta_bus = proc.load_cta_bus()
air_data_2019 = proc.load_air_traffic('flightdata_2019.csv')
air_data_2020 = proc.load_air_traffic('flightdata_2020.csv')

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
    return render_template('bike_trip_vis.html', station_data=station_data)


@app.route('/transit')
def transit():
    # return render_template('transit_vis.html',transit_data=transit_data)
    return render_template('transit_vis.html')

@app.route('/air')
def air():
    with open('data/station.json') as f:
        station_data = json.load(f)
    return render_template('air_traffic_vis.html', station_data=station_data)

@app.route('/get_month_year_data')
def get_month_year_data():
    month = int(request.args.get('month'))
    year = int(request.args.get('year'))
    bike_data = proc.get_month_year_data(year, month, all_data)

    return json.dumps(bike_data)


@app.route('/get_month_year_transit_data')
def get_month_year_transit_data():
    month = int(request.args.get('month'))
    year = int(request.args.get('year'))
    if year == 2019:
        filtered_transit_data = proc.get_month_year_transit_ridership_data(transit_data_2019, month, year)
    elif year == 2020:
        filtered_transit_data = proc.get_month_year_transit_ridership_data(transit_data_2020, month, year)
    elif year == 2021:
        filtered_transit_data = proc.get_month_year_transit_ridership_data(transit_data_2021, month, year)

    return json.dumps(filtered_transit_data)

@app.route('/get_month_year_air_traffic_data')
def get_month_year_air_traffic_data():
    month = int(request.args.get('month'))
    year = int(request.args.get('year'))
    if year==2019:
        filtered_air_data = proc.get_month_year_data(year, month, air_data_2019)
    elif year==2020:
        filtered_air_data = proc.get_month_year_data(year, month, air_data_2020)
    return json.dumps(filtered_air_data)

@app.route('/cta/bus/daily/<date>')
def cta_bus_daily(date):
    data = proc.load_cta_bus()
    print(type(data))
    date = date[:2] + "/" + date[2:4] + "/" + date[4:]
    print(cta_bus)
    data = data[data["date"]==date].set_index("route")
    print(data)
    data = data.to_dict("index")
    print(data)
    return json.dumps(data)

@app.route('/cta/bus')
def cta_bus():
    return render_template("cta_visualize_stops.html")