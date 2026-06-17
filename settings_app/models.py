from django.db import models

# Create your models here.
from django.db import models

class SystemConfig(models.Model):
    use_real_weather = models.BooleanField(default=False, help_text="Switch to real weather API (True) or simulation (False)")
    openweather_api_key = models.CharField(max_length=100, blank=True, default="", help_text="Get from https://openweathermap.org/api")
    
    def __str__(self):
        return f"Real weather: {self.use_real_weather}"
    
    class Meta:
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configurations"