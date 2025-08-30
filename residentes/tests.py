"""
Tests para el Sistema de Gestión de Residentes de Palme
Incluye tests unitarios e integración siguiendo mejores prácticas
"""
import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Edificio, Apartamento, Residente
from .services import EdificioService, ApartamentoService, ResidenteService


class EdificioModelTest(TestCase):
    """Tests para el modelo Edificio"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.edificio_valido_1 = Edificio(numero=1, puerta='A')
        self.edificio_valido_2 = Edificio(numero=25, puerta='I')
        self.edificio_invalido_1 = Edificio(numero=1, puerta='I')  # Regla violada
        self.edificio_invalido_2 = Edificio(numero=25, puerta='A')  # Regla violada
    
    def test_edificio_creacion_valida(self):
        """Test para crear edificios válidos"""
        self.edificio_valido_1.full_clean()
        self.edificio_valido_1.save()
        
        self.edificio_valido_2.full_clean()
        self.edificio_valido_2.save()
        
        self.assertEqual(Edificio.objects.count(), 2)
        self.assertEqual(Edificio.objects.get(numero=1).puerta, 'A')
        self.assertEqual(Edificio.objects.get(numero=25).puerta, 'I')
    
    def test_edificio_reglas_validacion(self):
        """Test para validar las reglas de negocio de edificios"""
        # Edificio 1-22 con puerta I (inválido)
        with self.assertRaises(ValidationError):
            self.edificio_invalido_1.full_clean()
        
        # Edificio 23-32 con puerta A (inválido)
        with self.assertRaises(ValidationError):
            self.edificio_invalido_2.full_clean()
    
    def test_edificio_str_representation(self):
        """Test para la representación en string del edificio"""
        self.edificio_valido_1.save()
        expected_str = "Edificio 1 - Puerta A"
        self.assertEqual(str(self.edificio_valido_1), expected_str)
    
    def test_edificio_ordering(self):
        """Test para verificar el ordenamiento de edificios"""
        edificio_3 = Edificio(numero=3, puerta='B')
        edificio_2 = Edificio(numero=2, puerta='A')
        
        edificio_3.save()
        edificio_2.save()
        self.edificio_valido_1.save()
        
        edificios = Edificio.objects.all()
        self.assertEqual(edificios[0].numero, 1)
        self.assertEqual(edificios[1].numero, 2)
        self.assertEqual(edificios[2].numero, 3)


class ApartamentoModelTest(TestCase):
    """Tests para el modelo Apartamento"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.edificio_1 = Edificio.objects.create(numero=1, puerta='A')
        self.edificio_25 = Edificio.objects.create(numero=25, puerta='I')
        
        self.apartamento_valido_1 = Apartamento(
            edificio=self.edificio_1,
            piso=3,
            numero='3A'
        )
        self.apartamento_valido_2 = Apartamento(
            edificio=self.edificio_25,
            piso=5,
            numero='5I'
        )
        self.apartamento_invalido_1 = Apartamento(
            edificio=self.edificio_1,
            piso=3,
            numero='3I'  # Debería ser A o B
        )
    
    def test_apartamento_creacion_valida(self):
        """Test para crear apartamentos válidos"""
        self.apartamento_valido_1.full_clean()
        self.apartamento_valido_1.save()
        
        self.apartamento_valido_2.full_clean()
        self.apartamento_valido_2.save()
        
        self.assertEqual(Apartamento.objects.count(), 2)
        self.assertEqual(Apartamento.objects.get(piso=3).numero, '3A')
    
    def test_apartamento_reglas_validacion(self):
        """Test para validar las reglas de negocio de apartamentos"""
        # Apartamento en edificio 1-22 con número I (inválido)
        with self.assertRaises(ValidationError):
            self.apartamento_invalido_1.full_clean()
    
    def test_apartamento_unique_together(self):
        """Test para verificar la unicidad de apartamentos"""
        self.apartamento_valido_1.save()
        
        # Intentar crear otro apartamento con el mismo edificio, piso y número
        apartamento_duplicado = Apartamento(
            edificio=self.edificio_1,
            piso=3,
            numero='3A'
        )
        
        with self.assertRaises(Exception):  # Debería fallar por unique_together
            apartamento_duplicado.save()
    
    def test_apartamento_str_representation(self):
        """Test para la representación en string del apartamento"""
        self.apartamento_valido_1.save()
        expected_str = "Edificio 1 - Piso 3 - 3A"
        self.assertEqual(str(self.apartamento_valido_1), expected_str)


