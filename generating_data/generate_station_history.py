# Method returns the dataframe with the hourly breakdown of bike returs 
# and bike hires for the date and station specified
# (data from database)

# Import modules and libraries
import datetime
from datetime import timedelta
from numpy import piecewise
import pandas as pd
import json

from scipy.linalg.decomp_svd import null_space

# Import methods and classes
from simulation.models import Trip_Model

# Method returns the dataframe with the hourly breakdown of bike returs and bike hires for the date and station specified
def get_last_year_station_data(station, date):

    station_no = int(station)
    date = date.date()

    name_map = {
        'id':'id', 
        'trip_id':'trip_id', 
        'bike':'bike', 
        'user':'user', 
        'starting_station':'starting_station', 
        'destination_station':'destination_station', 
        'datetime_start':'datetime_start', 
        'datetime_end':'datetime_end'
    }

    # convert the station id to json format
    station = json.dumps(station)

    # get the trip data where bikes was rented at the station specified on the specified date
    rentals_str = """SELECT "simulation_trip_model"."id", "simulation_trip_model"."trip_id", "simulation_trip_model"."bike", "simulation_trip_model"."user", "simulation_trip_model"."starting_station", "simulation_trip_model"."destination_station", "simulation_trip_model"."datetime_start", "simulation_trip_model"."datetime_end" FROM "simulation_trip_model" WHERE (("simulation_trip_model"."datetime_start")::date = '""" + str(date) +  """' AND "simulation_trip_model"."starting_station" = '"\\""" + '"' +str(station_no) + """\\""')"""
    rentals = Trip_Model.objects.raw(rentals_str, translations=name_map)
    

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

    returns_str = """SELECT "simulation_trip_model"."id", "simulation_trip_model"."trip_id", "simulation_trip_model"."bike", "simulation_trip_model"."user", "simulation_trip_model"."starting_station", "simulation_trip_model"."destination_station", "simulation_trip_model"."datetime_start", "simulation_trip_model"."datetime_end" FROM "simulation_trip_model" WHERE (("simulation_trip_model"."datetime_end")::date = '""" + str(date) +  """' AND "simulation_trip_model"."destination_station" = '"\\""" + '"' +str(station_no) + """\\""')"""
    returns = Trip_Model.objects.raw(returns_str, translations=name_map)
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
    df_station_hist['dateTime'] = df_station_hist.index
    df_station_hist = df_station_hist.set_index('dateTime')
    df_station_hist['ts'] = df_rent_hist.index
    df_station_hist['ts'] = pd.to_datetime(df_station_hist['ts'])
    hist_station_summary = df_station_hist.to_dict('records')
    # except:
    #     hist_station_summary = []
    #     for i in range(0,23):
    #      row = {'ts':datetime.time(i),'rented':0, 'returned':0}
    #      hist_station_summary.append(row)
    
    return hist_station_summary