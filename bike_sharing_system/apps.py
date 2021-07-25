# This code is authomatically executed when the server starts running

from django.apps import AppConfig
import threading
class AppNameConfig(AppConfig):
    name = 'bike_sharing_system'

    # def ready(self):

    #     from simulation.bg_sim import SimThread
    #     x = threading.Thread(target = SimThread.run, args=(1,), daemon=True)
    #     x.start()



        # # SCRIPTS USED FOR TESTING

        # from generating_data.generate_initial_data import initialize_stations_and_bikes
        # from generating_data.generate_initial_data import initialize_users
        # from simulation.sim_db_methods import clear_stations, clear_bikes, clear_users


        # # # CLEAR AND RE_INITIALIZE DATA
        # clear_bikes()
        # clear_stations()
        # clear_users()
    
        # initialize_stations_and_bikes()

        # # # Create users

        # initialize_users(250)


        # clear trips (CAREFUL!)
         # from simulation.sim_db_methods import clear_trips
        # clear_trips()

        # # # GENERATE HISTORICAL TRIPS DATA FROM SIMULATION
        # import datetime
        # from generating_data.generate_historical_trips import simulate_past_trips
        # # starts date
        # start_date = datetime.datetime(2020, 4, 8)
        # # number of dates the data should be generated for
        # num_days = 365
        # # generate data
        # simulate_past_trips(start_date, num_days)

    #     # # GENERATE HISTORICAL TRIPS DATA
           
    #     # import datetime
    #     # from generating_data.generate_historical_trips import generate_past_trips
    #     # # starts date
    #     # start_date = datetime.datetime(2020, 4, 11)

    #     # # number of dates the data should be generated for
    #     # num_days = 364

    #     # # generate data
    #     # generate_past_trips(start_date, num_days)



    #     # DELETE TRIP DATA FOR SELECTED DATE 
    
    #     # import datetime
    #     # from simulation.sim_db_methods import delete_trips_date
    #     # today= datetime.datetime.now()
    #     # y = today.year
    #     # m = today.month
    #     # d = today.day
    #     # dt = datetime.datetime(y, m, d)
    #     # delete_trips_date(dt)


    # # GET HISTORICAL WEATHER
        # from generating_data.generate_weather_data import get_historical_weather
        # import datetime
        # from datetime import timedelta

        # get_historical_weather()

        # start_date = datetime.datetime(2020, 4, 8)

        # # # number of dates the data should be generated for
        # num_days = 366
        # date = start_date.date()
        # delta_out = timedelta(days=num_days)
        # delta = timedelta(days=1)
        # last_day = date+delta_out
        # while date<last_day:
        #     forecast = get_historical_weather(date)
        #     date = date+delta


    # # # GET Station DATA FOR DEMAND FORECAST
    #     from generating_data.demand_forecast_data_prep import get_station_data
    #     print('Generating historical data')
    #     for i in range(1,31):
    #         station = str(i)
    #         get_station_data(station)
    #         print('Data for station ' + station + ' saved')
    #     print('Completed')


    # Generate models
        # from demand_forecast.calculate_forecast import calculate_demand_forecast
        # import datetime
        # date = datetime.datetime(year=2021, month=4, day=15)
        # for i in range(1,31):
        #     station = str(i)
        #     calculate_demand_forecast(station, date)
        #     print('Data for station ' + station + ' saved')


    # GENERATE HISTORICAL DATA FOR FORECAST 
        # from demand_forecast.calculate_forecast import calculate_demand_forecast
        # import datetime

        # for i in range(1,31):
        #     station = str(i)
        #     get_station_data(station)
        #     print('Data for station ' + station + ' saved')


    # GET FORECAST FOR ALL STATIONS FOR SPECIFIC DATE
        # from demand_forecast.calculate_forecast import calculate_demand_forecast
        # import datetime
        # date = datetime.datetime(year=2021, month=4, day=27)
        # for i in range(1,2):
        #     station = str(i)
        #     print('Calculating forecast for station ' + station)
        #     calculate_demand_forecast(station, date)


    # GET OPTIMIZED ALLOCATION
        # from optimization.optimizing_resource_allocation import optimize_resource_allocation
        # import datetime
        # date = datetime.datetime(year=2021, month=4, day=17)
        # optimize_resource_allocation(date)


        # date = datetime.datetime(year=2021, month=4, day=15)
        # calculate_demand_forecast('15', date)


    # # RUN THE VEHICLE OPTIMIZATION
    #     from optimization.vehicle_routing import optimize_truck_route

    #     optimize_truck_route()

    # GENERATE STATION HISTORY
        # from generating_data.generate_station_history import get_last_year_station_data
        # import datetime
        # date = datetime.datetime(year=2020, month=4, day=15)
        # get_last_year_station_data('15', date)


    # # # #    