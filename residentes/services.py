"""
Servicios de negocio para el sistema de gestión de residentes
Implementa la lógica de negocio separada de las vistas
"""
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Edificio, Apartamento, Residente


class EdificioService:
    """Servicios para la gestión de edificios"""
    
    @staticmethod
    def crear_edificio(numero):
        """
        Crear un nuevo edificio
        
        Args:
            numero (int): Número del edificio (1-32)
            
        Returns:
            Edificio: El edificio creado
            
        Raises:
            ValidationError: Si el número no es válido
        """
        if numero < 1 or numero > 32:
            raise ValidationError('El número de edificio debe estar entre 1 y 32')
        
        edificio = Edificio(numero=numero)
        edificio.full_clean()
        edificio.save()
        return edificio
    
    @staticmethod
    def obtener_edificio_por_id(edificio_id):
        """
        Obtener un edificio por su ID
        
        Args:
            edificio_id (str): UUID del edificio
            
        Returns:
            Edificio: El edificio encontrado
            
        Raises:
            Edificio.DoesNotExist: Si no se encuentra el edificio
        """
        return Edificio.objects.get(id=edificio_id)
    
    @staticmethod
    def listar_edificios():
        """
        Listar todos los edificios ordenados por número
        
        Returns:
            QuerySet: Lista de edificios
        """
        return Edificio.objects.all().order_by('numero')


class ApartamentoService:
    """Servicios para la gestión de apartamentos"""
    
    @staticmethod
    def crear_apartamento(edificio_id, piso, numero):
        """
        Crear un nuevo apartamento
        
        Args:
            edificio_id (str): UUID del edificio
            piso (int): Número de piso (1-8)
            numero (str): Número del apartamento
            
        Returns:
            Apartamento: El apartamento creado
            
        Raises:
            ValidationError: Si los datos no son válidos
            Edificio.DoesNotExist: Si no se encuentra el edificio
        """
        # Verificar que el edificio existe
        edificio = EdificioService.obtener_edificio_por_id(edificio_id)
        
        # Verificar que el piso esté en el rango correcto
        if piso < 1 or piso > 8:
            raise ValidationError('El piso debe estar entre 1 y 8')
        
        # Verificar que el número sea coherente con el edificio
        puertas_disponibles = edificio.get_puertas_disponibles()
        if not any(numero.endswith(puerta) for puerta in puertas_disponibles):
            raise ValidationError(
                f'El número del apartamento debe terminar en {", ".join(puertas_disponibles)} '
                f'para el Edificio {edificio.numero}'
            )
        
        apartamento = Apartamento(
            edificio=edificio,
            piso=piso,
            numero=numero
        )
        apartamento.full_clean()
        apartamento.save()
        return apartamento
    
    @staticmethod
    def obtener_apartamento_por_id(apartamento_id):
        """
        Obtener un apartamento por su ID
        
        Args:
            apartamento_id (str): UUID del apartamento
            
        Returns:
            Apartamento: El apartamento encontrado
            
        Raises:
            Apartamento.DoesNotExist: Si no se encuentra el apartamento
        """
        return Apartamento.objects.get(id=apartamento_id)
    
    @staticmethod
    def buscar_apartamentos(filtros=None):
        """
        Buscar apartamentos con filtros opcionales
        
        Args:
            filtros (dict): Filtros de búsqueda
                - edificio_id: UUID del edificio
                - piso: Número de piso
                - numero: Número del apartamento
                
        Returns:
            QuerySet: Lista de apartamentos filtrados
        """
        queryset = Apartamento.objects.select_related('edificio').all()
        
        if filtros:
            if filtros.get('edificio_id'):
                queryset = queryset.filter(edificio_id=filtros['edificio_id'])
            if filtros.get('piso'):
                queryset = queryset.filter(piso=filtros['piso'])
            if filtros.get('numero'):
                queryset = queryset.filter(numero__icontains=filtros['numero'])
        
        return queryset.order_by('edificio__numero', 'piso', 'numero')

    @staticmethod
    def obtener_apartamentos_con_residentes():
        """
        Obtener apartamentos con información de residentes
        
        Returns:
            QuerySet: Apartamentos con residentes
        """
        return Apartamento.objects.select_related('edificio').prefetch_related('residentes').all()


