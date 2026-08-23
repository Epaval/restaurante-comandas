from django.urls import path
from . import views
from apps.pedidos import views as pedidos_views

app_name = "dashboard"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("admin/", views.panel_admin, name="admin"),
    path("mesero/", views.panel_mesero, name="mesero"),
    path("cocina/", pedidos_views.panel_cocina, name="cocina"),
    path("caja/", pedidos_views.panel_caja, name="caja"),
    path("entregas/", pedidos_views.panel_entregas, name="entregas"),
]
