import requests
import random
from django.core.management.base import BaseCommand
from predictor.models import GridZone, WeatherData
from settings_app.models import SystemConfig

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        config = SystemConfig.objects.first()
        if not config:
            self.stdout.write(self.style.WARNING('No SystemConfig found. Run admin to set API key.'))
            return
        
        if config.use_real_weather and config.openweather_api_key:
            # Real weather
            api_key = config.openweather_api_key
            for zone in GridZone.objects.all():
                url = f'http://api.openweathermap.org/data/2.5/weather?lat={zone.latitude}&lon={zone.longitude}&appid={api_key}&units=metric'
                try:
                    resp = requests.get(url, timeout=10).json()
                    wind = resp['wind']['speed']
                    rain = resp.get('rain', {}).get('1h', 0)
                    temp = resp['main']['temp']
                    WeatherData.objects.create(zone=zone, wind_speed=wind, rainfall=rain, temperature=temp)
                    self.stdout.write(f'Real weather for {zone.name}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error fetching weather for {zone.name}: {e}'))
        else:
            # Simulation mode
            for zone in GridZone.objects.all():
                wind = random.uniform(0, 30)
                rain = random.uniform(0, 10)
                temp = random.uniform(-5, 35)
                WeatherData.objects.create(zone=zone, wind_speed=wind, rainfall=rain, temperature=temp)
                self.stdout.write(f'Simulated weather for {zone.name}')
        
        self.stdout.write(self.style.SUCCESS('Weather data updated.'))