"""
Comando de Django para poblar la base de datos con datos de muestra
Útil para desarrollo, testing y demostración
"""
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from residentes.services import EdificioService, ApartamentoService, ResidenteService
from residentes.models import Edificio, Apartamento, Residente
import random


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de muestra para el sistema de gestión de residentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--edificios',
            type=int,
            default=10,
            help='Número de edificios a crear (por defecto: 10)'
        )
        parser.add_argument(
            '--residentes',
            type=int,
            default=3,
            help='Número máximo de inquilinos por apartamento (por defecto: 3)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpiar todos los datos existentes antes de poblar'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Limpiando datos existentes...')
            Residente.objects.all().delete()
            Apartamento.objects.all().delete()
            Edificio.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Datos limpiados correctamente'))

        # Nombres de muestra para residentes
        nombres_muestra = [
            'Juan Carlos Pérez García',
            'María González López',
            'Carlos Rodríguez Martín',
            'Ana Fernández Jiménez',
            'Luis Sánchez Moreno',
            'Carmen Torres Ruiz',
            'Miguel Ángel Díaz Vega',
            'Isabel Morales Castro',
            'Francisco Javier Ruiz Navarro',
            'Elena Jiménez Hidalgo',
            'Antonio López Mendoza',
            'Rosa María Vega Ortega',
            'José Manuel Castro Paredes',
            'Teresa Navarro Delgado',
            'Manuel Ortega Herrera',
            'Pilar Herrera Méndez',
            'Javier Méndez Silva',
            'Concepción Silva Vargas',
            'Pedro Vargas Ríos',
            'Lucía Ríos Campos'
        ]

        edificios_creados = []
        apartamentos_creados = []
        residentes_creados = []

        # Crear edificios
        self.stdout.write('Creando edificios...')
        for i in range(1, min(options['edificios'] + 1, 33)):
            try:
                edificio = EdificioService.crear_edificio(i)
                edificios_creados.append(edificio)
                self.stdout.write(f'  ✓ Edificio {i} creado')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ⚠ Edificio {i} ya existe: {e}'))

        # Crear apartamentos - EXACTAMENTE 2 por piso (uno para cada tipo de puerta)
        self.stdout.write('Creando apartamentos...')
        for edificio in edificios_creados:
            for piso in range(1, 9):  # 8 pisos por edificio
                # Crear exactamente 2 apartamentos por piso
                if edificio.numero <= 22:
                    # Edificios 1-22: puertas A y B
                    puertas_piso = ['A', 'B']
                else:
                    # Edificios 23-32: puertas I y D
                    puertas_piso = ['I', 'D']
                
                for puerta in puertas_piso:
                    try:
                        numero = f"{piso}{puerta}"
                        apartamento = ApartamentoService.crear_apartamento(
                            str(edificio.id), piso, numero
                        )
                        apartamentos_creados.append(apartamento)
                        self.stdout.write(f'  ✓ Apartamento {numero} en Edificio {edificio.numero} Piso {piso}')
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'  ⚠ Apartamento {numero} ya existe: {e}'))

        # Crear residentes - 1 propietario + hasta N inquilinos por apartamento
        self.stdout.write('Creando residentes...')
        for apartamento in apartamentos_creados:
            # Crear 1 propietario obligatorio
            try:
                nombre_propietario = random.choice(nombres_muestra)
                propietario = ResidenteService.crear_residente(
                    nombre_completo=nombre_propietario,
                    apartamento_id=str(apartamento.id),
                    tipo='propietario'
                )
                residentes_creados.append(propietario)
                self.stdout.write(f'  ✓ Propietario {nombre_propietario} en {apartamento}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ⚠ Error creando propietario: {e}'))
            
            # Crear inquilinos adicionales (hasta el máximo especificado)
            num_inquilinos = random.randint(0, min(options['residentes'], 5))  # Máximo 5 inquilinos
            for _ in range(num_inquilinos):
                try:
                    nombre_inquilino = random.choice(nombres_muestra)
                    inquilino = ResidenteService.crear_residente(
                        nombre_completo=nombre_inquilino,
                        apartamento_id=str(apartamento.id),
                        tipo='inquilino'
                    )
                    residentes_creados.append(inquilino)
                    self.stdout.write(f'  ✓ Inquilino {nombre_inquilino} en {apartamento}')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  ⚠ Error creando inquilino: {e}'))

        # Mostrar resumen
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('RESUMEN DE DATOS CREADOS'))
        self.stdout.write('='*50)
        self.stdout.write(f'Edificios: {len(edificios_creados)}')
        self.stdout.write(f'Apartamentos: {len(apartamentos_creados)}')
        self.stdout.write(f'Residentes: {len(residentes_creados)}')
        self.stdout.write('='*50)
        
        # Calcular apartamentos esperados
        apartamentos_esperados = len(edificios_creados) * 8 * 2  # 8 pisos × 2 apartamentos por piso
        self.stdout.write(f'Apartmentos esperados: {apartamentos_esperados} (8 pisos × 2 aptos × {len(edificios_creados)} edificios)')

        # Mostrar estadísticas
        try:
            stats = ResidenteService.obtener_estadisticas()
            self.stdout.write(f'\nEstadísticas del sistema:')
            self.stdout.write(f'  • Total edificios: {stats["total_edificios"]}')
            self.stdout.write(f'  • Total apartamentos: {stats["total_apartamentos"]}')
            self.stdout.write(f'  • Total residentes: {stats["total_residentes"]}')
            self.stdout.write(f'  • Total propietarios: {stats["total_propietarios"]}')
            self.stdout.write(f'  • Total inquilinos: {stats["total_inquilinos"]}')
            self.stdout.write(f'  • Edificios con residentes: {stats["edificios_con_residentes"]}')
            self.stdout.write(f'  • Apartamentos con propietario: {stats["apartamentos_con_propietario"]}')
            self.stdout.write(f'  • Apartamentos sin propietario: {stats["apartamentos_sin_propietario"]}')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'No se pudieron obtener estadísticas: {e}'))

        self.stdout.write('\n' + self.style.SUCCESS('¡Base de datos poblada correctamente!'))
        self.stdout.write('Puedes acceder a la aplicación en: http://localhost:8000')
        self.stdout.write('Admin Django en: http://localhost:8000/admin/')
