#!/usr/bin/env python3
"""
Script de configuración inicial para el Sistema de Gestión de Residentes de Palme
Ejecuta las migraciones y crea un superusuario para acceder al admin
"""
import os
import sys
import django
from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model

def setup_project():
    """Configuración inicial del proyecto"""
    print("🏢 Configurando Sistema de Gestión de Residentes de Palme...")
    print("=" * 60)
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'residentes_palme.settings')
    django.setup()
    
    User = get_user_model()
    
    try:
        # Ejecutar migraciones
        print("📊 Ejecutando migraciones de la base de datos...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migraciones completadas")
        
        # Crear superusuario si no existe
        if not User.objects.filter(is_superuser=True).exists():
            print("\n👤 Creando superusuario para acceso al admin...")
            print("Por favor, ingresa los datos del superusuario:")
            
            username = input("Usuario (admin): ").strip() or "admin"
            email = input("Email: ").strip() or "admin@residentespalme.com"
            password = input("Contraseña: ").strip()
            
            if not password:
                password = "admin123"  # Contraseña por defecto
                print("⚠️  Usando contraseña por defecto: admin123")
            
            User.objects.create_superuser(username, email, password)
            print(f"✅ Superusuario '{username}' creado correctamente")
        else:
            print("✅ Superusuario ya existe")
        
        # Poblar con datos de muestra
        print("\n📝 ¿Deseas poblar la base de datos con datos de muestra? (s/n): ", end="")
        if input().lower().startswith('s'):
            print("📊 Poblando base de datos con datos de muestra...")
            execute_from_command_line(['manage.py', 'populate_sample_data', '--edificios', '5', '--apartamentos', '3', '--residentes', '2'])
            print("✅ Datos de muestra creados")
        
        print("\n" + "=" * 60)
        print("🎉 ¡Configuración completada exitosamente!")
        print("\n📱 Para acceder a la aplicación:")
        print("   • Frontend: http://localhost:8000")
        print("   • Admin Django: http://localhost:8000/admin/")
        print("   • API REST: http://localhost:8000/api/")
        print("\n🚀 Para ejecutar el servidor:")
        print("   python manage.py runserver")
        print("\n🔧 Para crear más datos de muestra:")
        print("   python manage.py populate_sample_data --edificios 10 --apartamentos 5 --residentes 3")
        
    except Exception as e:
        print(f"❌ Error durante la configuración: {e}")
        sys.exit(1)

if __name__ == '__main__':
    setup_project()
