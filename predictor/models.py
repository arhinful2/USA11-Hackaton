from django.db import models

from django.db import models

class GridZone(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    equipment_age_years = models.FloatField(default=10.0)
    population = models.IntegerField(default=5000)

    def __str__(self):
        return self.name

class WeatherData(models.Model):
    zone = models.ForeignKey(GridZone, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    wind_speed = models.FloatField()
    rainfall = models.FloatField()
    temperature = models.FloatField()

class OutageHistory(models.Model):
    zone = models.ForeignKey(GridZone, on_delete=models.CASCADE)
    date = models.DateField()
    wind_speed = models.FloatField()
    rainfall = models.FloatField()
    temperature = models.FloatField()
    equipment_age_years = models.FloatField()
    outage_occurred = models.BooleanField()  # 1 = outage, 0 = no outage

class CriticalInfrastructure(models.Model):
    zone = models.ForeignKey(GridZone, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    infra_type = models.CharField(max_length=50)  # hospital, shelter, police, etc.
    phone = models.CharField(max_length=20, blank=True)

class DemographicData(models.Model):
    zone = models.OneToOneField(GridZone, on_delete=models.CASCADE)
    poverty_percent = models.FloatField(default=10.0)
    elderly_percent = models.FloatField(default=15.0)