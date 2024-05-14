from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


class  CompaniesForm(forms.Form):
    name = forms.CharField(label='Nombre')
    description = forms.CharField(label='Descripción',required=False)
    db_name = forms.CharField(label='Nombre de la base de datos')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('db_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('description', css_class='form-group col-md-12 mb-0'), 
                css_class='form-row' 
            ),
            
            
            Submit('submit', 'Guardar')
        )
