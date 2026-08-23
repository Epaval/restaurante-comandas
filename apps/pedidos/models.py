from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.mesas.models import Mesa
from apps.menu.models import Producto



class Pedido(models.Model):
    class Tipo(models.TextChoices):
        MESA = "mesa", "En el local"
        DELIVERY = "delivery", "Delivery"
        PARA_LLEVAR = "llevar", "Para llevar"

    class Estado(models.TextChoices):
        BORRADOR = "borrador", "Borrador"  # Nuevo: mientras se toman productos
        PENDIENTE = "pendiente", "Pendiente"
        PREPARACION = "preparacion", "En preparación"
        LISTO = "listo", "Listo para servir"
        SERVIDO = "servido", "Servido"
        CUENTA_SOLICITADA = "cuenta", "Cuenta solicitada"
        PAGADO = "pagado", "Pagado"
        CANCELADO = "cancelado", "Cancelado"
        ENTREGADO = "entregado", "Entregado"

    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.MESA)
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.BORRADOR  # Cambiado
    )
    
    mesa = models.ForeignKey(
        'mesas.Mesa',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos'
    )
    mesero = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos_mesero'
    )
    
    # Datos del cliente (se llenan al enviar a cocina)
    cliente_nombre = models.CharField(max_length=100, blank=True, default="")
    cliente_telefono = models.CharField(max_length=20, blank=True, default="")
    cliente_direccion = models.TextField(blank=True, default="")
    
    notas = models.TextField(blank=True, default="")
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    enviado_cocina_en = models.DateTimeField(null=True, blank=True)
    listo_en = models.DateTimeField(null=True, blank=True)
    pagado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        return f"Pedido #{self.id} - {self.get_estado_display()}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    def enviar_a_cocina(self, cliente_nombre, cliente_telefono=""):
        """Envía el pedido a cocina y actualiza la mesa"""
        from django.utils import timezone
        
        self.cliente_nombre = cliente_nombre
        self.cliente_telefono = cliente_telefono
        self.estado = self.Estado.PREPARACION
        self.enviado_cocina_en = timezone.now()
        self.save()
        
        # Marcar mesa como ocupada
        if self.mesa:
            self.mesa.marcar_ocupada()

    def marcar_listo(self):
        """Cocina marca el pedido como listo"""
        from django.utils import timezone
        self.estado = self.Estado.LISTO
        self.listo_en = timezone.now()
        self.save()

    def solicitar_cuenta(self):
        """Cliente pide la cuenta"""
        self.estado = self.Estado.CUENTA_SOLICITADA
        self.save()

    def marcar_pagado(self):
        """Pedido pagado"""
        from django.utils import timezone
        self.estado = self.Estado.PAGADO
        self.pagado_en = timezone.now()
        self.save()
        
        # Solicitar limpieza de la mesa
        if self.mesa:
            self.mesa.solicitar_limpieza()

class ItemPedido(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        EN_PREPARACION = "en_preparacion", "En preparación"
        LISTO = "listo", "Listo"

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    notas = models.CharField(max_length=255, blank=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)

    @property
    def subtotal(self):
        return self.producto.precio * self.cantidad

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"


class Pago(models.Model):
    class Metodo(models.TextChoices):
        EFECTIVO = "efectivo", "Efectivo"
        TARJETA = "tarjeta", "Tarjeta"
        TRANSFERENCIA = "transferencia", "Transferencia"
        OTRO = "otro", "Otro"

    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name="pago")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=20, choices=Metodo.choices, default=Metodo.EFECTIVO)
    cajero = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago pedido #{self.pedido_id} - ${self.monto}"
