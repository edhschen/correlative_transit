
from datetime import datetime

import pandas as pd
import json
def load_bike():
    name = "data/concate_data.csv"
    df = pd.read_csv(name)
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['start_time'])

    trip_pos = df[["start_station","end_station","start_time","start_lat","start_lon","end_lat","end_lon","trip_route_category"]]

    trip_pos = trip_pos[trip_pos.trip_route_category=="One Way"]
    trip_pos = trip_pos.dropna(how='any')
    trip_pos['month'] = pd.DatetimeIndex(trip_pos['start_time']).month
    trip_pos['year'] = pd.DatetimeIndex(trip_pos['start_time']).year

    trip_pos = trip_pos.groupby(['start_station',"end_station","month","year"]) \
    .agg(
        {
            'start_station':"count",
            'start_lat':"mean",
            'start_lon':"mean",
            'end_lat':"mean",
            'end_lon':"mean",
        }
    )
    trip_pos.columns = ['count','start_lat','start_lon','end_lat','end_lon']
    trip_pos = trip_pos.reset_index()

    return trip_pos

def get_month_year_data(year,month,df):
    df_res = df[(df['month']==month) & (df['year'] == year)]

    return json.loads(df_res.to_json(orient='records'))

def get_exits_data(year, month, df):
    df_res = df[(df['month'] == month) & (df['year'] == year)]

    return json.loads(df_res.to_json(orient='records'))

def load_transit():
    name = "data/transit/body_19.csv"
    df = pd.read_csv(name)
    # print(df)
    df['date'] = pd.to_datetime(df['date'])

    ridership = df[["stop_name", "daytime_routes", "division", "line", "borough", "structure", "gtfs_longitude",
                    "gtfs_latitude", "complex_id", "date", "entries", "exits"]]

    # print(ridership.dtypes)

    ridership = ridership.dropna(how='any')
    ridership['month'] = pd.DatetimeIndex(ridership['date']).month
    ridership['year'] = pd.DatetimeIndex(ridership['date']).year
    # print(ridership.head(50))

    ridership.groupby('date')[['stop_name', 'entries']].apply(
        lambda x: x.set_index('stop_name').to_dict()).to_json(r'.\data\entries_2019.json')


    ridership = ridership.groupby(
        ['stop_name', 'gtfs_latitude', 'gtfs_longitude', 'complex_id', "month", "year"]).agg(
        {'entries': "sum", 'exits': "sum"})
    ridership.columns = ['total_entries', 'total_exits']
    ridership = ridership.reset_index()

    return ridership

if __name__ == '__main__':
    transit_data = load_transit()
    print(transit_data)