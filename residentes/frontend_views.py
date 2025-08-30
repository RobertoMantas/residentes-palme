"""
Vistas del frontend para el sistema de gestión de residentes
Implementa la interfaz de usuario para el conserje
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from .models import Edificio, Apartamento, Residente
from .services import EdificioService, ApartamentoService, ResidenteService


def dashboard(request):
    """Vista del dashboard principal"""
    try:
        stats = ResidenteService.obtener_estadisticas()
        
        # Obtener residentes recientes
        residentes_recientes = Residente.objects.select_related(
            'apartamento__edificio'
        ).order_by('-created_at')[:10]
        
        context = {
            'stats': stats,
            'residentes_recientes': residentes_recientes
        }
        
        return render(request, 'residentes/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f'Error al cargar el dashboard: {str(e)}')
        return render(request, 'residentes/dashboard.html', {'stats': {}, 'residentes_recientes': []})


def subir_residente(request):
    """Vista para subir información de un nuevo residente"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre_completo = request.POST.get('nombre_completo')
            tipo = request.POST.get('tipo')
            apartamento_id = request.POST.get('apartamento_id')
            foto = request.FILES.get('foto')
            
            # Validar datos requeridos
            if not nombre_completo or not tipo or not apartamento_id:
                messages.error(request, 'Nombre completo, tipo y apartamento son obligatorios')
                return redirect('residentes_frontend:subir_residente')
            
            # Crear residente usando el servicio
            residente = ResidenteService.crear_residente(
                nombre_completo=nombre_completo,
                tipo=tipo,
                apartamento_id=apartamento_id,
                foto=foto
            )
            
            messages.success(
                request, 
                f'Residente {residente.nombre_completo} ({residente.get_tipo_display()}) creado correctamente en {residente.apartamento}'
            )
            return redirect('residentes_frontend:dashboard')
            
        except Exception as e:
            messages.error(request, f'Error al crear el residente: {str(e)}')
    
    # GET: mostrar formulario
    try:
        edificios = EdificioService.listar_edificios()
        apartamentos = ApartamentoService.obtener_apartamentos_con_residentes()
        
        context = {
            'edificios': edificios,
            'apartamentos': apartamentos
        }
        return render(request, 'residentes/subir_residente.html', context)
        
    except Exception as e:
        messages.error(request, f'Error al cargar el formulario: {str(e)}')
        return render(request, 'residentes/subir_residente.html', {'edificios': [], 'apartamentos': []})


def buscar_residentes(request):
    """Vista para buscar y listar residentes"""
    try:
        # Filtros de búsqueda
        filtros = {}
        nombre = request.GET.get('nombre', '')
        edificio_id = request.GET.get('edificio_id', '')
        piso = request.GET.get('piso', '')
        numero_apartamento = request.GET.get('numero_apartamento', '')
        
        if nombre:
            filtros['nombre'] = nombre
        if edificio_id:
            filtros['edificio_id'] = edificio_id
        if piso:
            try:
                filtros['piso'] = int(piso)
            except ValueError:
                pass
        if numero_apartamento:
            filtros['numero_apartamento'] = numero_apartamento
        
        # Buscar residentes
        residentes = ResidenteService.buscar_residentes(filtros)
        
        # Paginación
        page = request.GET.get('page', 1)
        paginator = Paginator(residentes, 20)
        residentes_paginados = paginator.get_page(page)
        
        # Datos para el formulario de búsqueda
        edificios = EdificioService.listar_edificios()
        
        context = {
            'residentes': residentes_paginados,
            'edificios': edificios,
            'filtros': {
                'nombre': nombre,
                'edificio_id': edificio_id,
                'piso': piso,
                'numero_apartamento': numero_apartamento
            }
        }
        
        return render(request, 'residentes/buscar_residentes.html', context)
        
    except Exception as e:
        messages.error(request, f'Error al buscar residentes: {str(e)}')
        return render(request, 'residentes/buscar_residentes.html', {
            'residentes': [],
            'edificios': [],
            'filtros': {}
        })


