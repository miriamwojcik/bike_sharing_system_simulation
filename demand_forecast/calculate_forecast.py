# Calculate a demand forecast for station using classification

# import libraries
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn import metrics
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, KFold
from tabulate import tabulate
import pickle
import datetime

# import modules
from generating_data.demand_forecast_data_prep import get_station_data, get_hour, get_day, get_month, get_holidays, is_weekend,  get_temp, get_rain
from generating_data.generate_weather_data import get_weather_forecast

def calculate_demand_forecast(station, date):

    import math
    def custom_round(num):
        i, d = divmod(num, 1)
        if d>0.35:
            num = math.ceil(num)
        else:
            num = round(num)
        return num

    # PREDICT RENTALS USING RANDOM FOREST
    def predict_rentals(historical_data, df_demand_forecast, station, date):
        # get_data
        historical_data = historical_data
        df_demand_forecast = df_demand_forecast
        station = station

        # Seperate labels and data
        # col: 0-dateTime, 1-rentals, 2-returns, 3-hour,......, 9 - rain
        X = historical_data.iloc[:,3:10].values

        # rented label values
        y = historical_data.iloc[:,1].values

        ###Split into train and test set
        seed=100
        train_X, test_X, train_y, test_y = train_test_split(X, y,
                                                            train_size=0.80, test_size=0.2,
                                                            shuffle=y,
                                                            random_state=seed)
        # Feature Scaling
        #https://stackabuse.com/random-forest-algorithm-with-python-and-scikit-learn/
        sc = StandardScaler()
        train_X = sc.fit_transform(train_X)
        test_X = sc.transform(test_X)
        # train RF
        rfr = RandomForestRegressor(n_estimators=50, random_state=1, min_samples_leaf = 200)
        rfr.fit(train_X, train_y)

        # To speed up development read model from the file
        # path = 'generating_data/models/rental_model_' + station + '.sav'
        # rfr = pickle.load(open(path, 'rb'))

        targ_X = sc.transform(df_demand_forecast)
        # make predictions for target data
        targ_y = rfr.predict(targ_X)
        data = {'station':station, 'dateTime': date.date(), 'hour':df_demand_forecast['hour'], 'rentals_forecast':targ_y}
        df = pd.DataFrame(data)
        pred = rfr.predict(test_X)
        df['rentals_forecast'] = df['rentals_forecast'].apply(custom_round)
        # print('MSE: ', metrics.mean_squared_error(test_y, pred))
        # print('Root MSE:', np.sqrt(metrics.mean_squared_error(test_y, pred)))
        # print('R2', metrics.r2_score(test_y, pred))
        return df

    # PREDICT RETURNS USING RANDOM FOREST
    def predict_returns(historical_data, df_demand_forecast, station, date):
        historical_data = historical_data
        df_demand_forecast = df_demand_forecast
        station = station
        
        # Separate labels and data
        # col: 0-dateTime, 1-rentals, 2-returns, 3-hour,......, 9 - rain
        X = historical_data.iloc[:,3:10].values
        # returned label values
        y = historical_data.iloc[:,2].values

        ###Split into train and test set
        seed=100
        train_X, test_X, train_y, test_y = train_test_split(X, y,
                                                            train_size=0.8, test_size=0.2,
                                                            shuffle=y,
                                                            random_state=seed)
        
        # Feature Scaling
        #https://stackabuse.com/random-forest-algorithm-with-python-and-scikit-learn/
        sc = StandardScaler()
        train_X = sc.fit_transform(train_X)
        test_X = sc.transform(test_X)

        # train RF
        rfr = RandomForestRegressor(n_estimators=50, random_state=1, min_samples_leaf = 200)
        rfr.fit(train_X, train_y)

        # path = 'generating_data/models/returns_model_' + station + '.sav'
        # rfr = pickle.load(open(path, 'rb'))

        targ_X = sc.transform(df_demand_forecast)
        # make predictions for target data
        targ_y = rfr.predict(targ_X)
        data = {'station':station, 'dateTime': date.date(), 'hour':df_demand_forecast['hour'], 'returns_forecast':targ_y}
        df = pd.DataFrame(data)
        df['returns_forecast'] = df['returns_forecast'].apply(custom_round)
        return df

    

    # date = date
    station = station

    print('Calculating the forecast for the station no ' + str(station))
    
    # GET THE HISTORICAL DATA FOR THE STATION
    historical_data = get_station_data(station)
    historical_data = historical_data.reset_index()
    # in production read data from the file
    # path = 'generating_data/data/hist_station_data_' + station + '.csv'
    # historical_data = pd.read_csv(path)
    # a data frame to store data for prediction
    df_demand_forecast = pd.DataFrame(columns=['hour', 'month', 'day', 'weekend', 'holiday', 'temp', 'rain'])

    # get weather, holiday, weekend details for target date
    month = get_month(date)
    day = get_day(date)
    weekend = is_weekend(date)
    holiday = get_holidays(date)
    temp = get_temp(date)
    rain = get_rain(date)

    # add data for each hour
    for i in range(0,24):
        hour = i
        new = {'hour':hour, 'month':month, 'day':day, 'weekend':weekend, 'holiday':holiday, 'temp':temp, 'rain':rain}
        df_demand_forecast = df_demand_forecast.append(new, ignore_index=True)
    

    rentals_forecast = predict_rentals(historical_data, df_demand_forecast, station, date)
    returns_forecast = predict_returns(historical_data, df_demand_forecast, station, date)
    df_df = rentals_forecast.merge(returns_forecast, how='inner', on=['hour', 'station', 'dateTime'])
    return df_df

