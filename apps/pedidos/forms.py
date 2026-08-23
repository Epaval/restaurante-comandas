# apps/pedidos/forms.py
from django import forms
from .models import Pedido, ItemPedido, Pago


class DatosClienteForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente_nombre', 'cliente_telefono']
        widgets = {
            'cliente_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del cliente',
                'required': True
            }),
            'cliente_telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono (opcional)'
            }),
        }


class ItemPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ['producto', 'cantidad', 'notas']


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['monto', 'metodo']