class ResidenteModelTest(TestCase):
    """Tests para el modelo Residente"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.edificio = Edificio.objects.create(numero=1, puerta='A')
        self.apartamento = Apartamento.objects.create(
            edificio=self.edificio,
            piso=3,
            numero='3A'
        )
        
        self.residente = Residente(
            apartamento=self.apartamento,
            nombre_completo='Juan Carlos Pérez García'
        )
    
    def test_residente_creacion_valida(self):
        """Test para crear residentes válidos"""
        self.residente.full_clean()
        self.residente.save()
        
        self.assertEqual(Residente.objects.count(), 1)
        self.assertEqual(Residente.objects.first().nombre_completo, 'Juan Carlos Pérez García')
    
    def test_residente_str_representation(self):
        """Test para la representación en string del residente"""
        self.residente.save()
        expected_str = "Juan Carlos Pérez García - Edificio 1 - Piso 3 - 3A"
        self.assertEqual(str(self.residente), expected_str)
    
    def test_residente_edificio_info_property(self):
        """Test para la propiedad edificio_info"""
        self.residente.save()
        info = self.residente.edificio_info
        
        self.assertEqual(info['numero'], 1)
        self.assertEqual(info['puerta'], 'A')
        self.assertEqual(info['piso'], 3)
        self.assertEqual(info['numero_apartamento'], '3A')


class EdificioServiceTest(TestCase):
    """Tests para el servicio EdificioService"""
    
    def test_crear_edificio_valido(self):
        """Test para crear edificios válidos usando el servicio"""
        edificio = EdificioService.crear_edificio(1, 'A')
        self.assertEqual(edificio.numero, 1)
        self.assertEqual(edificio.puerta, 'A')
        
        edificio_2 = EdificioService.crear_edificio(25, 'I')
        self.assertEqual(edificio_2.numero, 25)
        self.assertEqual(edificio_2.puerta, 'I')
    
    def test_crear_edificio_invalido(self):
        """Test para validar reglas de negocio en el servicio"""
        # Edificio 1-22 con puerta I
        with self.assertRaises(ValidationError):
            EdificioService.crear_edificio(1, 'I')
        
        # Edificio 23-32 con puerta A
        with self.assertRaises(ValidationError):
            EdificioService.crear_edificio(25, 'A')
    
    def test_obtener_edificio_por_id(self):
        """Test para obtener edificio por ID"""
        edificio = EdificioService.crear_edificio(1, 'A')
        edificio_obtenido = EdificioService.obtener_edificio_por_id(str(edificio.id))
        
        self.assertEqual(edificio_obtenido, edificio)
        
        # Test con ID inexistente
        edificio_inexistente = EdificioService.obtener_edificio_por_id(str(uuid.uuid4()))
        self.assertIsNone(edificio_inexistente)
    
    def test_listar_edificios(self):
        """Test para listar todos los edificios"""
        EdificioService.crear_edificio(3, 'B')
        EdificioService.crear_edificio(1, 'A')
        EdificioService.crear_edificio(2, 'A')
        
        edificios = EdificioService.listar_edificios()
        self.assertEqual(len(edificios), 3)
        self.assertEqual(edificios[0].numero, 1)  # Debe estar ordenado


class ApartamentoServiceTest(TestCase):
    """Tests para el servicio ApartamentoService"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.edificio = EdificioService.crear_edificio(1, 'A')
    
    def test_crear_apartamento_valido(self):
        """Test para crear apartamentos válidos usando el servicio"""
        apartamento = ApartamentoService.crear_apartamento(
            str(self.edificio.id), 3, '3A'
        )
        
        self.assertEqual(apartamento.edificio, self.edificio)
        self.assertEqual(apartamento.piso, 3)
        self.assertEqual(apartamento.numero, '3A')
    
    def test_crear_apartamento_edificio_inexistente(self):
        """Test para crear apartamento con edificio inexistente"""
        with self.assertRaises(ValidationError):
            ApartamentoService.crear_apartamento(str(uuid.uuid4()), 3, '3A')
    
    def test_crear_apartamento_numero_incoherente(self):
        """Test para validar coherencia entre edificio y número de apartamento"""
        # Apartamento en edificio 1-22 con número I
        with self.assertRaises(ValidationError):
            ApartamentoService.crear_apartamento(
                str(self.edificio.id), 3, '3I'
            )
    
    def test_buscar_apartamentos(self):
        """Test para buscar apartamentos con filtros"""
        ApartamentoService.crear_apartamento(str(self.edificio.id), 3, '3A')
        ApartamentoService.crear_apartamento(str(self.edificio.id), 4, '4A')
        
        # Buscar por piso
        apartamentos_piso_3 = ApartamentoService.buscar_apartamentos(piso=3)
        self.assertEqual(len(apartamentos_piso_3), 1)
        self.assertEqual(apartamentos_piso_3[0].piso, 3)
        
        # Buscar por número
        apartamentos_numero_a = ApartamentoService.buscar_apartamentos(numero='A')
        self.assertEqual(len(apartamentos_numero_a), 2)


