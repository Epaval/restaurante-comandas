# desktop/launcher.py
import os
import sys
from pathlib import Path

def get_base_dir():
    """Obtiene el directorio base de la aplicación."""
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
    
    # Configurar variables de entorno
    os.environ.setdefault('DJANGO_DEBUG', 'False')
    os.environ.setdefault('ALLOWED_HOSTS', 'localhost,127.0.0.1,*')
    
    # Intentar cargar dotenv solo si existe
    try:
        from dotenv import load_dotenv
        env_file = base_dir / '.env'
        if env_file.exists():
            load_dotenv(env_file)
    except ImportError:
        pass
    
    # Usar Waitress (servidor de producción)
    try:
        from waitress import serve
        import django
        django.setup()
        from config.wsgi import application
        
        print("Iniciando servidor de producción con Waitress en http://127.0.0.1:8000")
        serve(application, host='127.0.0.1', port=8000)
    except Exception as e:
        print(f"Error al iniciar con Waitress: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()