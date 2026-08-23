# apps/mesas/urls.py
from django.urls import path
from . import views

app_name = 'mesas'

urlpatterns = [
    path('', views.lista_mesas, name='lista'),
    path('seleccionar/<int:mesa_id>/', views.seleccionar_mesa, name='seleccionar_mesa'),
    path('cambiar-estado/<int:mesa_id>/', views.cambiar_estado, name='cambiar_estado'),
    path('limpieza/', views.panel_limpieza, name='panel_limpieza'),
    path('completar-limpieza/<int:mesa_id>/', views.completar_limpieza, name='completar_limpieza'),
]