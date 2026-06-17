from django.contrib import admin
from django.urls import path
from predictor import views
from predictor.views import debug_status
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('risk-map-data/', views.risk_map_data, name='risk_data'),
    path('chatbot-api/', views.chatbot_api, name='chatbot'),
    path('debug/', debug_status),
]