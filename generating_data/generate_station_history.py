# Method returns the dataframe with the hourly breakdown of bike returs 
# and bike hires for the date and station specified
# (data from database)

# Import modules and libraries
import datetime
from datetime import timedelta
import pandas as pd
import json

# Import methods and classes
from simulation.models import Trip_Model

# Method returns the dataframe with the hourly breakdown of bike returs and bike hires for the date and station specified
def get_last_year_station_data(station, date):

    date = date.date()

    # convert the station id to json format
    station = json.dumps(station)

    # get the trip data where bikes was rented at the station specified on the specified date
    rentals = Trip_Model.objects.filter(starting_station=station, datetime_start__date=date).all()


    # print create an array with the query results
    data = []

    # loop over the queries results and get the dateTime, station and trip_id data;
    # append to the array
    for rental in rentals:
        data.append(
            {
                'dateTime' : rental.datetime_start,
                'station' : json.loads(rental.starting_station),
                'trip_id' : rental.trip_id
            }
        )


    # convert the array with hire results to pandas dataframe
    df_rentals = pd.DataFrame(data)

    returns = Trip_Model.objects.filter(destination_station=station, datetime_end__date=date).all()

    # Create dataframe with the return time and station id
    data = []

    # loop over the queries results and get the dateTime, station and trip_id data;
    # append to the array
    for ret in returns:
        data.append(
            {
                'dateTime' : ret.datetime_end,
                'station' : json.loads(ret.destination_station),
                'trip_id' : ret.trip_id
            }
        )

    # convert results for bike returns to pandas dataframe
    df_returns = pd.DataFrame(data)
    print(df_rentals.keys())
    print(df_rentals.dtypes)

    print(df_returns)

    # Group rentals by the hour sum up the number of bikes renter within that hour
    df_rent_sum = df_rentals.groupby(pd.Grouper(freq='1H', key='dateTime')).trip_id.count()

    print(df_rent_sum)
    df_rent_hist = pd.DataFrame(df_rent_sum)
    df_rent_hist = df_rent_hist.rename(columns={'trip_id':'rented'})

    # Group returns by the hour sum up the number of bikes returned within that hour
    df_return_sum = df_returns.groupby(pd.Grouper(freq='1H', key='dateTime')).trip_id.count()
    df_return_hist = pd.DataFrame(df_return_sum)
    df_return_hist = df_return_hist.rename(columns={'trip_id':'returned'})
    
    # create station historical summary dataframe by joining return and rentals summary data frames
    df_station_hist = df_rent_hist.join(df_return_hist)
    df_station_hist = df_station_hist.fillna(0)
    df_station_hist['dateTime'] = df_station_hist.index
    df_station_hist = df_station_hist.set_index('dateTime')
    df_station_hist['ts'] = df_rent_hist.index.time
    hist_station_summary = df_station_hist.to_dict('records')
    return hist_station_summary