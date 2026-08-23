from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="productos")
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tiempo_preparacion = models.PositiveIntegerField(
        help_text="Tiempo estimado de preparación en minutos", default=10
    )
    disponible = models.BooleanField(default=True)
    
    # NUEVO: Campo para la imagen del producto
    imagen = models.ImageField(
        upload_to='productos/',
        blank=True,
        null=True,
        verbose_name='Imagen del producto',
        help_text='Imagen opcional del producto (formatos: JPG, PNG, WEBP)'
    )
    
    # NUEVO: Campo para ingredientes/componentes
    componentes = models.TextField(
        blank=True,
        default='',
        verbose_name='Componentes/Ingredientes',
        help_text='Ingredientes o componentes del producto'
    )

    class Meta:
        ordering = ["categoria__orden", "nombre"]

    def __str__(self):
        return f"{self.nombre} (${self.precio})"