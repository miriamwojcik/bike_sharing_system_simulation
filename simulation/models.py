
from django.db import models
import jsonfield
from django.contrib.postgres.fields import JSONField

class User_Model(models.Model):
    user_id = models.CharField(max_length=100, unique=True)
    is_busy = models.BooleanField()

class Bike_Model(models.Model):
    bike_id = models.CharField(max_length=100, unique=True)
    bike_location = models.JSONField()


class Station_Model(models.Model):
    station_id = models.CharField(max_length=100, unique=True)
    station_location = models.JSONField()
    station_demand = models.IntegerField(null=True)
    station_capacity = models.SmallIntegerField()
    minimum_bikes = models.PositiveIntegerField(null=True)
    docs_available = models.SmallIntegerField(null=True)
    bikes_parked = models.JSONField(null=True)


class Trip_Model(models.Model):
    trip_id = models.CharField(max_length=100, unique=True)
    bike = models.JSONField(null=True)
    user = models.JSONField(null=True)
    starting_station = models.JSONField(null=True)
    destination_station = models.JSONField(null=True)
    datetime_start = models.DateTimeField(null=True)
    datetime_end = models.DateTimeField(null=True)

