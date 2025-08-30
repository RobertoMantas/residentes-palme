"""
Vistas de la API REST para el sistema de gestión de residentes
Implementa endpoints RESTful siguiendo principios de Clean Architecture
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Edificio, Apartamento, Residente
from .serializers import (
    EdificioSerializer, ApartamentoSerializer, ResidenteSerializer,
    ResidenteCreateSerializer, ResidenteSearchSerializer, ApartamentoCreateSerializer
)
from .services import EdificioService, ApartamentoService, ResidenteService


class EdificioAPIView(APIView):
    """Vista para gestionar edificios"""
    
    def get(self, request):
        """Listar edificios con paginación opcional"""
        try:
            edificios = EdificioService.listar_edificios()
            
            # Paginación opcional
            page = request.query_params.get('page')
            if page:
                paginator = Paginator(edificios, 20)
                edificios = paginator.get_page(page)
                serializer = EdificioSerializer(edificios, many=True)
                return Response({
                    'success': True,
                    'data': serializer.data,
                    'pagination': {
                        'page': edificios.number,
                        'total_pages': edificios.paginator.num_pages,
                        'total_count': edificios.paginator.count,
                        'has_next': edificios.has_next(),
                        'has_previous': edificios.has_previous()
                    }
                })
            
            serializer = EdificioSerializer(edificios, many=True)
            return Response({
                'success': True,
                'data': serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'message': 'Error al obtener los edificios'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Crear un nuevo edificio"""
        try:
            serializer = EdificioSerializer(data=request.data)
            if serializer.is_valid():
                edificio = EdificioService.crear_edificio(
                    numero=serializer.validated_data['numero']
                )
                response_serializer = EdificioSerializer(edificio)
                return Response({
                    'success': True,
                    'data': response_serializer.data,
                    'message': 'Edificio creado correctamente'
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': serializer.errors,
                    'message': 'Datos de entrada inválidos'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'message': 'Error al crear el edificio'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ApartamentoAPIView(APIView):
    """Vista para gestionar apartamentos"""
    
    def get(self, request):
        """Listar apartamentos con filtros opcionales"""
        try:
            # Filtros de búsqueda
            filtros = {}
            if request.query_params.get('edificio_id'):
                filtros['edificio_id'] = request.query_params.get('edificio_id')
            if request.query_params.get('piso'):
                filtros['piso'] = int(request.query_params.get('piso'))
            if request.query_params.get('numero'):
                filtros['numero'] = request.query_params.get('numero')
            
            apartamentos = ApartamentoService.buscar_apartamentos(filtros)
            
            # Paginación
            page = request.query_params.get('page', 1)
            paginator = Paginator(apartamentos, 20)
            apartamentos_paginados = paginator.get_page(page)
            
            serializer = ApartamentoSerializer(apartamentos_paginados, many=True)
            return Response({
                'success': True,
                'data': serializer.data,
                'pagination': {
                    'page': apartamentos_paginados.number,
                    'total_pages': apartamentos_paginados.paginator.num_pages,
                    'total_count': apartamentos_paginados.paginator.count,
                    'has_next': apartamentos_paginados.has_next(),
                    'has_previous': apartamentos_paginados.has_previous()
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'message': 'Error al obtener los apartamentos'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Crear un nuevo apartamento"""
        try:
            serializer = ApartamentoCreateSerializer(data=request.data)
            if serializer.is_valid():
                apartamento = ApartamentoService.crear_apartamento(
                    edificio_id=serializer.validated_data['edificio_id'],
                    piso=serializer.validated_data['piso'],
                    numero=serializer.validated_data['numero']
                )
                response_serializer = ApartamentoSerializer(apartamento)
                return Response({
                    'success': True,
                    'data': response_serializer.data,
                    'message': 'Apartamento creado correctamente'
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': serializer.errors,
                    'message': 'Datos de entrada inválidos'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'message': 'Error al crear el apartamento'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResidenteAPIView(APIView):
    """Vista para gestionar residentes"""
    
    def get(self, request):
        """Buscar residentes con filtros opcionales"""
        try:
            # Filtros de búsqueda
            filtros = {}
            if request.query_params.get('nombre'):
                filtros['nombre'] = request.query_params.get('nombre')
            if request.query_params.get('edificio_id'):
                filtros['edificio_id'] = request.query_params.get('edificio_id')
            if request.query_params.get('piso'):
                filtros['piso'] = int(request.query_params.get('piso'))
            if request.query_params.get('numero_apartamento'):
                filtros['numero_apartamento'] = request.query_params.get('numero_apartamento')
            
            residentes = ResidenteService.buscar_residentes(filtros)
            
            # Paginación
            page = request.query_params.get('page', 1)
            paginator = Paginator(residentes, 20)
            residentes_paginados = paginator.get_page(page)
            
            serializer = ResidenteSearchSerializer(residentes_paginados, many=True)
            return Response({
                'success': True,
                'data': serializer.data,
                'pagination': {
                    'page': residentes_paginados.number,
                    'total_pages': residentes_paginados.paginator.num_pages,
                    'total_count': residentes_paginados.paginator.count,
                    'has_next': residentes_paginados.has_next(),
                    'has_previous': residentes_paginados.has_previous()
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'message': 'Error al buscar residentes'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Crear un nuevo residente"""
        try:
            serializer = ResidenteCreateSerializer(data=request.data)
            if serializer.is_valid():
                residente = ResidenteService.crear_residente(
                    nombre_completo=serializer.validated_data['nombre_completo'],
                    apartamento_id=serializer.validated_data['apartamento_id'],
                    foto=request.FILES.get('foto') if request.FILES else None
                )
                response_serializer = ResidenteSerializer(residente)
                return Response({
                    'success': True,
                    'data': response_serializer.data,
                    'message': 'Residente creado correctamente'
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': serializer.errors,
                    'message': 'Datos de entrada inválidos'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'message': 'Error al crear el residente'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResidenteDetailAPIView(APIView):
    """Vista para gestionar un residente específico"""
    
    def get(self, request, residente_id):
        """Obtener detalles de un residente"""
        try:
            residente = ResidenteService.obtener_residente_por_id(residente_id)
            serializer = ResidenteSerializer(residente)
            return Response({
                'success': True,
                'data': serializer.data
            })
            
        except Residente.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Residente no encontrado',
                'message': 'El residente especificado no existe'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'message': 'Error al obtener el residente'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, residente_id):
        """Eliminar un residente"""
        try:
            ResidenteService.eliminar_residente(residente_id)
            return Response({
                'success': True,
                'message': 'Residente eliminado correctamente'
            })
            
        except Residente.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Residente no encontrado',
                'message': 'El residente especificado no existe'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'message': 'Error al eliminar el residente'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def estadisticas_api(request):
    """Endpoint para obtener estadísticas del sistema"""
    try:
        stats = ResidenteService.obtener_estadisticas()
        return Response({
            'success': True,
            'data': stats,
            'message': 'Estadísticas obtenidas correctamente'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Error al obtener las estadísticas'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
