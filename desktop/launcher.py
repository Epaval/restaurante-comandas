# desktop/launcher.py
import os
import sys
import traceback
import webbrowser
import time
from pathlib import Path

def get_base_dir():
    """Obtiene el directorio base de la aplicación (código fuente congelado)."""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    else:
        return Path(__file__).resolve().parent.parent

def get_app_data_dir():
    """Obtiene el directorio de datos persistentes (BD, media, logs)."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent  # Carpeta donde está el .exe
    else:
        return Path(__file__).resolve().parent.parent

def main():
    try:
        # ==========================================
        # 1. DEFINIR RUTAS PRIMERO
        # ==========================================
        base_dir = get_base_dir()
        app_data_dir = get_app_data_dir()
        sys.path.insert(0, str(base_dir))

        # ==========================================
        # 2. CONFIGURAR ENTORNO ANTES DE IMPORTAR DJANGO
        # ==========================================
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        os.environ.setdefault('DJANGO_DEBUG', 'True')
        os.environ.setdefault('ALLOWED_HOSTS', 'localhost,127.0.0.1,*')

        # ==========================================
        # 3. IMPORTAR Y FORZAR CONFIGURACIÓN DE DJANGO
        # ==========================================
        import django
        from django.conf import settings

        # 🔥 FORZAR RUTAS CORRECTAS ANTES DE CUALQUIER OPERACIÓN
        settings.DATABASES['default']['NAME'] = app_data_dir / 'db.sqlite3'
        settings.MEDIA_ROOT = app_data_dir / 'media'
        
        # Crear carpetas si no existen
        settings.MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

        # ==========================================
        # 4. INICIALIZAR DJANGO CON LAS RUTAS YA CORREGIDAS
        # ==========================================
        django.setup()

        # ==========================================
        # 5. EJECUTAR MIGRACIONES (AHORA SÍ USARÁ LA BD CORRECTA)
        # ==========================================
        print("⏳ Verificando y aplicando migraciones de la base de datos...")
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        
        print(f"💾 Base de datos en: {settings.DATABASES['default']['NAME']}")
        print(f"📁 Archivos multimedia en: {settings.MEDIA_ROOT}")

        # ==========================================
        # 6. CREAR SUPERUSUARIO SI ES NECESARIO
        # ==========================================
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if User.objects.count() == 0:
                print("⚠️  No hay usuarios. Creando superusuario por defecto...")
                User.objects.create_superuser(
                    username='admin',
                    email='admin@restaurante.com',
                    password='admin123',
                    rol='admin'  # Ajusta según tu modelo de Usuario
                )
                print("✅ Superusuario creado:")
                print("   👤 Usuario: admin")
                print("   🔑 Contraseña: admin123")
        except Exception as e:
            print(f"⚠️  No se pudo crear superusuario automático: {e}")

        # ==========================================
        # 7. INICIAR SERVIDOR
        # ==========================================
        from waitress import serve
        from config.wsgi import application

        print("\n✅ ¡Servidor iniciado exitosamente!")
        print("🌐 Abriendo navegador en http://127.0.0.1:8000 ...")
        
        time.sleep(1.5)
        webbrowser.open('http://127.0.0.1:8000')

        serve(application, host='127.0.0.1', port=8000)

    except Exception as e:
        # ==========================================
        # MANEJO DE ERRORES
        # ==========================================
        error_msg = f"Error crítico al iniciar:\n{str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error en Restaurante App", error_msg)
        except Exception:
            pass
        input("\nPresiona Enter para cerrar la ventana...")
        sys.exit(1)

if __name__ == '__main__':
    main()