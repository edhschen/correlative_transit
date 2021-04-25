from datetime import datetime

import pandas as pd
import json


def load_bike():
    name = "data/concate_data.csv"
    df = pd.read_csv(name)
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['end_time'])

    trip_pos = df[["start_station", "end_station", "start_time", "start_lat", "start_lon", "end_lat", "end_lon",
                   "trip_route_category"]]

    trip_pos = trip_pos[trip_pos.trip_route_category == "One Way"]
    trip_pos = trip_pos.dropna(how='any')
    trip_pos['month'] = pd.DatetimeIndex(trip_pos['start_time']).month
    trip_pos['year'] = pd.DatetimeIndex(trip_pos['start_time']).year

    trip_pos = trip_pos.groupby(['start_station', "end_station", "month", "year"]) \
        .agg(
        {
            'start_station': "count",
            'start_lat': "mean",
            'start_lon': "mean",
            'end_lat': "mean",
            'end_lon': "mean",
        }
    )
    trip_pos.columns = ['count', 'start_lat', 'start_lon', 'end_lat', 'end_lon']
    trip_pos = trip_pos.reset_index()

    return trip_pos


def load_bike_full():
    name = "data/concate_data.csv"
    df = pd.read_csv(name)
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['end_time'])

    trip_pos = df[["start_station", "end_station", "start_time", "start_lat", "start_lon", "end_lat", "end_lon",
                   "trip_route_category"]]

    trip_pos = trip_pos[trip_pos.trip_route_category == "One Way"]
    trip_pos = trip_pos.dropna(how='any')
    trip_pos['date'] = trip_pos['start_time'].dt.normalize()
    trip_pos['ts'] = trip_pos['date'].astype('int64')

    trip_pos['month'] = pd.DatetimeIndex(trip_pos['start_time']).month
    trip_pos['year'] = pd.DatetimeIndex(trip_pos['start_time']).year
    trip_pos['day'] = pd.DatetimeIndex(trip_pos['start_time']).day
    trip_pos['dayofweek'] = pd.DatetimeIndex(trip_pos['start_time']).dayofweek

    # rows = trip_pos.iloc[0]
    # ts = rows['ts']
    # print(trip_pos)

    # by_month = trip_pos.groupby(['date']) \
    #     .agg(
    #         {
    #             'ts':'first',
    #             'start_station':'count'
    #         }
    #     )
    # by_month.columns=['ts', 'count']
    # by_month = by_month.reset_index()
    # print(by_month)

    return trip_pos


def get_month_year_data(year, month, count_filter, df):
    df_res = df[(df['month'] == month) & (df['year'] == year) & (df['count'] >= count_filter)]

    return json.loads(df_res.to_json(orient='records'))


