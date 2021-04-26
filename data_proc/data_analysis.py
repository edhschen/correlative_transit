
import data_proc.load_database as proc
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import autocorrelation_plot
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error

matplotlib.use('agg')

def ARIMA_predict_year_station(series,year,station_name):

    series = series.set_index('date')
    labels = series.index

    series.index = series.index.to_period('D')

    X = series.values
    size = int(len(X)*0.66)
    if size==0:
        return False,None
    else:
        train,test = X[:size],X[size:]
        history = [x for x in train]
        test_label = labels[size:]
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

        # rmse = np.sqrt(mean_squared_error(test,predictions))
        full_test = X
        full_pridiction = np.concatenate([train,np.array(predictions)[:,np.newaxis]])
        fig,ax = plt.subplots()
        ax.set_title("ARIMA Model in Year %s at Station %s "%(year,station_name))
        ax.plot(labels,full_test,label="Ground Truth")
        ax.plot(labels,full_pridiction,label="Prediction")
        ax.vlines([labels[size]],-1,2*np.max(full_test),color='r')
        ax.legend()
        return True,fig

