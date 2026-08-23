# apps/pedidos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import F
import json

from .models import Pedido, ItemPedido, Producto
from .forms import ItemPedidoForm, PagoForm, DatosClienteForm
from apps.menu.models import Categoria
from apps.mesas.models import Mesa

# apps/pedidos/views.py
@login_required
@require_http_methods(["POST"])
def cambiar_estado_item(request, item_id):
    """Cambia el estado de un item del pedido (para cocina)"""
    item = get_object_or_404(ItemPedido, id=item_id)
    pedido = item.pedido
    
    # Verificar permisos (solo cocina o admin)
    if not (request.user.es_cocina or request.user.es_admin or request.user.is_superuser):
        messages.error(request, 'No tienes permiso para realizar esta acción')
        return redirect('dashboard:cocina')  # ✅ Cambiar a dashboard:cocina
    
    nuevo_estado = request.POST.get('estado')
    
    # Validar que el estado sea válido
    estados_validos = ['en_preparacion', 'listo']
    if nuevo_estado not in estados_validos:
        messages.error(request, 'Estado inválido')
        return redirect('dashboard:cocina')  # ✅ Cambiar a dashboard:cocina
    
    # Cambiar estado del item
    item.estado = nuevo_estado
    item.save()
    
    # Si el item está listo, verificar si todos los items están listos
    if nuevo_estado == 'listo':
        # Verificar si todos los items del pedido están listos
        todos_listos = all(
            i.estado == ItemPedido.Estado.LISTO 
            for i in pedido.items.all()
        )
        
        if todos_listos:
            # Cambiar estado del pedido a LISTO
            pedido.marcar_listo()
            messages.success(request, f'✅ Pedido #{pedido.id} completado - Todos los items están listos')
        else:
            messages.success(request, f'✅ Item "{item.producto.nombre}" marcado como listo')
    else:
        messages.success(request, f'🔄 Item "{item.producto.nombre}" en preparación')
    
    return redirect('dashboard:cocina')  # ✅ Cambiar a dashboard:cocina



# apps/pedidos/views.py
@login_required
def detalle_pedido(request, pedido_id):
    """Vista del detalle del pedido con flujo completo"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # ✅ Verificar permisos según el rol
    es_mesero_o_admin = request.user.es_mesero or request.user.es_admin or request.user.is_superuser
    es_propietario = pedido.mesero == request.user
    
    if not (es_mesero_o_admin or es_propietario):
        messages.error(request, 'No tienes permiso para ver este pedido')
        return redirect('dashboard:inicio')
    
    # ✅ Determinar si mostrar el menú (solo meseros, admin o propietario)
    mostrar_menu = False
    if (request.user.es_mesero or request.user.es_admin or request.user.is_superuser or es_propietario):
        mostrar_menu = pedido.estado in [Pedido.Estado.BORRADOR, Pedido.Estado.PREPARACION]
    
    # ✅ Verificar si puede editar (agregar/eliminar items)
    puede_editar = False
    if (request.user.es_mesero or request.user.es_admin or request.user.is_superuser or es_propietario):
        puede_editar = pedido.estado in [Pedido.Estado.BORRADOR, Pedido.Estado.PREPARACION]
    
    categorias = Categoria.objects.prefetch_related('productos').all()
    item_form = ItemPedidoForm()
    pago_form = PagoForm()
    datos_cliente_form = DatosClienteForm(instance=pedido)
    
    contexto = {
        'pedido': pedido,
        'categorias': categorias,
        'item_form': item_form,
        'pago_form': pago_form,
        'datos_cliente_form': datos_cliente_form,
        'mostrar_menu': mostrar_menu,
        'puede_editar': puede_editar,
        'es_limpieza': request.user.es_limpieza,
    }
    return render(request, 'pedidos/detalle_pedido.html', contexto)


@login_required
def enviar_a_cocina(request, pedido_id):
    """Envía el pedido a cocina solicitando datos del cliente"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if pedido.estado != Pedido.Estado.BORRADOR:
        messages.error(request, 'Este pedido ya fue enviado a cocina')
        return redirect('pedidos:detalle', pedido_id=pedido.id)
    
    if not pedido.items.exists():
        messages.error(request, 'Agregue al menos un producto antes de enviar a cocina')
        return redirect('pedidos:detalle', pedido_id=pedido.id)
    
    if request.method == 'POST':
        form = DatosClienteForm(request.POST, instance=pedido)
        if form.is_valid():
            cliente_nombre = form.cleaned_data['cliente_nombre']
            cliente_telefono = form.cleaned_data.get('cliente_telefono', '')
            
            # ✅ CORREGIDO: Usar el método del modelo
            pedido.enviar_a_cocina(cliente_nombre, cliente_telefono)
            messages.success(request, f'✅ Pedido #{pedido.id} enviado a cocina')
            return redirect('pedidos:detalle', pedido_id=pedido.id)
    else:
        form = DatosClienteForm(instance=pedido)
    
    return render(request, 'pedidos/enviar_a_cocina.html', {
        'pedido': pedido,
        'form': form
    })


