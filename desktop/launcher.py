# desktop/launcher.py
import os
import sys
from pathlib import Path

def main():
    # Configurar entorno Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    # Agregar el directorio de la aplicación al path
    base_dir = Path(sys.argv[0]).parent
    sys.path.insert(0, str(base_dir))
    
    # Configurar variables de entorno para el ejecutable
    os.environ.setdefault('DJANGO_DEBUG', 'False')
    os.environ.setdefault('ALLOWED_HOSTS', 'localhost,127.0.0.1')
    
    # Intentar cargar dotenv solo si existe (opcional)
    try:
        from dotenv import load_dotenv
        env_file = base_dir / '.env'
        if env_file.exists():
            load_dotenv(env_file)
    except ImportError:
        pass  # No usar dotenv en el ejecutable empaquetado
    
    # Ejecutar el servidor
    from django.core.management import execute_from_command_line
    sys.argv = ['manage.py', 'runserver', '127.0.0.1:8000']
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()