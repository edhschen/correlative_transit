""" routes.py - Flask route definitions

Flask requires routes to be defined to know what data to provide for a given
URL. The routes provided are relative to the base hostname of the website, and
must begin with a slash."""
from flaskapp import app
from flask import render_template
from flask import request,Response

import data_proc.load_database as proc
import json

import pandas as pd
import numpy as np
import io
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure
import random
from data_proc.bike_data_analysis import ARIMA_predict_year_station

transit_data = proc.load_transit()
all_data = proc.load_bike()
all_bike_data = proc.load_bike_full()
cta_bus = proc.load_cta_bus()

# air_data_2019 = proc.load_air_traffic('flightdata_2019.csv')
# air_data_2020 = proc.load_air_traffic('flightdata_2020.csv')

# The following two lines define two routes for the Flask app, one for just
# '/', which is the default route for a host, and one for '/index', which is
# a common name for the main page of a site.
#
# Both of these routes provide the exact same data - that is, whatever is
# produced by calling `index()` below.

@app.route('/')
@app.route('/la/bike')
def la_bike():
    with open('data/station.json') as f:
        station_data = json.load(f)
    year = 2019
    station = 3049
    return render_template('bike_trip_vis.html', station_data=station_data,year=year,station=station)


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
    filtered_transit_data = proc.get_exits_data(year, month, transit_data)

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


@app.route("/bike_prediction_<int:year>_<int:station>.svg")
def plot_prediction(year,station):
    print(year,station)
    if station!=-1:
        station_name = str(request.args.get('station_name'))
        status, fig=ARIMA_predict_year_station(all_bike_data,year,station,station_name)
        print(status)
        if status:
            
            output = io.BytesIO()
            FigureCanvasSVG(fig).print_svg(output)
            return Response(output.getvalue(), mimetype="image/svg+xml")
        else:
            return "Fail"