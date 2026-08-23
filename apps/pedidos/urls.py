# apps/pedidos/urls.py
from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    # Crear pedido - ambas rutas apuntan a la misma vista
    path('crear/', views.crear_pedido_rapido, name='crear'),  # ✅ Agregar esta línea
    path('nuevo/', views.crear_pedido_rapido, name='nuevo'),
    
    # Detalle y acciones del pedido
    path('<int:pedido_id>/', views.detalle_pedido, name='detalle'),
    path('<int:pedido_id>/enviar-cocina/', views.enviar_a_cocina, name='enviar_cocina'),
    path('<int:pedido_id>/solicitar-cuenta/', views.solicitar_cuenta, name='solicitar_cuenta'),
    path('<int:pedido_id>/procesar-pago/', views.procesar_pago, name='procesar_pago'),
    path('item/<int:item_id>/cambiar-estado/', views.cambiar_estado_item, name='cambiar_estado_item'),
    # Acciones de mesa
    path('mesa/<int:mesa_id>/completar-limpieza/', views.completar_limpieza, name='completar_limpieza'),
    
    # API endpoints (AJAX)
    path('api/agregar-item/<int:pedido_id>/', views.agregar_item_ajax, name='agregar_item'),
    path('api/eliminar-item/<int:item_id>/', views.eliminar_item_ajax, name='eliminar_item'),
    path('<int:pedido_id>/cancelar/', views.cancelar_pedido, name='cancelar_pedido'),

]