def load_transit_gtfs(city='New York'):
    file_routes = "data/transit/gtfs/" + city + "/routes.csv"
    file_trips = "data/transit/gtfs/" + city + "/trips.csv"
    file_stop_times = "data/transit/gtfs/" + city + "/stop_times.csv"
    file_stops = "data/transit/gtfs/" + city + "/stops.csv"

    df_routes = pd.read_csv(file_routes)
    df_trips = pd.read_csv(file_trips)
    df_stop_times = pd.read_csv(file_stop_times)
    df_stops = pd.read_csv(file_stops)
    df_routes['route_id'] = df_routes['route_id'].astype(str)
    df_trips['route_id'] = df_trips['route_id'].astype(str)
    # print(df_trips.dtypes, '\n', df_routes.dtypes)

    m = df_trips[['route_id', 'trip_id']].merge(df_routes[['route_id']], on='route_id', how='inner', sort=True)
    # print(m.info())
    n = m[['route_id', 'trip_id']].merge(df_stop_times[['stop_id', 'trip_id']], on='trip_id', how='inner', sort=True)
    # print(n.info())
    n = n[['stop_id', 'route_id']]
    n.reset_index()
    n = n.groupby(['stop_id'], as_index=False).agg({
        'route_id': 'first'
    })
    n.reset_index()
    # print(n.info())
    o = n[['route_id', 'stop_id']].merge(df_stops[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']], on='stop_id',
                                         how='inner', sort=True)
    o.reset_index()
    o["COORDINATES"] = o[["stop_lon", "stop_lat"]].values.tolist()
    o.reset_index()
    o = o.drop(['stop_lat', 'stop_lon'], 1)
    # print(o.info())
    # o.to_json(r'.\data\stop_list.json', orient='records', lines=True)
    return o


def load_transit(city='New York', year=2019):
    data = 'data/transit/body_' + str(year) + '.csv'

    df_ridership = pd.read_csv(data)
    # df_stops_routes = load_transit_gtfs(city)
    # print(df_ridership.info())
    # print(df_stops_routes.info())

    # df_stops_routes = df_stops_routes.groupby(['stop_name'], as_index=False).agg({
    #     'route_id': 'first',
    #     'stop_id': 'first',
    #     'COORDINATES': 'first'
    # })
    # print(df_stops_routes.head(50))

    df_ridership['date'] = pd.to_datetime(df_ridership['date'])

    ridership = df_ridership[
        ["stop_name", "daytime_routes", "division", "line", "borough", "structure", "gtfs_longitude",
         "gtfs_latitude", "complex_id", "date", "entries", "exits"]]
    # print(ridership.dtypes)

    ridership = ridership.dropna(how='any')

    ridership['month'] = pd.DatetimeIndex(ridership['date']).month
    ridership['year'] = pd.DatetimeIndex(ridership['date']).year
    # print(ridership.info())

    ridership["COORDINATES"] = ridership[["gtfs_longitude", "gtfs_latitude"]].values.tolist()
    ridership.reset_index()
    ridership = ridership.drop(["division", "line", "borough", "structure", 'gtfs_longitude', 'gtfs_latitude'], 1)
    # print(ridership.info())

    # ridership.groupby('date')[['stop_name', 'entries']].apply(
    #     lambda x: x.set_index('stop_name').to_dict()).to_json(r'.\data\entries_2019.json')
    #
    #
    ridership = ridership.groupby(['stop_name', "daytime_routes", "month", "year"]).agg(
        {
            'entries': "sum",
            'exits': "sum",
            'COORDINATES': 'first'
        }
    )
    ridership.columns = ['total_entries', 'total_exits', 'COORDINATES']
    ridership = ridership.reset_index()
    # print(ridership.info())

    return ridership


def get_month_year_transit_ridership_data(df, entries_filter, month='Jan', year=2019):
    df_res = df[(df['month'] == month) & (df['year'] == year) & (df['total_entries'] >= entries_filter)]

    return json.loads(df_res.to_json(orient='records'))


def load_transit_all(city='New York', year=2019):
    data = 'data/transit/body_' + str(year) + '.csv'

    df_ridership = pd.read_csv(data)
    df_ridership['date'] = pd.to_datetime(df_ridership['date'])

    ridership = df_ridership[
        ["stop_name", "daytime_routes", "division", "line", "borough", "structure", "gtfs_longitude",
         "gtfs_latitude", "complex_id", "date", "entries", "exits"]]
    # print(ridership.dtypes)

    ridership = ridership.dropna(how='any')
    ridership['date'] = ridership['date'].dt.normalize()

    ridership['month'] = pd.DatetimeIndex(ridership['date']).month
    ridership['year'] = pd.DatetimeIndex(ridership['date']).year
    ridership['day'] = pd.DatetimeIndex(ridership['date']).day
    ridership['dayofweek'] = pd.DatetimeIndex(ridership['date']).dayofweek
    # print(ridership.info())

    ridership = ridership.drop(["division", "line", "borough", "structure", 'gtfs_longitude', 'gtfs_latitude'], 1)
    # print(ridership.head(50))

    return ridership

def get_month_year_air_traffic_data(year, month, df):
    df_res = df[(df['month'] == month) & (df['year'] == year)]

    return json.loads(df_res.to_json(orient='records'))


def load_air_traffic(fil_name):
    name = 'data/air/' + fil_name
    df = pd.read_csv(name)

    df['date'] = pd.to_datetime(df['day'])
    df['latitude_1'] = df['latitude_1'].round(decimals=3)
    df['latitude_2'] = df['latitude_2'].round(decimals=3)
    df['longitude_1'] = df['longitude_1'].round(decimals=3)
    df['longitude_2'] = df['longitude_2'].round(decimals=3)

    df['month'] = pd.DatetimeIndex(df['day']).month
    df['year'] = pd.DatetimeIndex(df['day']).year

    departures = df.groupby(['origin', 'destination', 'month', 'year']).agg(
        {'origin': 'count', 'latitude_1': 'first', 'longitude_1': 'first', 'latitude_2': 'first',
         'longitude_2': 'first'})
    departures.columns = ['count', 'latitude_1', 'longitude_1', 'latitude_2', 'longitude_2']
    departures = departures.reset_index()

    return departures

def load_air_traffic_full(fil_name):
    name = 'data/air/' + fil_name
    df = pd.read_csv(name)
    df['date'] = pd.to_datetime(df['day'])

    return df

def q33(x):
    return x.quantile(0.33)


def q66(x):
    return x.quantile(0.66)


def load_cta_bus():
    name = "data/cta/cta_bus_data.csv"
    df = pd.read_csv(name)
    df["year"] = df["date"].str.split("/",expand=True)[2]
    gb = df.groupby("route")
    q = gb.agg({'rides': [q33, q66]})
    df = df.join(q, on='route', rsuffix='_r')
    df["q33"] = df[("rides", "q33")]
    df["q66"] = df[("rides", "q66")]
    df = df.drop([("rides", "q33"), ("rides", "q66")], axis=1)
    return df


if __name__ == '__main__':
    # transit_data = load_transit()
    # print(transit_data)
    # transit_data = load_transit()
    # print(transit_data)
    transit_data_all = load_transit_all()
