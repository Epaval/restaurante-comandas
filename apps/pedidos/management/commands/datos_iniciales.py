from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.mesas.models import Mesa
from apps.menu.models import Categoria, Producto

Usuario = get_user_model()


class Command(BaseCommand):
    help = "Crea usuarios de ejemplo, mesas y un menú básico para empezar a usar el sistema."

    def handle(self, *args, **options):
        usuarios_demo = [
            ("admin", "admin123", Usuario.Rol.ADMIN, True),
            ("mesero1", "mesero123", Usuario.Rol.MESERO, False),
            ("cocina1", "cocina123", Usuario.Rol.COCINA, False),
            ("caja1", "caja123", Usuario.Rol.CAJA, False),
            ("entrega1", "entrega123", Usuario.Rol.ENTREGA, False),
        ]
        for username, password, rol, superuser in usuarios_demo:
            if not Usuario.objects.filter(username=username).exists():
                usuario = Usuario.objects.create_user(username=username, password=password, rol=rol)
                if superuser:
                    usuario.is_staff = True
                    usuario.is_superuser = True
                    usuario.save()
                self.stdout.write(self.style.SUCCESS(f"Usuario creado: {username} / {password} ({rol})"))

        if not Mesa.objects.exists():
            for numero in range(1, 11):
                Mesa.objects.create(numero=numero, capacidad=4 if numero % 3 else 6)
            self.stdout.write(self.style.SUCCESS("10 mesas creadas."))

        if not Categoria.objects.exists():
            entradas = Categoria.objects.create(nombre="Entradas", orden=1)
            platos = Categoria.objects.create(nombre="Platos fuertes", orden=2)
            bebidas = Categoria.objects.create(nombre="Bebidas", orden=3)
            postres = Categoria.objects.create(nombre="Postres", orden=4)

            Producto.objects.bulk_create([
                Producto(categoria=entradas, nombre="Sopa del día", precio=45, tiempo_preparacion=8),
                Producto(categoria=entradas, nombre="Ensalada César", precio=60, tiempo_preparacion=7),
                Producto(categoria=platos, nombre="Milanesa con papas", precio=140, tiempo_preparacion=20),
                Producto(categoria=platos, nombre="Pasta alfredo", precio=120, tiempo_preparacion=15),
                Producto(categoria=platos, nombre="Pechuga a la plancha", precio=130, tiempo_preparacion=18),
                Producto(categoria=bebidas, nombre="Agua fresca", precio=25, tiempo_preparacion=2),
                Producto(categoria=bebidas, nombre="Refresco", precio=30, tiempo_preparacion=1),
                Producto(categoria=postres, nombre="Flan", precio=45, tiempo_preparacion=3),
            ])
            self.stdout.write(self.style.SUCCESS("Menú de ejemplo creado."))

        self.stdout.write(self.style.SUCCESS("Datos iniciales listos."))