class ResidenteService:
    """Servicios para la gestión de residentes"""
    
    @staticmethod
    def crear_residente(nombre_completo, apartamento_id, tipo='inquilino', foto=None):
        """
        Crear un nuevo residente
        
        Args:
            nombre_completo (str): Nombre completo del residente
            apartamento_id (str): UUID del apartamento
            tipo (str): Tipo de residente ('propietario' o 'inquilino')
            foto: Foto del residente (opcional)
            
        Returns:
            Residente: El residente creado
            
        Raises:
            ValidationError: Si los datos no son válidos
            Apartamento.DoesNotExist: Si no se encuentra el apartamento
        """
        # Verificar que el apartamento existe
        apartamento = ApartamentoService.obtener_apartamento_por_id(apartamento_id)
        
        # Verificar que se pueda agregar el residente
        if not apartamento.puede_agregar_residente(tipo):
            if tipo == 'propietario':
                raise ValidationError('Este apartamento ya tiene un propietario')
            else:
                raise ValidationError('Este apartamento ya tiene el máximo de 6 residentes')
        
        residente = Residente(
            nombre_completo=nombre_completo,
            apartamento=apartamento,
            tipo=tipo,
            foto=foto
        )
        residente.full_clean()
        residente.save()
        return residente
    
    @staticmethod
    def obtener_residente_por_id(residente_id):
        """
        Obtener un residente por su ID
        
        Args:
            residente_id (str): UUID del residente
            
        Returns:
            Residente: El residente encontrado
            
        Raises:
            Residente.DoesNotExist: Si no se encuentra el residente
        """
        return Residente.objects.select_related('apartamento__edificio').get(id=residente_id)
    
    @staticmethod
    def buscar_residentes(filtros=None):
        """
        Buscar residentes con filtros opcionales
        
        Args:
            filtros (dict): Filtros de búsqueda
                - nombre: Nombre del residente
                - tipo: Tipo de residente (propietario/inquilino)
                - edificio_id: UUID del edificio
                - piso: Número de piso
                - numero_apartamento: Número del apartamento
                
        Returns:
            QuerySet: Lista de residentes filtrados
        """
        queryset = Residente.objects.select_related(
            'apartamento__edificio'
        ).all()
        
        if filtros:
            if filtros.get('nombre'):
                queryset = queryset.filter(
                    nombre_completo__icontains=filtros['nombre']
                )
            if filtros.get('tipo'):
                queryset = queryset.filter(tipo=filtros['tipo'])
            if filtros.get('edificio_id'):
                queryset = queryset.filter(
                    apartamento__edificio_id=filtros['edificio_id']
                )
            if filtros.get('piso'):
                queryset = queryset.filter(
                    apartamento__piso=filtros['piso']
                )
            if filtros.get('numero_apartamento'):
                queryset = queryset.filter(
                    apartamento__numero__icontains=filtros['numero_apartamento']
                )
        
        return queryset.order_by('tipo', 'nombre_completo')
    
    @staticmethod
    def obtener_propietarios():
        """
        Obtener todos los propietarios
        
        Returns:
            QuerySet: Lista de propietarios
        """
        return Residente.objects.filter(tipo='propietario').select_related(
            'apartamento__edificio'
        ).order_by('apartamento__edificio__numero', 'apartamento__piso', 'apartamento__numero')
    
    @staticmethod
    def obtener_inquilinos():
        """
        Obtener todos los inquilinos
        
        Returns:
            QuerySet: Lista de inquilinos
        """
        return Residente.objects.filter(tipo='inquilino').select_related(
            'apartamento__edificio'
        ).order_by('nombre_completo')
    
    @staticmethod
    def cambiar_tipo_residente(residente_id, nuevo_tipo):
        """
        Cambiar el tipo de un residente
        
        Args:
            residente_id (str): UUID del residente
            nuevo_tipo (str): Nuevo tipo ('propietario' o 'inquilino')
            
        Returns:
            Residente: El residente actualizado
            
        Raises:
            ValidationError: Si no se puede cambiar el tipo
        """
        residente = ResidenteService.obtener_residente_por_id(residente_id)
        apartamento = residente.apartamento
        
        # Verificar que se pueda cambiar al nuevo tipo
        if not apartamento.puede_agregar_residente(nuevo_tipo):
            if nuevo_tipo == 'propietario':
                raise ValidationError('Este apartamento ya tiene un propietario')
            else:
                raise ValidationError('Este apartamento ya tiene el máximo de 6 residentes')
        
        # Cambiar el tipo
        residente.tipo = nuevo_tipo
        residente.full_clean()
        residente.save()
        return residente
    
    @staticmethod
    def eliminar_residente(residente_id):
        """
        Eliminar un residente
        
        Args:
            residente_id (str): UUID del residente
            
        Returns:
            bool: True si se eliminó correctamente
            
        Raises:
            Residente.DoesNotExist: Si no se encuentra el residente
        """
        residente = ResidenteService.obtener_residente_por_id(residente_id)
        residente.delete()
        return True
    
    @staticmethod
    def obtener_estadisticas():
        """
        Obtener estadísticas del sistema
        
        Returns:
            dict: Estadísticas del sistema
        """
        total_edificios = Edificio.objects.count()
        total_apartamentos = Apartamento.objects.count()
        total_residentes = Residente.objects.count()
        total_propietarios = Residente.objects.filter(tipo='propietario').count()
        total_inquilinos = Residente.objects.filter(tipo='inquilino').count()
        
        # Contar edificios con residentes
        edificios_con_residentes = Edificio.objects.filter(
            apartamentos__residentes__isnull=False
        ).distinct().count()
        
        # Apartamentos con propietario
        apartamentos_con_propietario = Apartamento.objects.filter(
            residentes__tipo='propietario'
        ).distinct().count()
        
        # Apartamentos sin propietario
        apartamentos_sin_propietario = total_apartamentos - apartamentos_con_propietario
        
        return {
            'total_edificios': total_edificios,
            'total_apartamentos': total_apartamentos,
            'total_residentes': total_residentes,
            'total_propietarios': total_propietarios,
            'total_inquilinos': total_inquilinos,
            'edificios_con_residentes': edificios_con_residentes,
            'edificios_sin_residentes': total_edificios - edificios_con_residentes,
            'apartamentos_con_propietario': apartamentos_con_propietario,
            'apartamentos_sin_propietario': apartamentos_sin_propietario
        }
