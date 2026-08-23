# apps/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        MESERO = 'mesero', 'Mesero'
        COCINA = 'cocina', 'Cocina'
        CAJA = 'caja', 'Caja'
        ENTREGA = 'entrega', 'Entregas'
        LIMPIEZA = 'limpieza', 'Limpieza'
    
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.MESERO)
    activo_turno = models.BooleanField(default=True)  # ✅ Agregar este campo
    
    @property
    def es_admin(self):
        return self.rol == self.Rol.ADMIN or self.is_superuser
    
    @property
    def es_mesero(self):
        return self.rol == self.Rol.MESERO
    
    @property
    def es_cocina(self):
        return self.rol == self.Rol.COCINA
    
    @property
    def es_caja(self):
        return self.rol == self.Rol.CAJA
    
    @property
    def es_entrega(self):
        return self.rol == self.Rol.ENTREGA
    
    @property
    def es_limpieza(self):
        return self.rol == self.Rol.LIMPIEZA
    
    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"