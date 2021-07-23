from django.db import models

class Weather_Model(models.Model):
    date = models.DateField(null=False)
    temperature = models.FloatField(null=False)
    rain = models.BooleanField()