@login_required
def solicitar_cuenta(request, pedido_id):
    """Cliente solicita la cuenta"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # ✅ CORREGIDO: Verificar LISTO
    if pedido.estado != Pedido.Estado.LISTO:
        messages.error(request, 'El pedido debe estar listo para solicitar la cuenta')
        return redirect('pedidos:detalle', pedido_id=pedido.id)
    
    pedido.solicitar_cuenta()
    messages.success(request, f'💰 Cuenta solicitada para pedido #{pedido.id}')
    return redirect('pedidos:detalle', pedido_id=pedido.id)


@login_required
def procesar_pago(request, pedido_id):
    """Procesa el pago y solicita limpieza"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # ✅ CORREGIDO: Verificar CUENTA_SOLICITADA
    if pedido.estado != Pedido.Estado.CUENTA_SOLICITADA:
        messages.error(request, 'El pedido debe tener la cuenta solicitada')
        return redirect('pedidos:detalle', pedido_id=pedido.id)
    
    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.pedido = pedido
            pago.monto = pedido.total
            pago.save()
            
            pedido.marcar_pagado()
            messages.success(request, f'✅ Pago registrado. Mesa {pedido.mesa.numero} en limpieza')
            return redirect('pedidos:detalle', pedido_id=pedido.id)
    else:
        form = PagoForm()
    
    return render(request, 'pedidos/procesar_pago.html', {
        'pedido': pedido,
        'form': form
    })


@login_required
def completar_limpieza(request, mesa_id):
    """Marca la mesa como disponible después de la limpieza"""
    mesa = get_object_or_404(Mesa, id=mesa_id)
    
    if mesa.estado != Mesa.Estado.LIMPIEZA:
        messages.error(request, 'Esta mesa no está en proceso de limpieza')
        return redirect('dashboard:inicio')
    
    mesa.completar_limpieza()
    messages.success(request, f'✅ Mesa {mesa.numero} disponible')
    return redirect('dashboard:inicio')


# apps/pedidos/views.py
@login_required
@require_http_methods(["POST"])
def agregar_item_ajax(request, pedido_id):
    """Agregar item al pedido vía AJAX"""
    pedido = get_object_or_404(Pedido, id=pedido_id)

    es_mesero_o_admin = request.user.es_mesero or request.user.es_admin or request.user.is_superuser
    es_propietario = pedido.mesero == request.user
    
    if not (es_mesero_o_admin or es_propietario):
        return JsonResponse({
            'error': 'No tienes permiso para modificar este pedido',
            'success': False
        }, status=403)
    
    # ✅ Cambiar: Permitir agregar items si el pedido está en BORRADOR o PREPARACION
    if pedido.estado not in [Pedido.Estado.BORRADOR, Pedido.Estado.PREPARACION]:
        return JsonResponse({
            'error': 'No se pueden agregar items a un pedido que ya está listo o pagado',
            'success': False
        }, status=400)
    
    try:
        data = json.loads(request.body)
        producto_id = data.get('producto_id')
        cantidad = int(data.get('cantidad', 1))
        notas = data.get('notas', '')
        
        producto = get_object_or_404(Producto, id=producto_id)
        
        item, created = ItemPedido.objects.get_or_create(
            pedido=pedido,
            producto=producto,
            notas=notas,
            defaults={'cantidad': cantidad}
        )
        
        if not created:
            item.cantidad = F('cantidad') + cantidad
            item.save()
            item.refresh_from_db()
        
        # ✅ Si el pedido estaba en PREPARACION, mantenerlo en PREPARACION
        # No cambiar el estado automáticamente
        
        return JsonResponse({
            'success': True,
            'item_id': item.id,
            'cantidad': item.cantidad,
            'subtotal': float(item.subtotal),
            'pedido_total': float(pedido.total),
            'mensaje': f'{producto.nombre} agregado al pedido',
            'estado_pedido': pedido.estado
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e), 'success': False}, status=400)


@login_required
@require_http_methods(["POST"])
def eliminar_item_ajax(request, item_id):
    """Eliminar o reducir cantidad de un item"""
    item = get_object_or_404(ItemPedido, id=item_id)
    pedido = item.pedido

    es_mesero_o_admin = request.user.es_mesero or request.user.es_admin or request.user.is_superuser
    es_propietario = pedido.mesero == request.user
    
    if not (es_mesero_o_admin or es_propietario):
        return JsonResponse({
            'error': 'No tienes permiso para modificar este pedido',
            'success': False
        }, status=403)
    
    if pedido.estado != Pedido.Estado.BORRADOR:
        return JsonResponse({
            'error': 'No se puede modificar el pedido',
            'success': False
        }, status=400)
    
    try:
        data = json.loads(request.body)
        accion = data.get('accion', 'eliminar')
        
        if accion == 'restar' and item.cantidad > 1:
            item.cantidad = F('cantidad') - 1
            item.save()
            item.refresh_from_db()
            
            return JsonResponse({
                'success': True,
                'item_id': item.id,
                'cantidad': item.cantidad,
                'subtotal': float(item.subtotal),
                'pedido_total': float(pedido.total),
                'mensaje': 'Cantidad reducida'
            })
        else:
            producto_nombre = item.producto.nombre
            item.delete()
            
            return JsonResponse({
                'success': True,
                'item_id': item_id,
                'pedido_total': float(pedido.total),
                'mensaje': f'{producto_nombre} eliminado',
                'eliminado': True
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e), 'success': False}, status=400)


