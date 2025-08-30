"""
Configuración de URLs para la API del Sistema de Gestión de Residentes de Palme
"""
from django.urls import path
from . import views

app_name = 'residentes_api'

urlpatterns = [
    # Endpoints para edificios
    path('edificios/', views.EdificioAPIView.as_view(), name='edificios'),
    
    # Endpoints para apartamentos
    path('apartamentos/', views.ApartamentoAPIView.as_view(), name='apartamentos'),
    
    # Endpoints para residentes
    path('residentes/', views.ResidenteAPIView.as_view(), name='residentes'),
    path('residentes/<uuid:residente_id>/', views.ResidenteDetailAPIView.as_view(), name='residente_detail'),
    
    # Endpoint para estadísticas
    path('estadisticas/', views.estadisticas_api, name='estadisticas'),
]
