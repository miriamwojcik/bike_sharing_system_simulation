
# Import libraries and packages
import numpy as np
import random
import json
from shapely.geometry import Polygon, Point, asShape

# import station and bike class
from simulation.bike import Bike
from simulation.station import Station
from simulation.user import User

# import methods to save data in the database
from simulation.sim_db_methods import save_bikes
from simulation.sim_db_methods import save_users
from simulation.sim_db_methods import save_stations
from simulation.sim_db_methods import clear_users
from simulation.sim_db_methods import clear_stations
from simulation.sim_db_methods import clear_bikes



# A method to initialize stations and bikes (initial setup)
def initialize_stations_and_bikes():

    # clear old data if exist
    try:
        clear_stations()
        clear_bikes()
    except:
        pass

    # GENERATE STATIONS LOCATION DATA
    # 2 stations per voting ward in Aberdeen City; 3 stations in 4 most populated wards
    # population estimates from https://www.citypopulation.de/en/uk/scotland/wards/

    # read the wards data from the file source: https://public.opendatasoft.com/explore/dataset/wards-in-scotland-december-2016/table/?q=aberdeen+city
    with open('generating_data/data/wards-aberdeen.json', 'r') as myfile:
        shapefile=myfile.read()
    json_data = json.loads(shapefile)
    wards = []

    # from the wards data create a list with a ward name and boundries geodata
    for ward in json_data:
        field = ward['fields']
        ward_name = field['wd16nm']
        # for some reason data for these two wards have a different format
        if (ward_name == 'Torry/Ferryhill' or ward_name=='Kincorth/Nigg/Cove'):
            polygon = field['geo_shape']['coordinates'][0][0]
        else:
            polygon = field['geo_shape']['coordinates'][0]
        coords = []
        # convert coordinates to tuple as this is a format used to create Polygons by shapely
        for coord in polygon:
            c = tuple(coord)
            coords.append(c)
        wards.append([ward_name, coords])

    # a method that returns two random points within a polygon
    # https://stackoverflow.com/questions/55392019/get-random-points-within-polygon-corners
    def random_points_within(poly, num_points):
        min_x, min_y, max_x, max_y = poly.bounds
        
        points = []

        while len(points) < num_points:
            random_point = Point([random.uniform(min_x, max_x), random.uniform(min_y, max_y)])
            if (random_point.within(poly)):
                points.append([random_point.x, random_point.y])
        return points

    # FROM THE BOUNDRIES OF EACH WARD SELECT 2 or 3 RANDOM POINTS FOR THE DOCKING STATION LOCATION
    # generate more stations for the most populated wards https://www.citypopulation.de/en/uk/scotland/wards/
    stations_coords = []
    for ward in wards:
        poly = Polygon(ward[1])
        if(ward[0] == 'George St/Harbour' or ward[0] == 'Dyce/Bucksburn/Danestone' or ward[0] =='Torry/Ferryhill' or ward[0] =='Hazlehead/Ashley/Queens Cross'):
            station = random_points_within(poly, 3)
            stations_coords.append(station[0])
            stations_coords.append(station[1])
            stations_coords.append(station[2])
        else:
            station = random_points_within(poly, 2)
            stations_coords.append(station[0])
            stations_coords.append(station[1])

    # GENERATE BIKES DATA 12 bikes per station: 12*30=360 bikes
    # Create bike objects and stations using bike data and location / set station capacity to 15 / set demand to 12 as initial value / variable to store bike id data
    bike_id = 1
    station_id = 1
    stations=[]
    for location in stations_coords:
        bikes = []
        for i in range(0,12):
            bike = Bike(str(bike_id), location)
            bike_id+=1
            bikes.append(bike)
        save_bikes(bikes)
        station = Station(station_id, location, 12, 15, bikes)
        # set minimum number of bikes at the end of the day to 1
        station.set_minimum_bikes(1)
        station_id+=1
        stations.append(station)

    # SAVE DATA IN THE DATABASE
    save_stations(stations)



# A METHOD TO INITIALIZE USERS
# takes number of users to be created as parameter
def initialize_users(users_number):
    # clear old data if exist
    try:
        clear_users()
    except:
        pass
    users = []
    for i in range(1, (users_number+1)):
        user = User(str(i))
        users.append(user)
    save_users(users)