# ✅ PANELES CORREGIDOS
@login_required
def panel_cocina(request):
    """Vista para el panel de cocina"""
    # ✅ CORREGIDO: Usar PREPARACION (no ENVIADO ni EN_PREPARACION)
    pedidos = Pedido.objects.filter(
        estado__in=[Pedido.Estado.PREPARACION]
    ).order_by('-creado')  # ✅ Usar 'creado' no 'created_at'
    return render(request, 'pedidos/panel_cocina.html', {'pedidos': pedidos})

@login_required
def panel_caja(request):
    """Vista para el panel de caja"""
    # ✅ CORREGIDO: Usar CUENTA_SOLICITADA
    pedidos = Pedido.objects.filter(
        estado=Pedido.Estado.CUENTA_SOLICITADA
    ).order_by('-creado')
    return render(request, 'pedidos/panel_caja.html', {'pedidos': pedidos})

@login_required
def panel_entregas(request):
    """Vista para el panel de entregas"""
    # ✅ CORREGIDO: Usar LISTO
    pedidos = Pedido.objects.filter(
        estado=Pedido.Estado.LISTO
    ).order_by('-creado')
    return render(request, 'pedidos/panel_entregas.html', {'pedidos': pedidos})   

@login_required
def crear_pedido_rapido(request):
    """Crea un nuevo pedido rápido para una mesa"""
    if request.method == 'POST':
        mesa_id = request.POST.get('mesa_id')
        if not mesa_id:
            messages.error(request, 'Debe seleccionar una mesa')
            return redirect('pedidos:nuevo')
        
        mesa = get_object_or_404(Mesa, id=mesa_id)
        
        # Verificar que la mesa esté disponible
        if mesa.estado != Mesa.Estado.DISPONIBLE:
            messages.error(request, f'La mesa {mesa.numero} no está disponible')
            return redirect('pedidos:nuevo')
        
        # Crear el pedido
        pedido = Pedido.objects.create(
            mesa=mesa,
            mesero=request.user,
            estado=Pedido.Estado.BORRADOR
        )
        
        # Cambiar estado de la mesa a OCUPADA
        mesa.estado = Mesa.Estado.OCUPADA
        mesa.save()
        
        messages.success(request, f'✅ Pedido #{pedido.id} creado para mesa {mesa.numero}')
        return redirect('pedidos:detalle', pedido_id=pedido.id)
    
    # GET - Mostrar formulario
    mesas_disponibles = Mesa.objects.filter(estado=Mesa.Estado.DISPONIBLE)
    return render(request, 'pedidos/crear_pedido_rapido.html', {
        'mesas': mesas_disponibles
    })


# apps/pedidos/views.py
@login_required
@require_http_methods(["POST"])
def cancelar_pedido(request, pedido_id):
    print("=" * 50)
    print("🚨 CANCELAR PEDIDO LLAMADO")
    print(f"  ID: {pedido_id}")
    print(f"  Usuario: {request.user}")
    print(f"  Método: {request.method}")
    print("=" * 50)
    
    """Cancela un pedido en estado BORRADOR y libera la mesa"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Verificar permisos
    if not (request.user.es_mesero or request.user.es_admin or 
            request.user.is_superuser or pedido.mesero == request.user):
        return JsonResponse({
            'error': 'No tienes permiso para cancelar este pedido',
            'success': False
        }, status=403)
    
    # Solo se pueden cancelar pedidos en estado BORRADOR
    if pedido.estado != Pedido.Estado.BORRADOR:
        return JsonResponse({
            'error': 'Solo se pueden cancelar pedidos en estado BORRADOR',
            'success': False
        }, status=400)
    
    # Cancelar pedido
    pedido.estado = Pedido.Estado.CANCELADO
    pedido.save()
    
    # Liberar la mesa
    if pedido.mesa:
        pedido.mesa.estado = Mesa.Estado.DISPONIBLE
        pedido.mesa.save()
    
    # ✅ Retornar JsonResponse
    return JsonResponse({
        'success': True,
        'mensaje': f'Pedido #{pedido.id} cancelado correctamente',
        'redirect_url': '/mesas/'
    })