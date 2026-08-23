# desktop/launcher.py
import os
import sys
from pathlib import Path

def get_base_dir():
    """Obtiene el directorio base de la aplicación (funciona en desarrollo y empaquetado)."""
    if getattr(sys, 'frozen', False):
        # Ejecutable empaquetado con PyInstaller
        return Path(sys._MEIPASS)
    else:
        # Ejecución desde código fuente
        return Path(__file__).resolve().parent.parent

def main():
    # Configurar entorno Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    # Agregar el directorio de la aplicación al path
    base_dir = get_base_dir()
    sys.path.insert(0, str(base_dir))
    
    # Configurar variables de entorno para el ejecutable
    os.environ.setdefault('DJANGO_DEBUG', 'False')
    os.environ.setdefault('ALLOWED_HOSTS', 'localhost,127.0.0.1,*')
    
    # Intentar cargar dotenv solo si existe (opcional)
    try:
        from dotenv import load_dotenv
        env_file = base_dir / '.env'
        if env_file.exists():
            load_dotenv(env_file)
    except ImportError:
        pass  # No usar dotenv en el ejecutable empaquetado
    
    # Usar Waitress (servidor de producción) en lugar de runserver
    try:
        from waitress import serve
        from config.wsgi import application
        
        print("Iniciando servidor de producción con Waitress en http://127.0.0.1:8000")
        serve(application, host='127.0.0.1', port=8000)
    except ImportError:
        # Fallback a runserver con --noreload si waitress no está disponible
        from django.core.management import execute_from_command_line
        print("Waitress no disponible, usando runserver en modo desarrollo...")
        sys.argv = ['manage.py', 'runserver', '127.0.0.1:8000', '--noreload']
        execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()