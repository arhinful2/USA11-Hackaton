import random
from django.core.management.base import BaseCommand
from predictor.models import GridZone, OutageHistory, CriticalInfrastructure, DemographicData
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Generate synthetic data for hackathon'

    def handle(self, *args, **kwargs):
        # Create 5 grid zones
        zones = [
            {"name": "Northside", "lat": 40.7128, "lon": -74.0060, "age": 15, "pop": 20000},
            {"name": "Southside", "lat": 40.7135, "lon": -74.0055, "age": 8, "pop": 15000},
            {"name": "East End", "lat": 40.7140, "lon": -74.0045, "age": 25, "pop": 8000},
            {"name": "West Park", "lat": 40.7110, "lon": -74.0070, "age": 5, "pop": 12000},
            {"name": "Downtown", "lat": 40.7100, "lon": -74.0080, "age": 30, "pop": 50000},
        ]
        zone_objs = []
        for z in zones:
            zone = GridZone.objects.create(
                name=z["name"], latitude=z["lat"], longitude=z["lon"],
                equipment_age_years=z["age"], population=z["pop"]
            )
            zone_objs.append(zone)

        # Critical infrastructure
        infra = [
            (zone_objs[0], "General Hospital", "hospital", "555-0101"),
            (zone_objs[0], "North Shelter", "shelter", "555-0102"),
            (zone_objs[2], "East Police Dept", "police", "555-0103"),
            (zone_objs[4], "City Emergency Center", "emergency", "555-0104"),
        ]
        for zone, name, itype, phone in infra:
            CriticalInfrastructure.objects.create(zone=zone, name=name, infra_type=itype, phone=phone)

        # Demographics
        for zone in zone_objs:
            DemographicData.objects.create(
                zone=zone,
                poverty_percent=random.uniform(5, 30),
                elderly_percent=random.uniform(8, 25)
            )

        # Outage history (last 100 days simulated)
        start_date = date.today() - timedelta(days=100)
        for i in range(100):
            day = start_date + timedelta(days=i)
            for zone in zone_objs:
                # Simple logic: older equipment + high wind -> more outage
                wind = random.uniform(5, 60)
                rain = random.uniform(0, 20)
                temp = random.uniform(-5, 40)
                age = zone.equipment_age_years
                outage_prob = (wind/100) * 0.6 + (age/40) * 0.4
                outage = 1 if random.random() < outage_prob else 0
                OutageHistory.objects.create(
                    zone=zone,
                    date=day,
                    wind_speed=wind,
                    rainfall=rain,
                    temperature=temp,
                    equipment_age_years=age,
                    outage_occurred=outage
                )
        self.stdout.write(self.style.SUCCESS('Data generated successfully'))