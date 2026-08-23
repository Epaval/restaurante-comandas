# apps/accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # ✅ Eliminar 'activo_turno' de list_display
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_active')
    
    # ✅ Eliminar 'activo_turno' de list_filter
    list_filter = ('rol', 'is_active', 'is_staff', 'is_superuser')
    
    # Resto de la configuración
    fieldsets = UserAdmin.fieldsets + (
        ('Información del Restaurante', {
            'fields': ('rol',)
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información del Restaurante', {
            'fields': ('rol',)
        }),
    )