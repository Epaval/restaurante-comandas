# apps/core/context_processors.py
from apps.mesas.models import Mesa

def mesas_en_limpieza(request):
    """Context processor para mostrar mesas en limpieza en toda la app"""
    if request.user.is_authenticated:
        mesas_limpieza = Mesa.objects.filter(estado=Mesa.Estado.LIMPIEZA)
        return {
            'mesas_limpieza_count': mesas_limpieza.count()
        }
    return {
        'mesas_limpieza_count': 0
    }