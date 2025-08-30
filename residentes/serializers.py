"""
Serializers para la API REST del sistema de gestión de residentes
Implementa la serialización y validación de datos
"""
from rest_framework import serializers
from .models import Edificio, Apartamento, Residente


class EdificioSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Edificio"""
    
    class Meta:
        model = Edificio
        fields = ['id', 'numero', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_numero(self, value):
        """Validar que el número esté en el rango correcto"""
        if value < 1 or value > 32:
            raise serializers.ValidationError(
                'El número de edificio debe estar entre 1 y 32'
            )
        return value


class ApartamentoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Apartamento"""
    edificio = EdificioSerializer(read_only=True)
    edificio_id = serializers.UUIDField(write_only=True)
    total_residentes = serializers.SerializerMethodField()
    propietario = serializers.SerializerMethodField()
    
    class Meta:
        model = Apartamento
        fields = ['id', 'edificio', 'edificio_id', 'piso', 'numero', 'total_residentes', 'propietario', 'created_at', 'updated_at']
        read_only_fields = ['id', 'edificio', 'total_residentes', 'propietario', 'created_at', 'updated_at']

    def get_total_residentes(self, obj):
        """Obtener el total de residentes en el apartamento"""
        return obj.get_total_residentes()

    def get_propietario(self, obj):
        """Obtener información del propietario"""
        propietario = obj.get_propietario()
        if propietario:
            return {
                'id': str(propietario.id),
                'nombre_completo': propietario.nombre_completo,
                'foto_url': propietario.foto.url if propietario.foto else None
            }
        return None

    def validate_piso(self, value):
        """Validar que el piso esté en el rango correcto"""
        if value < 1 or value > 8:
            raise serializers.ValidationError(
                'El piso debe estar entre 1 y 8'
            )
        return value

    def validate(self, data):
        """Validar coherencia entre edificio y número de apartamento"""
        edificio_id = data.get('edificio_id')
        numero = data.get('numero')
        
        if edificio_id and numero:
            try:
                edificio = Edificio.objects.get(id=edificio_id)
                puertas_disponibles = edificio.get_puertas_disponibles()
                
                if not any(numero.endswith(puerta) for puerta in puertas_disponibles):
                    raise serializers.ValidationError({
                        'numero': f'El número del apartamento debe terminar en {", ".join(puertas_disponibles)} '
                                f'para el Edificio {edificio.numero}'
                    })
            except Edificio.DoesNotExist:
                raise serializers.ValidationError({
                    'edificio_id': 'El edificio especificado no existe'
                })
        
        return data


class ApartamentoCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para crear apartamentos"""
    edificio_id = serializers.UUIDField()
    
    class Meta:
        model = Apartamento
        fields = ['edificio_id', 'piso', 'numero']

    def validate(self, data):
        """Validar coherencia entre edificio y número de apartamento"""
        edificio_id = data.get('edificio_id')
        numero = data.get('numero')
        
        if edificio_id and numero:
            try:
                edificio = Edificio.objects.get(id=edificio_id)
                puertas_disponibles = edificio.get_puertas_disponibles()
                
                if not any(numero.endswith(puerta) for puerta in puertas_disponibles):
                    raise serializers.ValidationError({
                        'numero': f'El número del apartamento debe terminar en {", ".join(puertas_disponibles)} '
                                f'para el Edificio {edificio.numero}'
                    })
            except Edificio.DoesNotExist:
                raise serializers.ValidationError({
                    'edificio_id': 'El edificio especificado no existe'
                })
        
        return data


class ResidenteSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Residente"""
    apartamento = ApartamentoSerializer(read_only=True)
    apartamento_id = serializers.UUIDField(write_only=True)
    edificio_info = serializers.SerializerMethodField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Residente
        fields = ['id', 'apartamento', 'apartamento_id', 'nombre_completo', 'tipo', 'tipo_display', 'foto', 'edificio_info', 'created_at', 'updated_at']
        read_only_fields = ['id', 'apartamento', 'edificio_info', 'tipo_display', 'created_at', 'updated_at']

    def get_edificio_info(self, obj):
        """Obtener información del edificio y apartamento"""
        return {
            'numero_edificio': obj.apartamento.edificio.numero,
            'piso': obj.apartamento.piso,
            'numero_apartamento': obj.apartamento.numero
        }

    def validate_apartamento_id(self, value):
        """Validar que el apartamento existe"""
        try:
            Apartamento.objects.get(id=value)
        except Apartamento.DoesNotExist:
            raise serializers.ValidationError(
                'El apartamento especificado no existe'
            )
        return value

    def validate(self, data):
        """Validar reglas de negocio para residentes"""
        apartamento_id = data.get('apartamento_id')
        tipo = data.get('tipo', 'inquilino')
        
        if apartamento_id:
            try:
                apartamento = Apartamento.objects.get(id=apartamento_id)
                
                # Verificar que se pueda agregar el residente
                if not apartamento.puede_agregar_residente(tipo):
                    if tipo == 'propietario':
                        raise serializers.ValidationError({
                            'tipo': 'Este apartamento ya tiene un propietario'
                        })
                    else:
                        raise serializers.ValidationError({
                            'tipo': 'Este apartamento ya tiene el máximo de 6 residentes'
                        })
                        
            except Apartamento.DoesNotExist:
                raise serializers.ValidationError({
                    'apartamento_id': 'El apartamento especificado no existe'
                })
        
        return data


class ResidenteCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para crear residentes"""
    apartamento_id = serializers.UUIDField()
    
    class Meta:
        model = Residente
        fields = ['apartamento_id', 'nombre_completo', 'tipo', 'foto']

    def validate_apartamento_id(self, value):
        """Validar que el apartamento existe"""
        try:
            Apartamento.objects.get(id=value)
        except Apartamento.DoesNotExist:
            raise serializers.ValidationError(
                'El apartamento especificado no existe'
            )
        return value

    def validate(self, data):
        """Validar reglas de negocio para residentes"""
        apartamento_id = data.get('apartamento_id')
        tipo = data.get('tipo', 'inquilino')
        
        if apartamento_id:
            try:
                apartamento = Apartamento.objects.get(id=apartamento_id)
                
                # Verificar que se pueda agregar el residente
                if not apartamento.puede_agregar_residente(tipo):
                    if tipo == 'propietario':
                        raise serializers.ValidationError({
                            'tipo': 'Este apartamento ya tiene un propietario'
                        })
                    else:
                        raise serializers.ValidationError({
                            'tipo': 'Este apartamento ya tiene el máximo de 6 residentes'
                        })
                        
            except Apartamento.DoesNotExist:
                raise serializers.ValidationError({
                    'apartamento_id': 'El apartamento especificado no existe'
                })
        
        return data


class ResidenteSearchSerializer(serializers.ModelSerializer):
    """Serializer para resultados de búsqueda de residentes"""
    apartamento_info = serializers.SerializerMethodField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Residente
        fields = ['id', 'nombre_completo', 'tipo', 'tipo_display', 'foto', 'apartamento_info']

    def get_apartamento_info(self, obj):
        """Obtener información del apartamento para búsqueda"""
        return {
            'numero_edificio': obj.apartamento.edificio.numero,
            'piso': obj.apartamento.piso,
            'numero_apartamento': obj.apartamento.numero
        }
