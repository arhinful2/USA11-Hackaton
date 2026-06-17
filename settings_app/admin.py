from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import SystemConfig

@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'use_real_weather', 'openweather_api_key')