class ResidenteServiceTest(TestCase):
    """Tests para el servicio ResidenteService"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.edificio = EdificioService.crear_edificio(1, 'A')
        self.apartamento = ApartamentoService.crear_apartamento(
            str(self.edificio.id), 3, '3A'
        )
    
    def test_crear_residente_valido(self):
        """Test para crear residentes válidos usando el servicio"""
        residente = ResidenteService.crear_residente(
            'Juan Carlos Pérez García',
            str(self.apartamento.id)
        )
        
        self.assertEqual(residente.nombre_completo, 'Juan Carlos Pérez García')
        self.assertEqual(residente.apartamento, self.apartamento)
    
    def test_crear_residente_apartamento_inexistente(self):
        """Test para crear residente con apartamento inexistente"""
        with self.assertRaises(ValidationError):
            ResidenteService.crear_residente(
                'Juan Carlos Pérez García',
                str(uuid.uuid4())
            )
    
    def test_buscar_residentes(self):
        """Test para buscar residentes con filtros"""
        ResidenteService.crear_residente(
            'Juan Carlos Pérez García',
            str(self.apartamento.id)
        )
        ResidenteService.crear_residente(
            'María González López',
            str(self.apartamento.id)
        )
        
        # Buscar por nombre
        residentes_juan = ResidenteService.buscar_residentes(nombre='Juan')
        self.assertEqual(len(residentes_juan), 1)
        self.assertIn('Juan', residentes_juan[0].nombre_completo)
        
        # Buscar por edificio
        residentes_edificio = ResidenteService.buscar_residentes(
            edificio_id=str(self.edificio.id)
        )
        self.assertEqual(len(residentes_edificio), 2)
    
    def test_eliminar_residente(self):
        """Test para eliminar residentes"""
        residente = ResidenteService.crear_residente(
            'Juan Carlos Pérez García',
            str(self.apartamento.id)
        )
        
        # Eliminar residente existente
        resultado = ResidenteService.eliminar_residente(str(residente.id))
        self.assertTrue(resultado)
        self.assertEqual(Residente.objects.count(), 0)
        
        # Eliminar residente inexistente
        resultado = ResidenteService.eliminar_residente(str(uuid.uuid4()))
        self.assertFalse(resultado)
    
    def test_obtener_estadisticas(self):
        """Test para obtener estadísticas del sistema"""
        # Crear algunos datos de prueba
        edificio_2 = EdificioService.crear_edificio(2, 'B')
        apartamento_2 = ApartamentoService.crear_apartamento(
            str(edificio_2.id), 3, '3B'
        )
        
        ResidenteService.crear_residente(
            'Juan Carlos Pérez García',
            str(self.apartamento.id)
        )
        
        stats = ResidenteService.obtener_estadisticas()
        
        self.assertEqual(stats['total_edificios'], 2)
        self.assertEqual(stats['total_apartamentos'], 2)
        self.assertEqual(stats['total_residentes'], 1)
        self.assertEqual(stats['edificios_con_residentes'], 1)


class APITest(APITestCase):
    """Tests para la API REST"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.client = Client()
        self.edificio = Edificio.objects.create(numero=1, puerta='A')
        self.apartamento = Apartamento.objects.create(
            edificio=self.edificio,
            piso=3,
            numero='3A'
        )
    
    def test_api_edificios_list(self):
        """Test para listar edificios via API"""
        url = reverse('residentes_api:edificios')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
    
    def test_api_edificios_create(self):
        """Test para crear edificios via API"""
        url = reverse('residentes_api:edificios')
        data = {'numero': 2, 'puerta': 'B'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
    
    def test_api_edificios_create_invalid(self):
        """Test para crear edificios inválidos via API"""
        url = reverse('residentes_api:edificios')
        data = {'numero': 1, 'puerta': 'I'}  # Regla violada
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('success', response.data)
        self.assertFalse(response.data['success'])
    
    def test_api_residentes_list(self):
        """Test para listar residentes via API"""
        url = reverse('residentes_api:residentes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
    
    def test_api_residentes_create(self):
        """Test para crear residentes via API"""
        url = reverse('residentes_api:residentes')
        data = {
            'nombre_completo': 'Juan Carlos Pérez García',
            'apartamento_id': str(self.apartamento.id)
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
    
    def test_api_estadisticas(self):
        """Test para obtener estadísticas via API"""
        url = reverse('residentes_api:estadisticas')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)


class FrontendViewsTest(TestCase):
    """Tests para las vistas del frontend"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.client = Client()
        self.edificio = Edificio.objects.create(numero=1, puerta='A')
        self.apartamento = Apartamento.objects.create(
            edificio=self.edificio,
            piso=3,
            numero='3A'
        )
    
    def test_dashboard_view(self):
        """Test para la vista del dashboard"""
        url = reverse('residentes_frontend:dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'residentes/dashboard.html')
        self.assertIn('stats', response.context)
    
    def test_subir_residente_view_get(self):
        """Test para la vista de subir residente (GET)"""
        url = reverse('residentes_frontend:subir_residente')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'residentes/subir_residente.html')
        self.assertIn('edificios', response.context)
        self.assertIn('apartamentos', response.context)
    
    def test_subir_residente_view_post(self):
        """Test para la vista de subir residente (POST)"""
        url = reverse('residentes_frontend:subir_residente')
        data = {
            'nombre_completo': 'Juan Carlos Pérez García',
            'apartamento_id': str(self.apartamento.id)
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(Residente.objects.count(), 1)
    
    def test_buscar_residentes_view(self):
        """Test para la vista de buscar residentes"""
        url = reverse('residentes_frontend:buscar_residentes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'residentes/buscar_residentes.html')
        self.assertIn('edificios', response.context)
    
    def test_gestionar_edificios_view(self):
        """Test para la vista de gestionar edificios"""
        url = reverse('residentes_frontend:gestionar_edificios')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'residentes/gestionar_edificios.html')
        self.assertIn('edificios', response.context)
    
    def test_gestionar_apartamentos_view(self):
        """Test para la vista de gestionar apartamentos"""
        url = reverse('residentes_frontend:gestionar_apartamentos')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'residentes/gestionar_apartamentos.html')
        self.assertIn('edificios', response.context)
        self.assertIn('apartamentos', response.context)


class IntegrationTest(TestCase):
    """Tests de integración para el flujo completo"""
    
    def test_flujo_completo_crear_residente(self):
        """Test para el flujo completo de crear un residente"""
        # 1. Crear edificio
        edificio = EdificioService.crear_edificio(1, 'A')
        self.assertIsNotNone(edificio)
        
        # 2. Crear apartamento
        apartamento = ApartamentoService.crear_apartamento(
            str(edificio.id), 3, '3A'
        )
        self.assertIsNotNone(apartamento)
        
        # 3. Crear residente
        residente = ResidenteService.crear_residente(
            'Juan Carlos Pérez García',
            str(apartamento.id)
        )
        self.assertIsNotNone(residente)
        
        # 4. Verificar relaciones
        self.assertEqual(residente.apartamento, apartamento)
        self.assertEqual(apartamento.edificio, edificio)
        self.assertEqual(residente.apartamento.edificio.numero, 1)
        self.assertEqual(residente.apartamento.edificio.puerta, 'A')
        self.assertEqual(residente.apartamento.piso, 3)
        self.assertEqual(residente.apartamento.numero, '3A')
    
    def test_busqueda_integrada(self):
        """Test para la búsqueda integrada de residentes"""
        # Crear datos de prueba
        edificio_1 = EdificioService.crear_edificio(1, 'A')
        edificio_2 = EdificioService.crear_edificio(25, 'I')
        
        apartamento_1 = ApartamentoService.crear_apartamento(
            str(edificio_1.id), 3, '3A'
        )
        apartamento_2 = ApartamentoService.crear_apartamento(
            str(edificio_2.id), 5, '5I'
        )
        
        ResidenteService.crear_residente(
            'Juan Carlos Pérez García',
            str(apartamento_1.id)
        )
        ResidenteService.crear_residente(
            'María González López',
            str(apartamento_2.id)
        )
        
        # Buscar por edificio
        residentes_edificio_1 = ResidenteService.buscar_residentes(
            edificio_id=str(edificio_1.id)
        )
        self.assertEqual(len(residentes_edificio_1), 1)
        self.assertEqual(residentes_edificio_1[0].nombre_completo, 'Juan Carlos Pérez García')
        
        # Buscar por nombre
        residentes_maria = ResidenteService.buscar_residentes(nombre='María')
        self.assertEqual(len(residentes_maria), 1)
        self.assertEqual(residentes_maria[0].nombre_completo, 'María González López')
        
        # Buscar por piso
        residentes_piso_3 = ResidenteService.buscar_residentes(piso=3)
        self.assertEqual(len(residentes_piso_3), 1)
        self.assertEqual(residentes_piso_3[0].apartamento.piso, 3)
