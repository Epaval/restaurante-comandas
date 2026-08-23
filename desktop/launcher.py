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

def create_default_superuser_if_needed():
    """Crea un superusuario por defecto si no hay ningún usuario."""
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
            print("   Usuario: admin")
            print("   Contraseña: admin123")
            print("   ⚠️  CAMBIA LA CONTRASEÑA DESPUÉS DE INGRESAR!")
    except Exception as e:
        print(f"⚠️  No se pudo crear superusuario automático: {e}")

def main():
    try:
        # MODO MANTENIMIENTO
        if len(sys.argv) > 1:
            from django.core.management import execute_from_command_line
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
            sys.path.insert(0, str(get_base_dir()))
            print(f"Ejecutando comando: {' '.join(sys.argv[1:])}")
            execute_from_command_line(sys.argv)
            sys.exit(0)

        # MODO NORMAL
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        base_dir = get_base_dir()
        app_data_dir = get_app_data_dir()
        sys.path.insert(0, str(base_dir))
        os.environ.setdefault('DJANGO_DEBUG', 'False')
        os.environ.setdefault('ALLOWED_HOSTS', 'localhost,127.0.0.1,*')

        from django.core.management import execute_from_command_line
        
        print("Verificando y aplicando migraciones de la base de datos...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])

        import django
        django.setup()

        # 🔥 CORRECCIÓN CRÍTICA PARA WINDOWS:
        # Forzar que MEDIA_ROOT apunte a la carpeta del .exe, no a _internal
        from django.conf import settings
        settings.MEDIA_ROOT = app_data_dir / 'media'
        settings.MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
        print(f"📁 MEDIA_ROOT configurado en: {settings.MEDIA_ROOT}")

        # Crear superusuario por defecto si no hay ninguno
        create_default_superuser_if_needed()

        from waitress import serve
        from config.wsgi import application

        print("✅ Servidor iniciado en http://127.0.0.1:8000")
        print("🌐 Abriendo navegador automáticamente...")
        
        time.sleep(1.5)
        webbrowser.open('http://127.0.0.1:8000')

        serve(application, host='127.0.0.1', port=8000)

    except Exception as e:
        error_msg = f"Error crítico: {str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error al iniciar Restaurante", error_msg)
        except:
            pass
        input("Presiona Enter para cerrar...")
        sys.exit(1)

if __name__ == '__main__':
    main()