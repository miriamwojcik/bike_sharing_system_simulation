# BSS_Events class is a collection of simulation Events methods

# Import libraries
import random
import time
from datetime import datetime
import math

# Import openrouteservice
import openrouteservice
from openrouteservice import Client
from openrouteservice.directions import directions

#Import Folium
import folium

# Import classes
from .bike_system import Bike_System
from .bike import Bike
from .station import Station
from .trip import Trip
from .user import User

# Import methods
from .sim_db_methods import update_user, update_station, save_trip, update_bike

# The Bss_Events class contains system operations such as creating new rentals, updating trips, users arriving at the station, returning bikes
# real_time atribute indicates is the simulation run to generate bulk data or is it run in the backgound
# this attribute is important to avoide reaching the daily limit of API calls in OpenRouteService
class Bss_Events:
    def __init__(self, bss, dt, real_time):
        self.bss = bss
        self.dt = dt
        self.real_time = real_time

    # A method returns free user (that is not currently using the system) if available
    def get_free_user(self):
        any_free = False
        for us in self.bss.users:
            if us.is_busy != True:
                any_free = True
                break
        if any_free == True:
            u = self.bss.users[random.randrange(len(self.bss.users))]
            while u.is_busy==True:
                u = self.bss.users[random.randrange(len(self.bss.users))]
        else:
            u = -1
        if u==-1:
            print('No free users')
            return -1
        else:
            return u

    def arrive_at_station(self, user: User, station: Station):
        # user.is_busy attribute controls is the user currently using the system or are they free to rent a new bike
        user = user
        user.is_busy = True
        update_user(user)
        # Check are there any bikes available at the station
        station = station
        bike_available = False
        if len(station.bikes_parked) > 0:
            # If bikes available rent a bike
            t = self.rent_bike(user, station)
            bike_available = True
        else:
            print('No bikes available')
        if bike_available == False:
            # if no bikes available after waiting time, free up the user and finish the process for him
            user.is_busy = False
            update_user(user)
            # global lost_transaction
            # lost_transaction +=1
            return -1
        else:
            return t

    # create a trip with random destination point different than the current station
    # return trip object
    def rent_bike(self, user: User, station: Station):
        # select and remove one of the bikes parked at the station
        bike = station.bikes_parked.pop(random.randrange(len(station.bikes_parked)))
        update_station(station)
        # select random destination different than starting station
        destination = self.bss.stations[random.randrange(len(self.bss.stations))]
        while destination == station:
            destination = self.bss.stations[random.randrange(len(self.bss.stations))]
        t = Trip(bike, user, station, destination, self.dt)
        # global no_of_rents
        # no_of_rents +=  1
        print('User ' + t.user.id + ' rented bike ' + t.bike.id + ' from station no ' + str(t.starting_station.id) + ' ' + str(t.starting_station.location) + ' to station no ' + str(t.destination_station.id) + ' ' + str(t.destination_station.location))
        return t

    # controls the path of the trip and keeps track of the bike's location / process simplified, doesnt take into considaration the fact bike could be stolen or abandoned by the user
    def initialize_trip(self, trip: Trip):

        # Starting station and destination coordinates
        coords = [trip.starting_station.location, trip.destination_station.location]
        # get the route for the trip by getting directions from the station where the bike was rented to the station where the user wants to return the bike
        # / use the profile=cycling option to get a more accurate time and paths that can be used by bikes
        client = openrouteservice.Client(key='5b3ce3597851110001cf6248361bdec0c0b94c0dbcc8c0d4b07fd4f6')
        
        # for the real-time simulation obtain directions from API
        if self.real_time == True:
            path = client.directions(coordinates=coords, format= 'geojson', geometry=True, profile='cycling-regular')
        # for generating a bulk of historical data use sample data (they wont have an impact on the forecast prediction)
        else:
            path = {'type': 'FeatureCollection', 'features': [{'bbox': [-2.1074, 57.132795, -2.082808, 57.155872], 'type': 'Feature', 'properties': {'segments': [{'distance': 4293.4, 'duration': 921.1, 'steps': [{'distance': 114.4, 'duration': 22.9, 'type': 11, 'instruction': 'Head southwest on Fraser Place', 'name': 'Fraser Place', 'way_points': [0, 5]}, {'distance': 650.7, 'duration': 130.1, 'type': 0, 'instruction': 'Turn left onto George Street, C156C', 'name': 'George Street, C156C', 'way_points': [5, 20]}, {'distance': 383.6, 'duration': 76.7, 'type': 1, 'instruction': 'Turn right onto St Andrew Street', 'name': 'St Andrew Street', 'way_points': [20, 31]}, {'distance': 72.1, 'duration': 14.4, 'type': 1, 'instruction': 'Turn right onto Rosemount Viaduct', 'name': 'Rosemount Viaduct', 'way_points': [31, 36]}, {'distance': 71.2, 'duration': 14.2, 'type': 0, 'instruction': 'Turn left onto B983', 'name': 'B983', 'way_points': [36, 39]}, {'distance': 241.6, 'duration': 48.3, 'type': 4, 'instruction': 'Turn slight left onto Union Terrace, B983', 'name': 'Union Terrace, B983', 'way_points': [39, 44]}, {'distance': 120.9, 'duration': 24.2, 'type': 1, 'instruction': 'Turn right onto Union Street, A9013', 'name': 'Union Street, A9013', 'way_points': [44, 48]}, {'distance': 824.0, 'duration': 164.8, 'type': 0, 'instruction': 'Turn left onto Crown Street', 'name': 'Crown Street', 'way_points': [48, 76]}, {'distance': 127.2, 'duration': 25.4, 'type': 0, 'instruction': 'Turn left onto Bank Street', 'name': 'Bank Street', 'way_points': [76, 77]}, {'distance': 235.6, 'duration': 47.5, 'type': 1, 'instruction': 'Turn right onto Prospect Terrace', 'name': 'Prospect Terrace', 'way_points': [77, 82]}, {'distance': 104.5, 'duration': 20.9, 'type': 0, 'instruction': 'Turn left onto Wellington Brae', 'name': 'Wellington Brae', 'way_points': [82, 87]}, {'distance': 25.4, 'duration': 9.3, 'type': 5, 'instruction': 'Turn slight right', 'name': '-', 'way_points': [87, 89]}, {'distance': 144.6, 'duration': 86.7, 'type': 6, 'instruction': 'Continue straight', 'name': '-', 'way_points': [89, 95]}, {'distance': 38.4, 'duration': 7.7, 'type': 0, 'instruction': 'Turn left', 'name': '-', 'way_points': [95, 98]}, {'distance': 12.1, 'duration': 2.4, 'type': 5, 'instruction': 'Turn slight right', 'name': '-', 'way_points': [98, 99]}, {'distance': 15.5, 'duration': 3.1, 'type': 1, 'instruction': 'Turn right onto Wellington Road, A956', 'name': 'Wellington Road, A956', 'way_points': [99, 101]}, {'distance': 276.3, 'duration': 55.3, 'type': 7, 'instruction': 'Enter the roundabout and take the 3rd exit onto Wellington Road, A956', 'name': 'Wellington Road, A956', 'exit_number': 3, 'way_points': [101, 122]}, {'distance': 630.1, 'duration': 126.0, 'type': 0, 'instruction': 'Turn left onto Grampian Place', 'name': 'Grampian Place', 'way_points': [122, 144]}, {'distance': 61.2, 'duration': 12.2, 'type': 4, 'instruction': 'Turn slight left onto Tullos Circle', 'name': 'Tullos Circle', 'way_points': [144, 149]}, {'distance': 73.9, 'duration': 14.8, 'type': 1, 'instruction': 'Turn right onto Tullos Place', 'name': 'Tullos Place', 'way_points': [149, 150]}, {'distance': 69.9, 'duration': 14.0, 'type': 1, 'instruction': 'Turn right onto South Grampian Circle', 'name': 'South Grampian Circle', 'way_points': [150, 156]}, {'distance': 0.0, 'duration': 0.0, 'type': 10, 'instruction': 'Arrive at South Grampian Circle, on the left', 'name': '-', 'way_points': [156, 156]}]}], 'summary': {'distance': 4293.4, 'duration': 921.1}, 'way_points': [0, 156]}, 'geometry': {'coordinates': [[-2.10588, 57.155872], [-2.106054, 57.155744], [-2.106098, 57.15572], [-2.106255, 57.155654], [-2.106691, 57.155511], [-2.1074, 57.155273], [-2.107365, 57.155241], [-2.106893, 57.154818], [-2.10648, 57.154458], [-2.105987, 57.154021], [-2.105848, 57.153897], [-2.105692, 57.153762], [-2.105308, 57.153422], [-2.104526, 57.152726], [-2.104262, 57.152499], [-2.104146, 57.152401], [-2.104026, 57.152285], [-2.103724, 57.151989], [-2.102738, 57.151147], [-2.101818, 57.150392], [-2.101709, 57.150303], [-2.101864, 57.150247], [-2.103075, 57.14981], [-2.104143, 57.149611], [-2.104281, 57.149571], [-2.104303, 57.149553], [-2.104316, 57.149531], [-2.104319, 57.149512], [-2.104306, 57.149473], [-2.103378, 57.147979], [-2.103341, 57.147885], [-2.103331, 57.1478], [-2.103347, 57.147799], [-2.103544, 57.147793], [-2.104221, 57.147771], [-2.104302, 57.14777], [-2.104524, 57.147766], [-2.10463, 57.147651], [-2.104965, 57.147294], [-2.10497, 57.147182], [-2.104256, 57.146762], [-2.103631, 57.146403], [-2.102562, 57.145826], [-2.102389, 57.145721], [-2.102254, 57.145592], [-2.102493, 57.145526], [-2.103142, 57.145345], [-2.103775, 57.145168], [-2.104036, 57.145095], [-2.103983, 57.14504], [-2.103929, 57.144985], [-2.103777, 57.144822], [-2.103349, 57.14439], [-2.103089, 57.144274], [-2.10277, 57.14411], [-2.102494, 57.143875], [-2.10233, 57.143646], [-2.102127, 57.143301], [-2.101756, 57.142647], [-2.101566, 57.142321], [-2.101562, 57.142314], [-2.101453, 57.142124], [-2.101117, 57.141498], [-2.101095, 57.141444], [-2.101056, 57.141339], [-2.10098, 57.141144], [-2.100945, 57.14105], [-2.100932, 57.141018], [-2.100894, 57.140906], [-2.100784, 57.140581], [-2.100753, 57.140459], [-2.100717, 57.139913], [-2.10069, 57.1397], [-2.100835, 57.13929], [-2.100909, 57.139168], [-2.100977, 57.139052], [-2.10096, 57.138117], [-2.098854, 57.138174], [-2.098886, 57.136984], [-2.098887, 57.136969], [-2.098908, 57.136187], [-2.098906, 57.136103], [-2.0989, 57.136055], [-2.0987, 57.136012], [-2.097927, 57.135803], [-2.097718, 57.13577], [-2.09738, 57.135752], [-2.097284, 57.135747], [-2.097189, 57.135692], [-2.096956, 57.135605], [-2.096838, 57.135575], [-2.096653, 57.135552], [-2.096517, 57.135555], [-2.094957, 57.135584], [-2.094637, 57.135594], [-2.094579, 57.135597], [-2.094439, 57.135758], [-2.094546, 57.13586], [-2.094539, 57.135909], [-2.094419, 57.135997], [-2.094305, 57.135972], [-2.094173, 57.135961], [-2.094092, 57.135986], [-2.094002, 57.135996], [-2.093911, 57.13599], [-2.093834, 57.135973], [-2.09372, 57.135908], [-2.093693, 57.135865], [-2.093688, 57.135819], [-2.093706, 57.135775], [-2.093747, 57.135735], [-2.093797, 57.135664], [-2.093834, 57.135573], [-2.093823, 57.135527], [-2.093663, 57.13529], [-2.093633, 57.135217], [-2.093625, 57.135159], [-2.093625, 57.135041], [-2.09366, 57.134933], [-2.09381, 57.134727], [-2.093975, 57.134474], [-2.094153, 57.134167], [-2.094384, 57.133813], [-2.094301, 57.133741], [-2.094236, 57.133716], [-2.094123, 57.1337], [-2.092853, 57.133532], [-2.092534, 57.133505], [-2.092244, 57.13353], [-2.091757, 57.133622], [-2.091363, 57.13374], [-2.090923, 57.133895], [-2.090807, 57.133903], [-2.090611, 57.13389], [-2.090429, 57.133856], [-2.089118, 57.133599], [-2.088855, 57.133585], [-2.086595, 57.133513], [-2.086177, 57.133507], [-2.085362, 57.133496], [-2.085352, 57.133425], [-2.085292, 57.133316], [-2.085172, 57.133229], [-2.084986, 57.133158], [-2.084754, 57.133117], [-2.084552, 57.133131], [-2.084388, 57.13316], [-2.084203, 57.13324], [-2.084089, 57.133326], [-2.084022, 57.133432], [-2.082808, 57.133348], [-2.082846, 57.133258], [-2.082915, 57.133142], [-2.083009, 57.13304], [-2.083044, 57.133002], [-2.083197, 57.132868], [-2.083325, 57.132795]], 'type': 'LineString'}}], 'bbox': [-2.1074, 57.132795, -2.082808, 57.155872], 'metadata': {'attribution': 'openrouteservice.org | OpenStreetMap contributors', 'service': 'routing', 'timestamp': 1614751041236, 'query': {'coordinates': [[-2.105803049059682, 57.15584072167345], [-2.0828320755185894, 57.1325414074971]], 'profile': 'cycling-regular', 'format': 'geojson', 'geometry': True}, 'engine': {'version': '6.3.6', 'build_date': '2021-02-21T01:31:06Z', 'graph_date': '1970-01-01T00:00:00Z'}}}

        # an array of coordinates along the trip's route returned / by the OpenRouteService API
        geo = path['features'][0]['geometry']['coordinates']

        # geopoint 
        gp = []

        # loop over the array of route coordinates and reverse the lon and lat (ORS and Leaflet use reversed formats)
        for i in geo:
            i = list(reversed(i))
            gp.append(i)

        # duration of the trip based on the data returned by API. API returns value in seconds. Round the value returned and set trips duration to a rounded value
        duration = (path['features'][0]['properties']['summary']['duration'])
        duration = round(duration, 2)
        trip.set_trip_duration(duration)

        # trip stage is used to collect information about different parts of journey in case there is no bike available at the original docking station and an alternative destination is generated
        # otherwise the data would be overwritten and lost
        trip.add_trip_stage(duration)

        # obtain a number of coordinates along the path to emulate bike's movement
        # the data returned by the API dont allow to establish how long exactly it takes to move from one coordinate to another
        # screen to be updated every 10 sec so divide the duration by 10 sec and ---> speed
        # divide the number of coordinates by duration/10 to emulate an estimated real time movement of a bike
        speed = len(gp)//(duration/10)
        speed = int(math.floor(speed))
        trip_steps = []
        i = 0
        while i <len(gp):
            trip_steps.append(gp[i])
            i+=speed
        trip_steps.append(gp[-1])
        trip.current_step = 0
        trip.trip_steps = trip_steps

    # Different scenatios are possible once the user reaches the destination:
    # 1) there might be a free docking slot, in which case they can park the bike and finish their journey
    # 2) there is no docking slot, so user needs to go to a different station (random -> in the future could check for the closes docking station)
    def arrive_at_destination(self, t: Trip):
        if self.docking_slots_availability(t) == True:
            self.return_bike(t)
        else:
            current_dest = t.destination_station
            new_dest = self.bss.stations[random.randrange(len(self.bss.stations))]
            while new_dest == current_dest:
                new_dest = self.bss.stations[random.randrange(len(self.bss.stations))]
            t.starting_station = current_dest
            t.destination_station = new_dest
            self.initialize_trip(t)
            print('The destination changed')
            print('New destination: '+ new_dest.id + ' ' + str(new_dest.location))


    # a method to check are there any docking slots available at the destination station
    def docking_slots_availability(self, trip: Trip):
        docs_available = trip.destination_station.get_docs_available()
        if docs_available==0:
            # wait for a while, check again, if no, go to another station-> should be the nearest but can be simplified to random
            return False
        else:
            print('Park the bike')
            return True

    # a function used to return the bike at the parking station
    # add the bike to the parking station list of bikes parked there
    # free up the user
    # update user data in the database
    # save the trip in the db
    def return_bike(self, trip: Trip):
        trip.destination_station.park_bike(trip.bike)
        trip.set_trip_datetime_end()
        update_station(trip.destination_station)
        trip.user.is_busy = False
        update_user(trip.user)
        print('Bike ' + str(trip.bike.id) + ' returned ' + 'by user ' + str(trip.user.id) + ' at station: ' + str(trip.destination_station.id))
        trip.trip_finished = True
        save_trip(trip)

    # create new trip method
    # check are there any free users
    # if possible get a user that is currently not using the system
    # initialize new trip or abandon
    def create_trip(self):
        try:
            user = self.get_free_user()
            if(user != -1):
                t = self.arrive_at_station(self.get_free_user(), self.bss.stations[random.randrange(len(self.bss.stations))])
                
                if t!= -1:
                    self.initialize_trip(t)
                else:
                    t=-1
            else:
                t = -1
        except:
            t=-1
        return t

    # a method to update the trip
    # move the bike along the path
    # check did the user arrive at the destination
    def update_trip(self, trip: Trip):
        trip.current_step += 1
        bl = trip.trip_steps[(trip.current_step-1)]
        trip.bike.set_bike_location(bl)
        update_bike(trip.bike)
        print('Bike ' + str(trip.bike.id) + ' moved to:' + str(trip.bike.location))
        if trip.current_step == (len(trip.trip_steps)-1):
            self.arrive_at_destination(trip)
