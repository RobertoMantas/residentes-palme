"""
Configuración de URLs del frontend para el Sistema de Gestión de Residentes de Palme
"""
from django.urls import path
from . import frontend_views

app_name = 'residentes_frontend'

urlpatterns = [
    # Dashboard principal
    path('', frontend_views.dashboard, name='dashboard'),
    
    # Gestión de residentes
    path('subir-residente/', frontend_views.subir_residente, name='subir_residente'),
    path('buscar-residentes/', frontend_views.buscar_residentes, name='buscar_residentes'),
    path('ver-detalles-residente/<uuid:residente_id>/', frontend_views.ver_detalles_residente, name='ver_detalles_residente'),
    path('eliminar-residente/<uuid:residente_id>/', frontend_views.eliminar_residente, name='eliminar_residente'),
    
    # Gestión de infraestructura
    path('gestionar-edificios/', frontend_views.gestionar_edificios, name='gestionar_edificios'),
    path('gestionar-apartamentos/', frontend_views.gestionar_apartamentos, name='gestionar_apartamentos'),
    
    # APIs AJAX para el frontend
    path('api/crear-residente/', frontend_views.api_crear_residente_ajax, name='api_crear_residente'),
    path('api/buscar-residentes/', frontend_views.api_buscar_residentes_ajax, name='api_buscar_residentes'),
]
