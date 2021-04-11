
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