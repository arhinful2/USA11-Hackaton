from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import GridZone, WeatherData, OutageHistory, CriticalInfrastructure, DemographicData

@admin.register(GridZone)
class GridZoneAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'latitude', 'longitude', 'equipment_age_years', 'population')
    list_filter = ('equipment_age_years',)
    search_fields = ('name',)

@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'zone', 'timestamp', 'wind_speed', 'rainfall', 'temperature')
    list_filter = ('zone', 'timestamp')
    date_hierarchy = 'timestamp'

@admin.register(OutageHistory)
class OutageHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'zone', 'date', 'outage_occurred', 'wind_speed', 'rainfall')
    list_filter = ('zone', 'outage_occurred', 'date')
    date_hierarchy = 'date'

@admin.register(CriticalInfrastructure)
class CriticalInfrastructureAdmin(admin.ModelAdmin):
    list_display = ('id', 'zone', 'name', 'infra_type', 'phone')
    list_filter = ('zone', 'infra_type')
    search_fields = ('name',)

@admin.register(DemographicData)
class DemographicDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'zone', 'poverty_percent', 'elderly_percent')
    list_filter = ('zone',)