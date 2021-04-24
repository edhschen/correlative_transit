
import data_proc.load_database as proc
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import autocorrelation_plot
from statsmodels.tsa.arima.model import ARIMA
all_bike_data = proc.load_bike_full()

filtered_df = all_bike_data[ (all_bike_data['year']==2019)&(all_bike_data['start_station']==3049)]

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

series = series.set_index('date')

X = series.values
size = int(len(vals)*0.66)
train,test = X[:size],X[size:]
history = [x for x in train]
predictions = []

model = ARIMA(series,order(7,1,0))
model_fit = model.fit()
print(model_fit.summary())

# print(series)
# series.plot()
# plt.show()
# autocorrelation_plot(series)
# plt.show()
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