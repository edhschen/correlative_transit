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
from data_proc.data_analysis import ARIMA_predict_year_station

transit_data_2019 = proc.load_transit('New York', 2019)
transit_data_2020 = proc.load_transit('New York', 2020)
transit_data_2021 = proc.load_transit('New York', 2021)

transit_data_2019_full = proc.load_transit_all('New York', 2019)
transit_data_2020_full = proc.load_transit_all('New York', 2020)
transit_data_2021_full = proc.load_transit_all('New York', 2021)

all_data = proc.load_bike()
all_bike_data = proc.load_bike_full()
cta_bus = proc.load_cta_bus()

air_data_2019 = proc.load_air_traffic('flightdata_2019.csv')
air_data_2020 = proc.load_air_traffic('flightdata_2020.csv')
air_data_2019_full = proc.load_air_traffic_full('flightdata_2019.csv')
air_data_2020_full = proc.load_air_traffic_full('flightdata_2020.csv')

# The following two lines define two routes for the Flask app, one for just
# '/', which is the default route for a host, and one for '/index', which is
# a common name for the main page of a site.
#
# Both of these routes provide the exact same data - that is, whatever is
# produced by calling `index()` below.

@app.route('/')
def index():
    return render_template('index.html')

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

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/get_month_year_data')
def get_month_year_data():
    month = int(request.args.get('month'))
    year = int(request.args.get('year'))
    count_filter = int(request.args.get('count_filter'))
    bike_data = proc.get_month_year_data(year, month,count_filter, all_data)

    return json.dumps(bike_data)


@app.route('/get_month_year_transit_data')
def get_month_year_transit_data():
    month = int(request.args.get('month'))
    year = int(request.args.get('year'))
    city = str(request.args.get('city'))
    if city == 'New York':
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
        filtered_air_data = proc.get_month_year_air_traffic_data(year, month, air_data_2019)
    elif year==2020:
        filtered_air_data = proc.get_month_year_air_traffic_data(year, month, air_data_2020)
    else:
        filtered_air_data = 0
    return json.dumps(filtered_air_data)

@app.route('/cta/bus/daily/<date>')
def cta_bus_daily(date):
    date = date[:2] + "/" + date[2:4] + "/" + date[4:]
    data = cta_bus[cta_bus["date"]==date].set_index("route")
    data = data.to_dict("index")
    return json.dumps(data)

@app.route('/cta/bus')
def cta_bus_render():
    return render_template("cta_visualize_stops.html")


@app.route("/bike_prediction_<int:year>_<int:station>.svg")
def plot_prediction(year,station):

    
    print(year,station)
    if station!=-1:
        filtered_df = all_bike_data[(all_bike_data['year']==year) & (all_bike_data['start_station']==station)]
        by_day = filtered_df.groupby(['date']) \
            .agg(
                {
                    'ts':'first',
                    'start_station':'count'
                }
            )

        by_day.columns=['ts', 'count']
        by_day = by_day.reset_index()
        series = by_day[['date','count']]
        
        station_name = str(request.args.get('station_name'))
        status, fig=ARIMA_predict_year_station(series,year,station_name)
        print(status)
        if status:
            
            output = io.BytesIO()
            FigureCanvasSVG(fig).print_svg(output)
            return Response(output.getvalue(), mimetype="image/svg+xml")
        else:
            return "Fail"

@app.route("/transit_prediction_<int:year>.svg")
def transit_plot_prediction(year):

    stop_name = (request.args.get('stop_name'))
    daytime_routes = (request.args.get('daytime_routes'))

    print(stop_name,daytime_routes)
    if daytime_routes!=-1:
        if year == 2019:
            filtered_df = transit_data_2019_full[(transit_data_2019_full['stop_name']==stop_name)&(transit_data_2019_full['daytime_routes']==daytime_routes)]
        elif year == 2020:
            filtered_df = transit_data_2020_full[(transit_data_2020_full['stop_name']==stop_name)&(transit_data_2020_full['daytime_routes']==daytime_routes)]
        else:
            filtered_df = transit_data_2021_full[(transit_data_2021_full['stop_name']==stop_name)&(transit_data_2021_full['daytime_routes']==daytime_routes)]
        # print(filtered_df.head())

        by_day = filtered_df.groupby(['date']) \
            .agg(
                {
                    'entries':'sum'
                    # 'total_exits':'sum'
                }
            )

        by_day.columns=['count']
        by_day = by_day.reset_index()
        series = by_day[['date','count']]
        # print(series.head())
        status, fig=ARIMA_predict_year_station(series,year,stop_name)
        # print(status)
        # status = True
        # fig = Figure()
        if status:
            
            output = io.BytesIO()
            FigureCanvasSVG(fig).print_svg(output)
            return Response(output.getvalue(), mimetype="image/svg+xml")
        else:
            return "Fail"

@app.route("/air_traffic_prediction_<int:year>.svg")
def air_traffic_plot_prediction(year):

    airport = request.args.get('origin')
    print('airport ID = ',airport)

    if airport!=-1:
        if year==2019:
            filtered_df = air_data_2019_full[air_data_2019_full['origin']==airport]
        elif year==2020:
            filtered_df = air_data_2020_full[air_data_2020_full['origin']==airport]

        df_day = filtered_df.groupby(['date']).agg({'origin':'count'})

        print(df_day)

        df_day.columns=['count']
        df_day = df_day.reset_index()
        series = df_day[['date','count']]
        
        status, fig=ARIMA_predict_year_station(series,year,airport)
        print(status)
        if status:
            output = io.BytesIO()
            FigureCanvasSVG(fig).print_svg(output)
            return Response(output.getvalue(), mimetype="image/svg+xml")
        else:
            return "Fail"
