# config/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect  # <-- Agrega esta importación

# Función simple para redirigir la raíz
def redirect_to_dashboard(request):
    if request.user.is_authenticated:
        return redirect("dashboard:inicio")
    return redirect("login")

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', lambda request: redirect('login'), name='home'),
    
    # Dashboard personalizado bajo /dashboard/
    path("dashboard/", include("apps.dashboard.urls")),
    
    path("mesas/", include("apps.mesas.urls")),
    path("pedidos/", include("apps.pedidos.urls")),
    
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    
    # Redirección de la raíz "/" 
    path("", redirect_to_dashboard, name="home"),  # <-- Agrega esta línea
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)