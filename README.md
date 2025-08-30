# 🏢 Sistema de Gestión de Residentes de Palme

Sistema web completo para la gestión de residentes en un complejo residencial de 32 edificios con 8 pisos cada uno. Desarrollado específicamente para el personal de conserjería con interfaz completamente en español.

## ✨ Características Principales

### 🏗️ **Gestión de Infraestructura**
- **32 Edificios** numerados del 1 al 32
- **8 Pisos** por edificio
- **2 Apartamentos** por piso (puertas A/B para edificios 1-22, I/D para 23-32)
- **Total: 512 apartamentos** en todo el complejo

### 👥 **Gestión de Residentes**
- **Hasta 6 residentes** por apartamento
- **1 Propietario** + **5 Inquilinos** máximo
- **Fotos de residentes** con almacenamiento en servidor
- **Búsqueda avanzada** por nombre, edificio, piso y apartamento

### 🎯 **Funcionalidades del Sistema**
- ✅ **Subir residentes** con foto y asignación a apartamento
- ✅ **Buscar residentes** con filtros múltiples
- ✅ **Ver detalles completos** de cada residente
- ✅ **Eliminar residentes** con confirmación
- ✅ **Gestión de edificios** y apartamentos
- ✅ **Estadísticas del complejo** en tiempo real

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 4.2.7 + Django REST Framework
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend**: Django Templates + Bootstrap 5 + Font Awesome
- **Arquitectura**: Clean Architecture + SOLID Principles
- **Contenedores**: Docker + Docker Compose
- **Python**: 3.9+

## 🚀 Instalación y Configuración

### **Requisitos Previos**
- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- Git

### **Instalación Rápida**

#### **1. Clonar el Repositorio**
```bash
git clone <tu-repositorio-github>
cd residentesPalme
```

#### **2. Configurar Entorno Virtual**
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

#### **3. Instalar Dependencias**
```bash
pip install -r requirements.txt
```

#### **4. Configurar Variables de Entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

#### **5. Ejecutar Migraciones**
```bash
python manage.py makemigrations
python manage.py migrate
```

#### **6. Crear Superusuario**
```bash
python manage.py createsuperuser
```

#### **7. Poblar Datos de Ejemplo (Opcional)**
```bash
python manage.py populate_sample_data
```

#### **8. Ejecutar el Servidor**
```bash
python manage.py runserver
```

### **Acceso al Sistema**
- **Frontend**: http://localhost:8000/
- **Admin Django**: http://localhost:8000/admin/
- **API REST**: http://localhost:8000/api/

## 🐳 Instalación con Docker

### **Ejecutar con Docker Compose**
```bash
docker-compose up -d
```

### **Construir Imagen Personalizada**
```bash
docker build -t residentes-palme .
docker run -p 8000:8000 residentes-palme
```

## 📁 Estructura del Proyecto

```
residentesPalme/
├── residentes/                 # Aplicación principal
│   ├── models.py              # Modelos de datos
│   ├── views.py               # Vistas de la API
│   ├── frontend_views.py      # Vistas del frontend
│   ├── services.py            # Lógica de negocio
│   ├── serializers.py         # Serializadores DRF
│   ├── admin.py               # Configuración del admin
│   └── migrations/            # Migraciones de base de datos
├── templates/                  # Plantillas HTML
│   ├── base.html              # Plantilla base
│   └── residentes/            # Plantillas específicas
├── static/                     # Archivos estáticos
├── media/                      # Archivos subidos por usuarios
├── residentes_palme/          # Configuración del proyecto
├── requirements.txt            # Dependencias Python
├── Dockerfile                  # Configuración Docker
├── docker-compose.yml          # Orquestación Docker
├── Makefile                    # Comandos de automatización
└── README.md                   # Este archivo
```

## 🔧 Comandos Útiles

### **Desarrollo**
```bash
make run              # Ejecutar servidor de desarrollo
make migrate          # Ejecutar migraciones
make makemigrations  # Crear nuevas migraciones
make test            # Ejecutar tests
make shell           # Abrir shell de Django
```

### **Datos**
```bash
make populate        # Poblar datos de ejemplo
make clear-db        # Limpiar base de datos
make superuser       # Crear superusuario
```

### **Docker**
```bash
make docker-build    # Construir imagen Docker
make docker-run      # Ejecutar con Docker
make docker-stop     # Detener contenedores
```

## 📊 API REST

### **Endpoints Principales**
- `GET /api/edificios/` - Listar edificios
- `POST /api/edificios/` - Crear edificio
- `GET /api/apartamentos/` - Listar apartamentos
- `POST /api/apartamentos/` - Crear apartamento
- `GET /api/residentes/` - Listar residentes
- `POST /api/residentes/` - Crear residente
- `GET /api/estadisticas/` - Estadísticas del sistema

### **Ejemplo de Uso**
```bash
# Obtener estadísticas
curl http://localhost:8000/api/estadisticas/

# Crear residente
curl -X POST http://localhost:8000/api/residentes/ \
  -H "Content-Type: application/json" \
  -d '{"nombre_completo": "Juan Pérez", "tipo": "propietario", "apartamento_id": "uuid"}'
```

## 🧪 Testing

### **Ejecutar Tests**
```bash
# Tests unitarios
python manage.py test residentes.tests

# Tests de integración
python manage.py test residentes.test_integration

# Cobertura de código
coverage run --source='.' manage.py test
coverage report
```

## 🚀 Despliegue en Producción

### **Configuración de Producción**
1. Cambiar `DEBUG = False` en settings
2. Configurar `ALLOWED_HOSTS`
3. Usar PostgreSQL en lugar de SQLite
4. Configurar variables de entorno de producción
5. Usar servidor WSGI (Gunicorn/uWSGI)
6. Configurar servidor web (Nginx/Apache)

### **Variables de Entorno de Producción**
```bash
DEBUG=False
SECRET_KEY=tu-clave-secreta-super-segura
DATABASE_URL=postgresql://usuario:password@host:puerto/db
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

Desarrollado para el Complejo Residencial de Palme.

## 📞 Soporte

Para soporte técnico o consultas:
- Crear un issue en GitHub
- Contactar al equipo de desarrollo

---

**¡Gracias por usar el Sistema de Gestión de Residentes de Palme!** 🏢✨
