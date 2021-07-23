# Distance Matrix Class
# Contains the matrix of distances between the docking stations
#distance_matrix data obtained from the openrouteservice API distance_matrix module

# import the library
import openrouteservice
from openrouteservice import convert, Client
from openrouteservice.distance_matrix import distance_matrix

# Create Distance_Matrix class
# Pass the list of coordinates in a constructor
class Distance_Matrix:
    def __init__(self, coordinates):
        self.coordinates = coordinates
        self.distance_matrix = []

    # get the distance matrix for distances between all stations from the openrouteservice API
    def get_distance_matrix(self):
        try:
            client = openrouteservice.Client(key='5b3ce3597851110001cf6248aa422718516246e08bf63377485a1e13')
            dm = distance_matrix(client, locations=self.coordinates, units='m', metrics=['distance'])
            distances = dm['distances']
            for i in range (len(distances)):
                for e in range(len(distances[i])):
                    x = int(distances[i][e])
                    distances[i][e] = x
            return distances
        except:
            print('dm failed')