"""
Configuración del admin de Django para el sistema de gestión de residentes
Proporciona una interfaz administrativa completa y funcional
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Edificio, Apartamento, Residente


@admin.register(Edificio)
class EdificioAdmin(admin.ModelAdmin):
    """Admin para el modelo Edificio"""
    list_display = ['numero', 'total_apartamentos', 'total_residentes', 'total_propietarios', 'created_at']
    list_filter = ['created_at']
    search_fields = ['numero']
    ordering = ['numero']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_apartamentos(self, obj):
        """Total de apartamentos en el edificio"""
        return obj.apartamentos.count()
    total_apartamentos.short_description = 'Total Apartamentos'
    
    def total_residentes(self, obj):
        """Total de residentes en el edificio"""
        return sum(apt.residentes.count() for apt in obj.apartamentos.all())
    total_residentes.short_description = 'Total Residentes'
    
    def total_propietarios(self, obj):
        """Total de propietarios en el edificio"""
        return sum(apt.residentes.filter(tipo='propietario').count() for apt in obj.apartamentos.all())
    total_propietarios.short_description = 'Total Propietarios'


@admin.register(Apartamento)
class ApartamentoAdmin(admin.ModelAdmin):
    """Admin para el modelo Apartamento"""
    list_display = ['edificio', 'piso', 'numero', 'total_residentes', 'propietario_info', 'edificio_info']
    list_filter = ['edificio', 'piso', 'created_at']
    search_fields = ['numero', 'edificio__numero']
    ordering = ['edificio__numero', 'piso', 'numero']
    readonly_fields = ['created_at', 'updated_at', 'total_residentes', 'propietario_info']
    
    fieldsets = (
        ('Información del Apartamento', {
            'fields': ('edificio', 'piso', 'numero')
        }),
        ('Información de Residentes', {
            'fields': ('total_residentes', 'propietario_info'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_residentes(self, obj):
        """Total de residentes en el apartamento"""
        return obj.get_total_residentes()
    total_residentes.short_description = 'Total Residentes'
    
    def propietario_info(self, obj):
        """Información del propietario"""
        propietario = obj.get_propietario()
        if propietario:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ {}</span>',
                propietario.nombre_completo
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Sin propietario</span>'
        )
    propietario_info.short_description = 'Propietario'
    
    def edificio_info(self, obj):
        """Información del edificio"""
        return f"Edificio {obj.edificio.numero}"
    edificio_info.short_description = 'Edificio'


@admin.register(Residente)
class ResidenteAdmin(admin.ModelAdmin):
    """Admin para el modelo Residente"""
    list_display = ['nombre_completo', 'tipo_badge', 'apartamento_info', 'foto_preview', 'created_at']
    list_filter = ['tipo', 'apartamento__edificio', 'apartamento__piso', 'created_at']
    search_fields = ['nombre_completo', 'apartamento__numero', 'apartamento__edificio__numero']
    ordering = ['tipo', 'nombre_completo']
    readonly_fields = ['created_at', 'updated_at', 'foto_preview']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre_completo', 'tipo', 'foto')
        }),
        ('Ubicación', {
            'fields': ('apartamento',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def tipo_badge(self, obj):
        """Mostrar tipo de residente con badge de color"""
        if obj.tipo == 'propietario':
            return format_html(
                '<span class="badge" style="background-color: #28a745; color: white; padding: 4px 8px; border-radius: 4px;">Propietario</span>'
            )
        else:
            return format_html(
                '<span class="badge" style="background-color: #17a2b8; color: white; padding: 4px 8px; border-radius: 4px;">Inquilino</span>'
            )
    tipo_badge.short_description = 'Tipo'
    
    def apartamento_info(self, obj):
        """Información completa del apartamento"""
        apt = obj.apartamento
        return f"Edificio {apt.edificio.numero} - Piso {apt.piso} - {apt.numero}"
    apartamento_info.short_description = 'Apartamento'
    
    def foto_preview(self, obj):
        """Vista previa de la foto"""
        if obj.foto:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.foto.url
            )
        return "Sin foto"
    foto_preview.short_description = 'Foto'
    
    def get_queryset(self, request):
        """Optimizar consultas con select_related"""
        return super().get_queryset(request).select_related(
            'apartamento__edificio'
        )
    
    def get_list_display(self, request):
        """Personalizar list_display según el usuario"""
        list_display = list(super().get_list_display(request))
        return list_display
    
    def get_ordering(self, request):
        """Ordenar por tipo y luego por nombre"""
        return ['tipo', 'nombre_completo']
