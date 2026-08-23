# apps/mesas/models.py
from django.db import models
from django.conf import settings


class Mesa(models.Model):
    class Estado(models.TextChoices):
        DISPONIBLE = "disponible", "Disponible"
        OCUPADA = "ocupada", "Ocupada"
        RESERVADA = "reservada", "Reservada"
        LIMPIEZA = "limpieza", "En limpieza"

    numero = models.IntegerField(unique=True)
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.DISPONIBLE
    )
    capacidad = models.PositiveIntegerField(default=4)
    
    # Nuevos campos para el flujo de limpieza
    solicitada_limpieza = models.BooleanField(default=False)
    limpieza_solicitada_en = models.DateTimeField(null=True, blank=True)
    limpieza_completada_en = models.DateTimeField(null=True, blank=True)
    ultimo_pedido = models.ForeignKey(
        'pedidos.Pedido',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mesas_usadas'
    )

    class Meta:
        ordering = ["numero"]

    def __str__(self):
        return f"Mesa {self.numero} ({self.get_estado_display()})"

    def marcar_ocupada(self):
        self.estado = self.Estado.OCUPADA
        self.solicitada_limpieza = False
        self.save()

    def solicitar_limpieza(self):
        from django.utils import timezone
        self.estado = self.Estado.LIMPIEZA
        self.solicitada_limpieza = True
        self.limpieza_solicitada_en = timezone.now()
        self.save()

    def completar_limpieza(self):
        from django.utils import timezone
        self.estado = self.Estado.DISPONIBLE
        self.solicitada_limpieza = False
        self.limpieza_completada_en = timezone.now()
        self.ultimo_pedido = None
        self.save()