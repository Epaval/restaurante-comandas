# desktop/launcher.py
import os
import sys
import traceback
from pathlib import Path

def get_base_dir():
    """Obtiene el directorio base de la aplicación."""
    if getattr(sys, 'frozen', False):
        # Ejecutable empaquetado con PyInstaller
        return Path(sys._MEIPASS)
    else:
        # Ejecución desde código fuente
        return Path(__file__).resolve().parent.parent

def get_app_data_dir():
    """Obtiene el directorio de datos de la aplicación (donde se guardan logs y BD)."""
    if getattr(sys, 'frozen', False):
        # En ejecutable: usar carpeta junto al .exe
        return Path(sys.executable).parent
    else:
        # En desarrollo: usar carpeta del proyecto
        return Path(__file__).resolve().parent.parent

def setup_logging():
    """Configura el logging a archivo."""
    import logging
    log_dir = get_app_data_dir()
    log_file = log_dir / 'restaurante.log'
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def main():
    logger = None
    try:
        logger = setup_logging()
        logger.info("Iniciando aplicación Restaurante...")
        
        # Configurar entorno Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        
        # Agregar el directorio de la aplicación al path
        base_dir = get_base_dir()
        sys.path.insert(0, str(base_dir))
        
        logger.info(f"Base directory: {base_dir}")
        logger.info(f"App data directory: {get_app_data_dir()}")
        
        # Configurar variables de entorno
        os.environ.setdefault('DJANGO_DEBUG', 'False')
        os.environ.setdefault('ALLOWED_HOSTS', 'localhost,127.0.0.1,*')
        
        # Intentar cargar dotenv solo si existe
        try:
            from dotenv import load_dotenv
            env_file = base_dir / '.env'
            if env_file.exists():
                load_dotenv(env_file)
                logger.info("Cargado .env")
        except ImportError:
            pass
        
        # Usar Waitress (servidor de producción)
        from waitress import serve
        import django
        django.setup()
        logger.info("Django setup completado")
        
        from config.wsgi import application
        
        logger.info("Iniciando servidor Waitress en http://127.0.0.1:8000")
        print("Servidor iniciado en http://127.0.0.1:8000")
        print("Presiona Ctrl+C para detener")
        
        serve(application, host='127.0.0.1', port=8000)
        
    except Exception as e:
        error_msg = f"Error crítico: {str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        
        if logger:
            logger.error(error_msg)
        
        # Mostrar error al usuario en una ventana
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error al iniciar Restaurante", error_msg)
        except:
            pass
        
        # Esperar para que el usuario pueda leer el error
        input("Presiona Enter para cerrar...")
        sys.exit(1)

if __name__ == '__main__':
    main()