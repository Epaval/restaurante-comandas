# apps/menu/admin.py

from django.contrib import admin
from .models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'orden']
    ordering = ['orden', 'nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio', 'tiempo_preparacion', 'disponible', 'imagen_preview']
    list_filter = ['categoria', 'disponible', 'categoria__nombre']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['disponible']
    
    fieldsets = (
        ('Información básica', {
            'fields': ('categoria', 'nombre', 'descripcion', 'componentes')
        }),
        ('Precio y tiempo', {
            'fields': ('precio', 'tiempo_preparacion')
        }),
        ('Imagen', {
            'fields': ('imagen',),
            'description': 'Sube una imagen del producto (opcional)'
        }),
        ('Disponibilidad', {
            'fields': ('disponible',)
        }),
    )
    
    def imagen_preview(self, obj):
        if obj.imagen:
            from django.utils.html import format_html
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.imagen.url
            )
        return 'Sin imagen'
    imagen_preview.short_description = 'Vista previa'