def eliminar_residente(request):
    """Vista para eliminar un residente"""
    if request.method == 'POST':
        try:
            residente_id = request.POST.get('residente_id')
            if not residente_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de residente requerido'
                }, status=400)
            
            # Eliminar residente usando el servicio
            ResidenteService.eliminar_residente(residente_id)
            
            return JsonResponse({
                'success': True,
                'message': 'Residente eliminado correctamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al eliminar residente: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)


def gestionar_edificios(request):
    """Vista para gestionar edificios"""
    if request.method == 'POST':
        try:
            numero = request.POST.get('numero')
            if not numero:
                messages.error(request, 'El número de edificio es obligatorio')
                return redirect('residentes_frontend:gestionar_edificios')
            
            # Crear edificio usando el servicio
            edificio = EdificioService.crear_edificio(numero=int(numero))
            
            messages.success(
                request, 
                f'Edificio {edificio.numero} creado correctamente'
            )
            return redirect('residentes_frontend:gestionar_edificios')
            
        except Exception as e:
            messages.error(request, f'Error al crear el edificio: {str(e)}')
    
    # GET: mostrar lista de edificios
    try:
        edificios = EdificioService.listar_edificios()
        context = {
            'edificios': edificios
        }
        return render(request, 'residentes/gestionar_edificios.html', context)
        
    except Exception as e:
        messages.error(request, f'Error al cargar los edificios: {str(e)}')
        return render(request, 'residentes/gestionar_edificios.html', {'edificios': []})


def gestionar_apartamentos(request):
    """Vista para gestionar apartamentos"""
    if request.method == 'POST':
        try:
            edificio_id = request.POST.get('edificio_id')
            piso = request.POST.get('piso')
            numero = request.POST.get('numero')
            
            if not all([edificio_id, piso, numero]):
                messages.error(request, 'Todos los campos son obligatorios')
                return redirect('residentes_frontend:gestionar_apartamentos')
            
            # Crear apartamento usando el servicio
            apartamento = ApartamentoService.crear_apartamento(
                edificio_id=edificio_id,
                piso=int(piso),
                numero=numero
            )
            
            messages.success(
                request, 
                f'Apartamento {apartamento.numero} creado correctamente en {apartamento.edificio}'
            )
            return redirect('residentes_frontend:gestionar_apartamentos')
            
        except Exception as e:
            messages.error(request, f'Error al crear el apartamento: {str(e)}')
    
    # GET: mostrar lista de apartamentos
    try:
        apartamentos = ApartamentoService.buscar_apartamentos()
        edificios = EdificioService.listar_edificios()
        
        context = {
            'apartamentos': apartamentos,
            'edificios': edificios
        }
        return render(request, 'residentes/gestionar_apartamentos.html', context)
        
    except Exception as e:
        messages.error(request, f'Error al cargar los apartamentos: {str(e)}')
        return render(request, 'residentes/gestionar_apartamentos.html', {
            'apartamentos': [],
            'edificios': []
        })


# Endpoints AJAX para funcionalidades dinámicas
@csrf_exempt
def api_crear_residente_ajax(request):
    """Endpoint AJAX para crear residentes (sin foto)"""
    if request.method == 'POST':
        try:
            nombre_completo = request.POST.get('nombre_completo')
            tipo = request.POST.get('tipo', 'inquilino')
            apartamento_id = request.POST.get('apartamento_id')
            
            if not nombre_completo or not apartamento_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Nombre completo y apartamento son obligatorios'
                }, status=400)
            
            # Crear residente usando el servicio
            residente = ResidenteService.crear_residente(
                nombre_completo=nombre_completo,
                tipo=tipo,
                apartamento_id=apartamento_id
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Residente {residente.nombre_completo} ({residente.get_tipo_display()}) creado correctamente',
                'data': {
                    'id': str(residente.id),
                    'nombre_completo': residente.nombre_completo,
                    'tipo': residente.tipo,
                    'apartamento': str(residente.apartamento)
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al crear el residente: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)


def api_buscar_residentes_ajax(request):
    """Endpoint AJAX para buscar residentes"""
    try:
        # Filtros de búsqueda
        filtros = {}
        nombre = request.GET.get('nombre', '')
        edificio_id = request.GET.get('edificio_id', '')
        piso = request.GET.get('piso', '')
        numero_apartamento = request.GET.get('numero_apartamento', '')
        
        if nombre:
            filtros['nombre'] = nombre
        if edificio_id:
            filtros['edificio_id'] = edificio_id
        if piso:
            try:
                filtros['piso'] = int(piso)
            except ValueError:
                pass
        if numero_apartamento:
            filtros['numero_apartamento'] = numero_apartamento
        
        # Buscar residentes
        residentes = ResidenteService.buscar_residentes(filtros)
        
        # Serializar resultados
        from .serializers import ResidenteSearchSerializer
        serializer = ResidenteSearchSerializer(residentes[:50], many=True)  # Limitar a 50 resultados
        
        return JsonResponse({
            'success': True,
            'data': serializer.data,
            'total': residentes.count()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al buscar residentes: {str(e)}'
        }, status=500)


def ver_detalles_residente(request, residente_id):
    """Vista para mostrar los detalles de un residente específico"""
    try:
        # Obtener el residente con información relacionada
        residente = ResidenteService.obtener_residente_por_id(residente_id)
        
        # Obtener estadísticas del apartamento
        apartamento = residente.apartamento
        total_residentes = apartamento.get_total_residentes()
        propietario = apartamento.get_propietario()
        inquilinos = apartamento.get_inquilinos()
        
        context = {
            'residente': residente,
            'apartamento': apartamento,
            'total_residentes': total_residentes,
            'propietario': propietario,
            'inquilinos': inquilinos,
            'titulo': f'Detalles de {residente.nombre_completo}'
        }
        
        return render(request, 'residentes/ver_detalles_residente.html', context)
        
    except Residente.DoesNotExist:
        messages.error(request, 'El residente especificado no existe')
        return redirect('residentes_frontend:buscar_residentes')
    except Exception as e:
        messages.error(request, f'Error al cargar los detalles: {str(e)}')
        return redirect('residentes_frontend:buscar_residentes')
