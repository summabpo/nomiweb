from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit,HTML

class FormularioCertificaciones(forms.Form):
    destino = forms.CharField(
        label='Destino',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'A quien va dirigida la certificación'})
        )
    opciones = (
        ('', 'Escoja el tipo de Salario'),
        ('1', 'Con salario básico'),
        ('2', 'Con salario promedio'),
        ('3', 'Sin salario'),
        ('4', 'Contrato Liquidado'),
    )
    modelo = forms.ChoiceField(choices=opciones, widget=forms.Select)

    def __init__(self, *args, **kwargs):
        super(FormularioCertificaciones, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post' 
        self.helper.layout = Layout(
            Div(
                'destino',
                'modelo',
                Submit('submit', 'Enviar', css_class='btn btn-primary hover-elevate-up')
            )
        )