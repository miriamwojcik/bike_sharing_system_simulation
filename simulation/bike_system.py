# Bike class used to model Aberdeen Bike-Sharing System

# class declaration
# the list of stations objects, bikes, and users as parameters in a constructor
class Bike_System:
    def __init__(self, stations: list, bikes: list, users: list):
        self.stations = stations
        self.bikes = bikes
        self.users = users

    # Getters and Setters
    def get_stations(self):
        return self.stations

    def get_bikes(self):
        return self.bikes

    def get_users(self):
        return self.users

    def set_stations(self, stations):
        self.stations = stations

    def set_bikes(self, bikes):
        self.bikes = bikes

    def set_users(self, users):
        self.users = users

    # To string method
    def __str__(self):
        x = ' Bikes: '
        x+= str(self.bikes)
        for bike in self.bikes:
            x+= str(bike.id) + ', '

        x+= ' Users: '
        x+= str(self.users)
        for user in self.users:
            x+= str(user.id) + ', '

        x += 'Stations: '
        x+= str(self.stations)
        for station in self.stations:
            x+= str(station.id) + ', '
        return x