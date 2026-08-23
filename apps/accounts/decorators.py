from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages


def rol_requerido(*roles):
    """Permite el acceso solo a usuarios con alguno de los roles indicados
    (los superusuarios / admin siempre tienen acceso)."""

    def decorador(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            usuario = request.user
            if usuario.is_superuser or usuario.rol == "admin" or usuario.rol in roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "No tiene permisos para acceder a esa sección.")
            return redirect("dashboard:inicio")

        return _wrapped

    return decorador
