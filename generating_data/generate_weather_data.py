from .models import Weather_Model

import pandas as pd
import os
import calendar
import datetime
from datetime import date
import holidays
import requests
import json

# METHOD TO OBTAIN HISTORICAL DATA FROM THE FILE
def get_historical_weather():
    # Set rain to 1 if it's raining that day
    def is_raining(rain):
        if rain > 0:
            return 1
        else:
            return 0

    ###### Historical weather data preprocessing ########

    # read weather data obtained from https://home.openweathermap.org/history_bulks/new
    weather = pd.read_csv('generating_data/data/aberdeen_historical_weather.csv')

    # Change missing data to 0
    weather.fillna(0, inplace=True)

    # drop unnecesary columns
    weather = weather[['dt_iso', 'temp', 'rain_1h']]

    # rename the rain and date column
    weather = weather.rename(columns={'rain_1h':'rain', 'dt_iso': 'date'})

    #change date format
    weather['date'] = pd.to_datetime(weather['date'].str[:18], format='%Y-%m-%dT%H:%M:%S')

    # get the mean temp and rain for the date
    weather = weather.groupby([weather['date'].dt.date]).mean()

    # boolean value for the rain data
    weather['rain'] = weather['rain'].apply(is_raining)

    # Save historical data to database
    for date in weather.itertuples():
            w = Weather_Model.objects.create(date=date.Index, temperature=date.temp, rain=date.rain)


# METHOD THAT RETURNS WEATHER DATA FROM DB OR OPENWEATHER API
def get_weather_forecast(date):

    def check_database(date):
        wf = Weather_Model.objects.filter(date=date).all()
        if len(wf)>0:
            return True
        else:
            return False

    def get_forecast_from_db(date):
        wf = Weather_Model.objects.filter(date=date).all()
        d = wf[0].date
        temp = wf[0].temperature
        rain = int(wf[0].rain)
        forecast = {'date' : d, 'temp': temp, 'rain': rain}
        # df_forecast = pd.DataFrame.from_dict(forecast)
        return forecast

    def new_forcast(date):
        ###### GET WEATHER FORECAST ########
        # Weather forecast obtained using OpenWeather API
        # return temp and rain for date selected if available
        def get_date_data(forecasts, date):
            data = {}
            for forecast in forecasts:
                d = pd.to_datetime(forecast['dt'], unit='s')
                d = d.date()
                if d == date:
                    temp=forecast['temp']['day']
                    rain = 0
                    try:
                        if forecast['rain'] != None:
                            rain = 1
                    except:
                        rain = 0
                    date_data = {'date':d, 'temp': temp, 'rain': rain}
                    data = date_data
            return data

        # change date to user input in django
        date = date
        # API URL: get forecast for today and next 7 days
        url = 'https://api.openweathermap.org/data/2.5/onecall?lat=57.149651&lon=-2.0990759&exclude=current,minutely,hourly,alerts&units=imperial&appid=61f34d76e3437234180472596b348b61'
        # Get forecast from API
        res = requests.get(url)
        forecast = res.json()
        forecasts = forecast['daily']
        # Get forecast for the date selected
        date_forecast = get_date_data(forecasts, date)
        # SAVE WEATHER Forecast IN DB
        if(date_forecast) != {}:
            w = Weather_Model.objects.create(date=date_forecast['date'], temperature=date_forecast['temp'], rain=date_forecast['rain'])
        # Create dataframe from the forecast
        # df_forecast = pd.DataFrame.from_dict(date_forecast)
        return date_forecast

    date = date
    today = datetime.datetime.today()
    today = today.date()
    delta = datetime.timedelta(days=8)
    if date>=(today + delta):
        print('No data available for the date selected')
        return -1
    elif (date >= today and date < (today + delta)) :
        # if data in db return forecast
        db = check_database(date)
        if db == True:
            forecast = get_forecast_from_db(date)
            return forecast
        # if not get forecast from API
        else:
            forecast = new_forcast(date)
            # return weather forecast
            return forecast
    # if data not in db but still in the past, return default data
    else: 
        # if data in db return forecast
        db = check_database(date)
        if db == True:
            forecast = get_forecast_from_db(date)
            return forecast
        else:
            forecast = {'date':date, 'temp': 50, 'rain': 1}
            w = Weather_Model.objects.create(date=date, temperature=50, rain=1)
            return forecast

