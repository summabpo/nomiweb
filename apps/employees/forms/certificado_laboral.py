from django import forms

class FormularioCertificaciones(forms.Form):
    destino = forms.CharField(
        label='Destino',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'A quien va dirigida la certificación'})
        )
    opciones = (
        ('', 'Escoja el tipo de certificación'),
        ('1', 'Con salario básico'),
        ('2', 'Con salario promedio'),
        ('3', 'Sin salario'),
    )
    seleccion = forms.ChoiceField(choices=opciones, widget=forms.Select)