import json
import joblib
import os
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from predictor.models import GridZone, WeatherData, CriticalInfrastructure, DemographicData

# Try to load model, but don't crash if missing
MODEL_PATH = os.path.join(settings.BASE_DIR, 'outage_model.pkl')
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    model = None
    print("Warning: outage_model.pkl not found. Run 'python manage.py train_model'")

def home(request):
    return render(request, 'predictor/home.html')


def debug_status(request):
    import os
    from django.conf import settings
    from predictor.models import GridZone, WeatherData
    import joblib
    model_path = os.path.join(settings.BASE_DIR, 'outage_model.pkl')
    model_exists = os.path.exists(model_path)
    zone_count = GridZone.objects.count()
    weather_count = WeatherData.objects.count()
    model_loaded = False
    if model_exists:
        try:
            model = joblib.load(model_path)
            model_loaded = True
        except:
            pass
    return JsonResponse({
        'model_file_exists': model_exists,
        'model_loaded_successfully': model_loaded,
        'grid_zones_count': zone_count,
        'weather_records_count': weather_count,
        'model_path': model_path,
        'base_dir': str(settings.BASE_DIR)
    })

def risk_map_data(request):
    zones_data = []
    for zone in GridZone.objects.all():
        weather = WeatherData.objects.filter(zone=zone).order_by('-timestamp').first()
        if weather:
            features = [[weather.wind_speed, weather.rainfall, weather.temperature, zone.equipment_age_years]]
        else:
            # fallback features
            features = [[10, 0, 20, zone.equipment_age_years]]
        
        if model:
            prob = model.predict_proba(features)[0][1]
        else:
            prob = 0.5
        
        # Get demographics
        try:
            demo = DemographicData.objects.get(zone=zone)
            vulnerability = (demo.poverty_percent + demo.elderly_percent) / 100
        except DemographicData.DoesNotExist:
            vulnerability = 0.2
        
        priority_score = prob * vulnerability
        
        infra_list = [{"name": i.name, "type": i.infra_type, "phone": i.phone} 
                      for i in zone.criticalinfrastructure_set.all()]
        
        zones_data.append({
            'id': zone.id,
            'name': zone.name,
            'lat': zone.latitude,
            'lon': zone.longitude,
            'risk': round(prob, 2),
            'priority': round(priority_score, 3),
            'infrastructure': infra_list
        })
    return JsonResponse({'zones': zones_data})

def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_msg = data.get('message', '').lower()
            
            # If no zones in DB, return helpful message
            if GridZone.objects.count() == 0:
                return JsonResponse({'reply': "⚠️ No data yet. Please run 'python manage.py generate_data' first."})
            
            # Check if model exists
            if not model:
                return JsonResponse({'reply': "⚠️ AI model not trained. Run 'python manage.py train_model'."})
            
            # Simple intent matching
            if any(word in user_msg for word in ['outage', 'power', 'electricity', 'blackout']):
                # Find highest risk zone
                highest_risk = 0
                highest_zone = None
                for zone in GridZone.objects.all():
                    weather = WeatherData.objects.filter(zone=zone).order_by('-timestamp').first()
                    if weather:
                        features = [[weather.wind_speed, weather.rainfall, weather.temperature, zone.equipment_age_years]]
                        prob = model.predict_proba(features)[0][1]
                        if prob > highest_risk:
                            highest_risk = prob
                            highest_zone = zone
                if highest_zone:
                    reply = f"⚠️ Highest outage risk: {highest_zone.name} with {highest_risk*100:.1f}% probability. Factors: wind, equipment age."
                else:
                    reply = "Could not calculate risk. Ensure weather data exists."
            
            elif any(word in user_msg for word in ['shelter', 'help', 'resource', 'food']):
                shelter = CriticalInfrastructure.objects.filter(infra_type='shelter').first()
                if shelter:
                    reply = f"🏥 {shelter.name} – Call {shelter.phone}. Check map for more resources."
                else:
                    reply = "No shelter data. Add via admin panel (CriticalInfrastructure)."
            
            elif 'risk' in user_msg or 'probability' in user_msg:
                total = 0
                count = 0
                for zone in GridZone.objects.all():
                    weather = WeatherData.objects.filter(zone=zone).order_by('-timestamp').first()
                    if weather:
                        features = [[weather.wind_speed, weather.rainfall, weather.temperature, zone.equipment_age_years]]
                        prob = model.predict_proba(features)[0][1]
                        total += prob
                        count += 1
                avg = (total/count)*100 if count else 0
                reply = f"📊 Average outage risk across all zones: {avg:.1f}%. Red zones >70%."
            
            elif 'prepare' in user_msg:
                reply = "🔧 Prepare: flashlights, backup power, charge devices. Check map for nearest shelter."
            
            else:
                reply = "🤖 Ask about 'outage risk', 'shelter', or 'how to prepare'."
            
            return JsonResponse({'reply': reply})
        
        except Exception as e:
            return JsonResponse({'reply': f"Error: {str(e)}. Check console for details."})
    
    return JsonResponse({'error': 'POST only'})