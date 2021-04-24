
import data_proc.load_database as proc
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import autocorrelation_plot
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
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
series.index = series.index.to_period('D')

X = series.values
size = int(len(X)*0.66)
train,test = X[:size],X[size:]
history = [x for x in train]
predictions = []
for t in range(len(test)):

    model = ARIMA(history,order=(7,1,0))

    model_fit = model.fit()
    output = model_fit.forecast()
    yhat = output[0]
    predictions.append(yhat)
    obs = test[t]
    history.append(obs)
    print('predicted=%f, expected=%f' % (yhat, obs))
rmse = np.sqrt(mean_squared_error(test,predictions))
print('Test RMSE: %.3f' % rmse)
plt.plot(test)
plt.plot(predictions, color='red')
plt.show()
