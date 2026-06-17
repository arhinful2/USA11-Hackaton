import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from django.core.management.base import BaseCommand
from predictor.models import OutageHistory

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Load data from DB
        qs = OutageHistory.objects.all().values(
            'wind_speed', 'rainfall', 'temperature', 'equipment_age_years', 'outage_occurred'
        )
        df = pd.DataFrame(qs)
        if df.empty:
            self.stdout.write(self.style.ERROR('No outage history found. Run generate_data first.'))
            return
        X = df[['wind_speed', 'rainfall', 'temperature', 'equipment_age_years']]
        y = df['outage_occurred']
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        joblib.dump(model, 'outage_model.pkl')
        self.stdout.write(self.style.SUCCESS('Model saved as outage_model.pkl'))