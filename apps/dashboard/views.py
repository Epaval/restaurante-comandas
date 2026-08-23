# apps/dashboard/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Sum, Count

from apps.accounts.decorators import rol_requerido
from apps.mesas.models import Mesa
from apps.pedidos.models import Pedido, Pago


@login_required
def inicio(request):
    usuario = request.user
    if usuario.is_superuser or usuario.es_admin:
        return redirect("dashboard:admin")
    if usuario.es_mesero:
        return redirect("dashboard:mesero")
    if usuario.es_cocina:
        return redirect("dashboard:cocina")
    if usuario.es_caja:
        return redirect("dashboard:caja")
    if usuario.es_entrega:
        return redirect("dashboard:entregas")
    # ✅ Agregar redirección para limpieza
    if usuario.es_limpieza:
        return redirect("mesas:panel_limpieza")
    return redirect("accounts:login")  # ✅ Usar nombre completo


@rol_requerido("mesero")
def panel_mesero(request):
    pedidos_activos = (
        Pedido.objects.filter(mesero=request.user)
        .exclude(estado__in=[Pedido.Estado.PAGADO, Pedido.Estado.CANCELADO, Pedido.Estado.ENTREGADO])
        .prefetch_related("items")
    )
    return render(request, "dashboard/mesero.html", {"pedidos": pedidos_activos})


@rol_requerido("admin")
def panel_admin(request):
    hoy = timezone.localdate()
    pedidos_hoy = Pedido.objects.filter(creado__date=hoy)
    ventas_hoy = Pago.objects.filter(fecha__date=hoy).aggregate(total=Sum("monto"))["total"] or 0

    contexto = {
        "pedidos_hoy": pedidos_hoy.count(),
        "ventas_hoy": ventas_hoy,
        "pedidos_activos": pedidos_hoy.exclude(
            estado__in=[Pedido.Estado.PAGADO, Pedido.Estado.CANCELADO]
        ).count(),
        "mesas_disponibles": Mesa.objects.filter(estado=Mesa.Estado.DISPONIBLE).count(),
        "mesas_total": Mesa.objects.count(),
        "por_estado": pedidos_hoy.values("estado").annotate(total=Count("id")),
        "ultimos_pedidos": Pedido.objects.select_related("mesa", "mesero")[:10],
    }
    return render(request, "dashboard/admin.html", contexto)


@rol_requerido("cocina")
def panel_cocina_dashboard(request):
    """Panel de cocina desde el dashboard"""
    from apps.pedidos.models import Pedido
    pedidos = Pedido.objects.filter(
        estado=Pedido.Estado.PREPARACION
    ).order_by('-creado')
    return render(request, 'pedidos/panel_cocina.html', {'pedidos': pedidos})


@rol_requerido("caja")
def panel_caja_dashboard(request):
    """Panel de caja desde el dashboard"""
    from apps.pedidos.models import Pedido
    pedidos = Pedido.objects.filter(
        estado=Pedido.Estado.CUENTA_SOLICITADA
    ).order_by('-creado')
    return render(request, 'pedidos/panel_caja.html', {'pedidos': pedidos})


@rol_requerido("entrega")
def panel_entregas_dashboard(request):
    """Panel de entregas desde el dashboard"""
    from apps.pedidos.models import Pedido
    pedidos = Pedido.objects.filter(
        estado=Pedido.Estado.LISTO
    ).order_by('-creado')
    return render(request, 'pedidos/panel_entregas.html', {'pedidos': pedidos})