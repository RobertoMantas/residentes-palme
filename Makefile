# Makefile para el Sistema de Gestión de Residentes de Palme
# Comandos útiles para desarrollo y despliegue

.PHONY: help install setup run test clean docker-build docker-run docker-stop populate-data

# Variables
PYTHON = python3
PIP = pip3
MANAGE = python manage.py
PROJECT_NAME = residentes_palme

help: ## Mostrar esta ayuda
	@echo "🏢 Sistema de Gestión de Residentes de Palme"
	@echo "=============================================="
	@echo ""
	@echo "Comandos disponibles:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Instalar dependencias
	@echo "📦 Instalando dependencias..."
	$(PIP) install -r requirements.txt
	@echo "✅ Dependencias instaladas"

setup: ## Configuración inicial del proyecto
	@echo "🔧 Configurando proyecto..."
	$(PYTHON) setup.py
	@echo "✅ Proyecto configurado"

run: ## Ejecutar servidor de desarrollo
	@echo "🚀 Iniciando servidor de desarrollo..."
	$(MANAGE) runserver

test: ## Ejecutar tests
	@echo "🧪 Ejecutando tests..."
	$(MANAGE) test residentes.tests --verbosity=2

test-coverage: ## Ejecutar tests con cobertura
	@echo "🧪 Ejecutando tests con cobertura..."
	coverage run --source='.' manage.py test
	coverage report
	coverage html

clean: ## Limpiar archivos temporales
	@echo "🧹 Limpiando archivos temporales..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/
	@echo "✅ Limpieza completada"

migrations: ## Crear migraciones
	@echo "📊 Creando migraciones..."
	$(MANAGE) makemigrations

migrate: ## Aplicar migraciones
	@echo "📊 Aplicando migraciones..."
	$(MANAGE) migrate

superuser: ## Crear superusuario
	@echo "👤 Creando superusuario..."
	$(MANAGE) createsuperuser

populate-data: ## Poblar base de datos con datos de muestra
	@echo "📝 Poblando base de datos..."
	@echo "📊 Estructura: 8 pisos × 2 apartamentos por piso = 16 apartamentos por edificio"
	$(MANAGE) populate_sample_data --edificios 10 --residentes 3

collectstatic: ## Recolectar archivos estáticos
	@echo "📁 Recolectando archivos estáticos..."
	$(MANAGE) collectstatic --noinput

# Comandos Docker
docker-build: ## Construir imagen Docker
	@echo "🐳 Construyendo imagen Docker..."
	docker build -t $(PROJECT_NAME) .

docker-run: ## Ejecutar con Docker Compose
	@echo "🐳 Ejecutando con Docker Compose..."
	docker-compose up --build

docker-stop: ## Parar servicios Docker
	@echo "🐳 Parando servicios Docker..."
	docker-compose down

docker-logs: ## Ver logs de Docker
	@echo "🐳 Mostrando logs..."
	docker-compose logs -f

# Comandos de desarrollo
shell: ## Abrir shell de Django
	@echo "🐍 Abriendo shell de Django..."
	$(MANAGE) shell

check: ## Verificar estado del proyecto
	@echo "🔍 Verificando estado del proyecto..."
	$(MANAGE) check
	$(MANAGE) check --deploy

lint: ## Ejecutar linting (requiere flake8)
	@echo "🔍 Ejecutando linting..."
	flake8 residentes/ residentes_palme/ --max-line-length=120

format: ## Formatear código (requiere black)
	@echo "🎨 Formateando código..."
	black residentes/ residentes_palme/

# Comandos de producción
production-setup: ## Configurar para producción
	@echo "🚀 Configurando para producción..."
	export DEBUG=False
	export SECRET_KEY=your-production-secret-key
	$(MANAGE) collectstatic --noinput
	@echo "✅ Configuración de producción completada"

gunicorn: ## Ejecutar con Gunicorn
	@echo "🚀 Ejecutando con Gunicorn..."
	gunicorn $(PROJECT_NAME).wsgi:application --bind 0.0.0.0:8000 --workers 3

# Comandos de base de datos
db-reset: ## Resetear base de datos
	@echo "🗑️  Reseteando base de datos..."
	$(MANAGE) flush --noinput
	@echo "✅ Base de datos reseteada"

db-backup: ## Crear backup de la base de datos
	@echo "💾 Creando backup..."
	$(MANAGE) dumpdata > backup_$(shell date +%Y%m%d_%H%M%S).json
	@echo "✅ Backup creado"

# Comandos de monitoreo
status: ## Mostrar estado del sistema
	@echo "📊 Estado del sistema:"
	@echo "  • Python: $(shell python3 --version)"
	@echo "  • Django: $(shell python3 -c "import django; print(django.get_version())")"
	@echo "  • Base de datos: $(shell python3 -c "from django.db import connection; print(connection.vendor)")"

# Comando por defecto
.DEFAULT_GOAL := help
