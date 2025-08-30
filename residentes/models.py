"""
Modelos para el sistema de gestión de residentes
Implementa la lógica de negocio y validaciones
"""
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Edificio(models.Model):
    """
    Modelo para representar un edificio del complejo residencial
    Los edificios solo tienen números del 1 al 32, sin puertas
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.IntegerField(
        unique=True,
        verbose_name=_("Número de Edificio"),
        help_text=_("Número del edificio (1-32)")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Fecha de Creación"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Fecha de Actualización"))

    class Meta:
        verbose_name = _("Edificio")
        verbose_name_plural = _("Edificios")
        ordering = ['numero']
        db_table = 'edificios'

    def clean(self):
        """Validar que el número esté en el rango correcto"""
        if self.numero < 1 or self.numero > 32:
            raise ValidationError({
                'numero': _('El número de edificio debe estar entre 1 y 32')
            })

    def __str__(self):
        return f"Edificio {self.numero}"

    def get_puertas_disponibles(self):
        """Obtener las puertas disponibles para este edificio"""
        if self.numero <= 22:
            return ['A', 'B']
        else:
            return ['I', 'D']


class Apartamento(models.Model):
    """
    Modelo para representar un apartamento
    Cada apartamento pertenece a un edificio y tiene un piso y número específico
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edificio = models.ForeignKey(
        Edificio,
        on_delete=models.CASCADE,
        related_name='apartamentos',
        verbose_name=_("Edificio")
    )
    piso = models.IntegerField(
        verbose_name=_("Piso"),
        help_text=_("Número de piso (1-8)")
    )
    numero = models.CharField(
        max_length=10,
        verbose_name=_("Número de Apartamento"),
        help_text=_("Número del apartamento (ej: 1A, 2B, 3I, 4D)")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Fecha de Creación"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Fecha de Actualización"))

    class Meta:
        verbose_name = _("Apartamento")
        verbose_name_plural = _("Apartamentos")
        unique_together = ['edificio', 'piso', 'numero']
        ordering = ['edificio__numero', 'piso', 'numero']
        db_table = 'apartamentos'

    def clean(self):
        """Validar coherencia entre edificio, piso y número"""
        # Validar rango de piso
        if self.piso < 1 or self.piso > 8:
            raise ValidationError({
                'piso': _('El piso debe estar entre 1 y 8')
            })

        # Validar que el número sea coherente con el edificio
        if self.edificio:
            puertas_disponibles = self.edificio.get_puertas_disponibles()
            if not any(self.numero.endswith(puerta) for puerta in puertas_disponibles):
                raise ValidationError({
                    'numero': _(
                        f'El número del apartamento debe terminar en {", ".join(puertas_disponibles)} '
                        f'para el Edificio {self.edificio.numero}'
                    )
                })

    def __str__(self):
        return f"Edificio {self.edificio.numero} - Piso {self.piso} - {self.numero}"

    @property
    def edificio_info(self):
        """Información del edificio para conveniencia"""
        return {
            'numero_edificio': self.edificio.numero,
            'piso': self.piso,
            'numero_apartamento': self.numero
        }

    def get_propietario(self):
        """Obtener el propietario del apartamento"""
        return self.residentes.filter(tipo='propietario').first()

    def get_inquilinos(self):
        """Obtener los inquilinos del apartamento"""
        return self.residentes.filter(tipo='inquilino')

    def get_total_residentes(self):
        """Obtener el total de residentes en el apartamento"""
        return self.residentes.count()

    def puede_agregar_residente(self, tipo_residente):
        """Verificar si se puede agregar un residente al apartamento"""
        total_actual = self.get_total_residentes()
        
        if tipo_residente == 'propietario':
            # Solo puede haber un propietario
            return not self.get_propietario()
        else:
            # Máximo 6 residentes en total
            return total_actual < 6


class Residente(models.Model):
    """
    Modelo para representar un residente
    Cada residente está asignado a un apartamento específico
    Puede ser propietario o inquilino
    """
    
    class TipoResidente(models.TextChoices):
        PROPIETARIO = 'propietario', _('Propietario')
        INQUILINO = 'inquilino', _('Inquilino')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    apartamento = models.ForeignKey(
        Apartamento,
        on_delete=models.CASCADE,
        related_name='residentes',
        verbose_name=_("Apartamento")
    )
    nombre_completo = models.CharField(
        max_length=200,
        verbose_name=_("Nombre Completo")
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoResidente.choices,
        default=TipoResidente.INQUILINO,
        verbose_name=_("Tipo de Residente"),
        help_text=_("Propietario o inquilino del apartamento")
    )
    foto = models.ImageField(
        upload_to='residentes/fotos/',
        blank=True,
        null=True,
        verbose_name=_("Foto del Residente"),
        help_text=_("Foto opcional del residente")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Fecha de Creación"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Fecha de Actualización"))

    class Meta:
        verbose_name = _("Residente")
        verbose_name_plural = _("Residentes")
        ordering = ['tipo', 'nombre_completo']
        db_table = 'residentes'
        # Un propietario por apartamento
        unique_together = ['apartamento', 'tipo']

    def clean(self):
        """Validar reglas de negocio para residentes"""
        if self.apartamento:
            # Verificar que no se exceda el límite de residentes
            if not self.apartamento.puede_agregar_residente(self.tipo):
                if self.tipo == 'propietario':
                    raise ValidationError({
                        'tipo': _('Este apartamento ya tiene un propietario')
                    })
                else:
                    raise ValidationError({
                        'tipo': _('Este apartamento ya tiene el máximo de 6 residentes')
                    })

    def __str__(self):
        tipo_display = self.get_tipo_display()
        return f"{self.nombre_completo} ({tipo_display}) - {self.apartamento}"

    @property
    def edificio_info(self):
        """Información del edificio y apartamento para conveniencia"""
        return {
            'numero_edificio': self.apartamento.edificio.numero,
            'piso': self.apartamento.piso,
            'numero_apartamento': self.apartamento.numero
        }

    @property
    def es_propietario(self):
        """Verificar si el residente es propietario"""
        return self.tipo == 'propietario'

    @property
    def es_inquilino(self):
        """Verificar si el residente es inquilino"""
        return self.tipo == 'inquilino'
