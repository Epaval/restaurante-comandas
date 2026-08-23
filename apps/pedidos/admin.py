from django.contrib import admin
from .models import Pedido, ItemPedido, Pago


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "tipo", "estado", "mesa", "cliente_nombre", "mesero", "creado")
    list_filter = ("tipo", "estado")
    inlines = [ItemPedidoInline]


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("pedido", "monto", "metodo", "cajero", "fecha")
