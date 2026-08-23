# apps/mesas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Mesa
from apps.pedidos.models import Pedido

def lista_mesas(request):
    """Vista de todas las mesas con su estado"""
    mesas = Mesa.objects.all().order_by('numero')
    disponibles = mesas.filter(estado=Mesa.Estado.DISPONIBLE).count()
    ocupadas = mesas.filter(estado=Mesa.Estado.OCUPADA).count()
    
    for mesa in mesas:
        if mesa.estado == Mesa.Estado.DISPONIBLE:
            mesa.badge_class = 'badge-success'
        elif mesa.estado == Mesa.Estado.OCUPADA:
            mesa.badge_class = 'badge-danger'
        elif mesa.estado == Mesa.Estado.LIMPIEZA:
            mesa.badge_class = 'badge-warning'
        else:
            mesa.badge_class = 'badge-secondary'
    
    contexto = {
        'mesas': mesas,
        'disponibles': disponibles,
        'ocupadas': ocupadas,
    }
    return render(request, 'mesas/lista_mesas.html', contexto)

# apps/mesas/views.py
@login_required
def seleccionar_mesa(request, mesa_id):
    """Selecciona una mesa y crea/abre un pedido"""
    mesa = get_object_or_404(Mesa, id=mesa_id)
    
    if mesa.estado == Mesa.Estado.LIMPIEZA:
        messages.warning(request, f'La mesa {mesa.numero} está en proceso de limpieza')
        return redirect('mesas:lista')
    
    # ✅ Buscar pedido activo (borrador o en preparación)
    pedido_activo = Pedido.objects.filter(
        mesa=mesa,
        estado__in=[Pedido.Estado.BORRADOR, Pedido.Estado.PREPARACION]
    ).order_by('-creado').first()
    
    # Si hay pedido activo, ir a él
    if pedido_activo:
        messages.info(request, f'Abriendo pedido #{pedido_activo.id}')
        return redirect('pedidos:detalle', pedido_id=pedido_activo.id)
    
    # Si la mesa está disponible, crear nuevo pedido
    if mesa.estado == Mesa.Estado.DISPONIBLE:
        try:
            pedido = Pedido.objects.create(
                mesa=mesa,
                mesero=request.user,
                estado=Pedido.Estado.BORRADOR
            )
            mesa.estado = Mesa.Estado.OCUPADA
            mesa.save()
            
            messages.success(request, f'✅ Pedido #{pedido.id} creado para mesa {mesa.numero}')
            return redirect('pedidos:detalle', pedido_id=pedido.id)
        except Exception as e:
            messages.error(request, f'Error al crear pedido: {str(e)}')
            return redirect('mesas:lista')
    
    # Si la mesa está ocupada pero no tiene pedido activo
    elif mesa.estado == Mesa.Estado.OCUPADA:
        messages.warning(request, f'La mesa {mesa.numero} está ocupada pero no tiene pedido activo')
        return redirect('mesas:lista')
    
    messages.info(request, f'La mesa {mesa.numero} no está disponible actualmente')
    return redirect('mesas:lista')

# ✅ AGREGAR ESTA FUNCIÓN
@login_required
def cambiar_estado(request, mesa_id):
    """Cambia el estado de una mesa manualmente (desde el panel de administración)"""
    mesa = get_object_or_404(Mesa, id=mesa_id)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        
        # Validar que el estado sea válido
        estados_validos = [choice[0] for choice in Mesa.Estado.choices]
        if nuevo_estado in estados_validos:
            mesa.estado = nuevo_estado
            mesa.save()
            
            # Obtener el nombre legible del estado
            estado_nombre = dict(Mesa.Estado.choices).get(nuevo_estado, nuevo_estado)
            messages.success(request, f'✅ Mesa {mesa.numero} cambiada a "{estado_nombre}"')
        else:
            messages.error(request, 'Estado inválido')
    
    # Redirigir a la página de mesas o a la página anterior
    next_url = request.POST.get('next', request.GET.get('next', 'mesas:lista'))
    return redirect(next_url)

@login_required
def panel_limpieza(request):
    """Vista del panel de limpieza - solo para usuarios con rol LIMPIEZA"""
    # ✅ Verificar que el usuario tenga permiso
    if not (request.user.es_limpieza or request.user.es_admin or request.user.is_superuser):
        messages.error(request, 'No tienes permiso para acceder a este panel')
        return redirect('dashboard:inicio')
    
    mesas_limpieza = Mesa.objects.filter(estado=Mesa.Estado.LIMPIEZA).order_by('numero')
    
    # Obtener el pedido asociado a cada mesa
    for mesa in mesas_limpieza:
        pedido = Pedido.objects.filter(
            mesa=mesa,
            estado=Pedido.Estado.PAGADO
        ).order_by('-creado').first()
        mesa.pedido = pedido
    
    contexto = {
        'mesas': mesas_limpieza,
        'total_limpieza': mesas_limpieza.count(),
    }
    return render(request, 'mesas/panel_limpieza.html', contexto)

@login_required
def completar_limpieza(request, mesa_id):
    """Marca la mesa como disponible después de la limpieza - solo para LIMPIEZA"""
    # ✅ Verificar que el usuario tenga permiso
    if not (request.user.es_limpieza or request.user.es_admin or request.user.is_superuser):
        messages.error(request, 'No tienes permiso para realizar esta acción')
        return redirect('dashboard:inicio')
    
    mesa = get_object_or_404(Mesa, id=mesa_id)
    
    if mesa.estado != Mesa.Estado.LIMPIEZA:
        messages.error(request, 'Esta mesa no está en proceso de limpieza')
        return redirect('mesas:panel_limpieza')
    
    mesa.completar_limpieza()
    messages.success(request, f'✅ Mesa {mesa.numero} limpia y disponible')
    return redirect('mesas:panel_limpieza')