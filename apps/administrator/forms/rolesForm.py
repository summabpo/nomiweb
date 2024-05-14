from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


class  RolesForm(forms.Form):
    tipo = forms.CharField(label='Tipo de Rol')
    nombre = forms.CharField(label='Nombre Rol')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('tipo', css_class='form-group col-md-6 mb-0'),
                Column('nombre', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),           
            
            Submit('submit', 'Guardar')
        )
