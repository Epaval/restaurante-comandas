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
        # En ejecutable: usar la carpeta donde está el .exe
        return Path(sys.executable).parent
    else:
        # En desarrollo: usar la carpeta raíz del proyecto
        return Path(__file__).resolve().parent.parent

def create_default_superuser_if_needed():
    """Crea un superusuario por defecto si no hay ningún usuario en la BD."""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if User.objects.count() == 0:
            print("⚠️  No hay usuarios. Creando superusuario por defecto...")
            User.objects.create_superuser(
                username='admin',
                email='admin@restaurante.com',
                password='admin123',
                rol='admin'  # Ajusta si tu modelo exige un valor diferente
            )
            print("✅ Superusuario creado:")
            print("   👤 Usuario: admin")
            print("   🔑 Contraseña: admin123")
            print("   ⚠️  ¡CAMBIA LA CONTRASEÑA DESPUÉS DE INGRESAR!")
    except Exception as e:
        print(f"⚠️  No se pudo crear superusuario automático: {e}")

def main():
    try:
        # ==========================================
        # MODO MANTENIMIENTO (Ej: Restaurante.exe migrate)
        # ==========================================
        if len(sys.argv) > 1:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
            sys.path.insert(0, str(get_base_dir()))
            from django.core.management import execute_from_command_line
            print(f"⚙️  Ejecutando comando: {' '.join(sys.argv[1:])}")
            execute_from_command_line(sys.argv)
            sys.exit(0)

        # ==========================================
        # MODO NORMAL (Iniciar aplicación)
        # ==========================================
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        
        base_dir = get_base_dir()
        app_data_dir = get_app_data_dir()
        
        # Asegurar que el código fuente sea encontrable
        sys.path.insert(0, str(base_dir))
        
        # Configuración de entorno
        os.environ.setdefault('DJANGO_DEBUG', 'True')  # True ayuda a servir media localmente
        os.environ.setdefault('ALLOWED_HOSTS', 'localhost,127.0.0.1,*')

        print("⏳ Verificando y aplicando migraciones de la base de datos...")
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])

        import django
        django.setup()

        # ==========================================
        # 🔥 CORRECCIONES CRÍTICAS PARA ESCRITORIO (WINDOWS)
        # ==========================================
        from django.conf import settings
        
        # 1. Forzar que la BD se guarde junto al .exe (NO en _internal)
        settings.DATABASES['default']['NAME'] = app_data_dir / 'db.sqlite3'
        
        # 2. Forzar que MEDIA se guarde junto al .exe
        settings.MEDIA_ROOT = app_data_dir / 'media'
        
        # Crear las carpetas si no existen
        settings.MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
        
        print(f"💾 Base de datos en: {settings.DATABASES['default']['NAME']}")
        print(f"📁 Archivos multimedia en: {settings.MEDIA_ROOT}")

        # Crear superusuario si es la primera vez
        create_default_superuser_if_needed()

        # ==========================================
        # INICIAR SERVIDOR
        # ==========================================
        from waitress import serve
        from config.wsgi import application

        print("\n✅ ¡Servidor iniciado exitosamente!")
        print("🌐 Abriendo navegador en http://127.0.0.1:8000 ...")
        
        time.sleep(1.5)
        webbrowser.open('http://127.0.0.1:8000')

        # Mantener el servidor corriendo
        serve(application, host='127.0.0.1', port=8000)

    except Exception as e:
        # ==========================================
        # MANEJO DE ERRORES AMIGABLE PARA EL USUARIO
        # ==========================================
        error_msg = f"Error crítico al iniciar:\n{str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()  # Ocultar ventana principal de tkinter
            messagebox.showerror("Error en Restaurante App", error_msg)
        except Exception:
            pass  # Si falla tkinter, al menos ya se imprimió en consola
            
        input("\nPresiona Enter para cerrar la ventana...")
        sys.exit(1)

if __name__ == '__main__':
    main()