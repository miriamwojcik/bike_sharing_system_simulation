# A method to get the rental and return hourly data for selected station together with holiday, weekend, and weather data

# Import libraries
import pandas as pd
import os
import calendar
import datetime
from datetime import date
import holidays
from generating_data.generate_weather_data import get_weather_forecast
from simulation.models import Trip_Model
import json


#check is it weekday-1 weekend-0
def is_weekend(date):
    year = date.year
    month = date.month
    day = date.day
    if calendar.weekday(year,month,day) in range(5, 6):
        return 1
    else:
        return 0

# Check is the date a bank holiday in UK; use the holidays library
def get_holidays(date):
    date = date
    holiday = -1
    hol = holidays.Scotland()
    if hol.get(date) == None:
        holiday = 0
    else:
        holiday = 1
    return holiday

# Getrain for the date specified
def get_rain(date):
    date = date.date()
    forecast = get_weather_forecast(date)
    rain = int(forecast['rain'])
    return rain

# Get temperature data for the date specified
def get_temp(date):
    date = date.date()
    forecast = get_weather_forecast(date)
    temp = int(forecast['temp'])
    return temp

# Get hour of the day
def get_hour(time):
    hour = time.hour
    return hour

# Get month
def get_month(date):
    month = date.month
    return month

# Get day
def get_day(date):
    day = date.day
    return day


# GET STATION DATA BY STATION ID
def get_station_data(station):
    station = json.dumps(station)
    # Get trips where the starting station was the station parsed
    rentals = Trip_Model.objects.filter(starting_station=station)
    data = []
    # Create dataframe with the rental time and station id
    for rental in rentals:
        data.append(
            {
                'dateTime' : rental.datetime_start,
                'station' : json.loads(rental.starting_station),
                'trip_id' : rental.trip_id
            }
        )
    df_rentals = pd.DataFrame(data)
    # Get trips where the destination station was the station parsed and the time the trip finished
    returns = Trip_Model.objects.filter(destination_station=station).all()
    # Create dataframe with the return time and station id
    data = []
    for ret in returns:
        data.append(
            {
                'dateTime' : ret.datetime_end,
                'station' : json.loads(ret.destination_station),
                'trip_id' : ret.trip_id
            }
        )
    df_returns = pd.DataFrame(data)


    station = json.loads(station)
    # Group rentals by the hour sum up the number of bikes renter within that hour
    df_rent_sum = df_rentals.groupby(pd.Grouper(freq='1H', key='dateTime')).trip_id.count()
    df_rent_hist = pd.DataFrame(df_rent_sum)
    df_rent_hist = df_rent_hist.rename(columns={'trip_id':'rented'})

    # Group returns by the hour sum up the number of bikes returned within that hour
    df_return_sum = df_returns.groupby(pd.Grouper(freq='1H', key='dateTime')).trip_id.count()
    df_return_hist = pd.DataFrame(df_return_sum)
    df_return_hist = df_return_hist.rename(columns={'trip_id':'returned'})
    
    # create station historical summary dataframe by joining return and rentals summary data frames
    df_station_hist = df_rent_hist.join(df_return_hist)
    df_station_hist = df_station_hist.fillna(0)
    
    # set date time data as index
    df_station_hist['dateTime'] = df_station_hist.index

    # get the hour data
    df_station_hist['hour'] = df_station_hist['dateTime'].apply(get_hour)

    # get the number of the month (the demand can vary between different months based on research)
    df_station_hist['month'] = df_station_hist['dateTime'].apply(get_month)

    # get day of the month
    df_station_hist['day'] = df_station_hist['dateTime'].apply(get_day)

    # get weekend data
    df_station_hist['weekend'] = df_station_hist['dateTime'].apply(is_weekend)
    
    # get holiday data
    df_station_hist['holiday'] = df_station_hist['dateTime'].apply(get_holidays)
    

    # get temp 
    df_station_hist['temp'] = df_station_hist['dateTime'].apply(get_temp)

    # get rain
    df_station_hist['rain'] = df_station_hist['dateTime'].apply(get_rain)

    # reset the index
    df_station_hist = df_station_hist.set_index('dateTime', drop=True)


    # # TO SPEED UP development SAVE DATA TO CVS FILE
    #  # write data to the file to speed up development and testing
    # path = 'generating_data/data/hist_station_data_' + station + '.csv'
    # df_station_hist.to_csv(path)
    return df_station_hist
