from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class RolesForm(forms.Form):
    nombre = forms.CharField(label='Nombre', max_length=100)
    descripcion = forms.CharField(
        label='Descripción',
        widget=forms.Textarea(attrs={
            'rows': 4,
            'data-kt-autosize':"true",
            'placeholder': 'Escribe la descripción aquí...',
            'style': 'width: 450px; height: 150px;'  # Tamaño fijo para el Textarea
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('nombre', css_class='form-group col-md-8 mb-0'),
                css_class='form-row'
            ),           
            Row(
                Column('descripcion', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Crear')
        )
