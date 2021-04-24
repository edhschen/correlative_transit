
from datetime import datetime

import pandas as pd
import json
def load_bike():
    name = "data/concate_data.csv"
    df = pd.read_csv(name)
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['end_time'])

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

def load_bike_full():
    name = "data/concate_data.csv"
    df = pd.read_csv(name)
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['end_time'])

    trip_pos = df[["start_station","end_station","start_time","start_lat","start_lon","end_lat","end_lon","trip_route_category"]]

    trip_pos = trip_pos[trip_pos.trip_route_category=="One Way"]
    trip_pos = trip_pos.dropna(how='any')
    trip_pos['date'] = trip_pos['start_time'].dt.normalize()
    trip_pos['ts'] = trip_pos['date'].astype('int64')

    trip_pos['month'] = pd.DatetimeIndex(trip_pos['start_time']).month
    trip_pos['year'] = pd.DatetimeIndex(trip_pos['start_time']).year
    
    trip_pos = trip_pos[(trip_pos['year']==2019)&(trip_pos['start_station']==3049)]
    rows = trip_pos.iloc[0]
    ts = rows['ts']
    print(trip_pos)

    by_month = trip_pos.groupby(['date']) \
        .agg(
            {
                'ts':'first',
                'start_station':'count'
            }
        )
    by_month.columns=['ts', 'count']
    by_month = by_month.reset_index()
    print(by_month)

    # trip_pos.info()
    # trip_pos = df[["start_station","end_station","start_time","start_lat","start_lon","end_lat","end_lon","trip_route_category"]]

    # trip_pos = trip_pos[trip_pos.trip_route_category=="One Way"]
    # trip_pos = trip_pos.dropna(how='any')
    # trip_pos['month'] = pd.DatetimeIndex(trip_pos['start_time']).month
    # trip_pos['year'] = pd.DatetimeIndex(trip_pos['start_time']).year

    # trip_pos = trip_pos.groupby(['start_station',"end_station","month","year"]) \
    # .agg(
    #     {
    #         'start_station':"count",
    #         'start_lat':"mean",
    #         'start_lon':"mean",
    #         'end_lat':"mean",
    #         'end_lon':"mean",
    #     }
    # )
    # trip_pos.columns = ['count','start_lat','start_lon','end_lat','end_lon']
    # trip_pos = trip_pos.reset_index()

    # return trip_pos
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

def load_air_traffic():
    name='data/air/flightlist_20190101_20190131.csv'
    df = pd.read_csv(name)

    df['firstseen'] = pd.to_datetime(df['firstseen'])
    df['lastseen'] = pd.to_datetime(df['lastseen'])
    df['day'] = pd.to_datetime(df['day']).dt.date

    airport_list = ['KBOS','KORH','KMHT','KPVD','KDCA','KIAD','KBWI','KJFK','KLGA','KEWR','KSFO','KSJC','KLAX','KSAN','KORD','KMDW']
    #airport_list = ['KLAX']

    filtered_df = df[df['origin'].isin(airport_list)]

    filtered_df = filtered_df.dropna(subset=['destination'])

    #filtered_df['month'] = pd.to_datetime(df['day']).dt.strftime('%b')
    filtered_df['month'] = pd.DatetimeIndex(filtered_df['day']).month
    filtered_df['year'] = pd.DatetimeIndex(filtered_df['day']).year

    departures = filtered_df.groupby(['origin','destination','month','year']).agg({'origin':'count','latitude_1':'first','longitude_1':'first','latitude_2':'first','longitude_2':'first'})
    departures.columns = ['count','latitude_1','longitude_1','latitude_2','longitude_2']
    departures = departures.reset_index()

#   print(trip_pos)
    return departures

def q33(x):
    return x.quantile(0.33)
def q66(x):
    return x.quantile(0.66)
def load_cta_bus():
    name="data/cta/cta_bus_data.csv"
    df = pd.read_csv(name)
    gb = df.groupby("route")
    q = gb.agg({'rides': [q33, q66]})
    df = df.join(q, on='route', rsuffix='_r')
    df["q33"] = df[("rides", "q33")]
    df["q66"] = df[("rides", "q66")]
    df = df.drop([("rides", "q33"), ("rides", "q66")],axis=1)
    return df

if __name__ == '__main__':
    transit_data = load_transit()
    print(transit_data)
