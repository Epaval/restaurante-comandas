# config/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.views.static import serve
from django.conf import settings

def redirect_to_dashboard(request):
    if request.user.is_authenticated:
        return redirect("dashboard:inicio")
    return redirect("login")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", include("apps.dashboard.urls")),
    path("mesas/", include("apps.mesas.urls")),
    path("pedidos/", include("apps.pedidos.urls")),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", redirect_to_dashboard, name="home"),
]

# 🔥 Servir archivos media SIEMPRE, ignorando el estado de DEBUG
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]