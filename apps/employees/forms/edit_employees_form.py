from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row,Button,Column,HTML ,Field
from apps.common.models import Ciudades

class EditEmployeesForm(forms.Form):
    
    phone = forms.CharField(max_length=12, label='Telefono',required=False)
    address = forms.CharField(max_length=100, label='Direccion',required=False)
    profile_picture = forms.ImageField(label='Imagen de perfil', required=False)
    cell = forms.CharField(max_length=12, label='Celular',required=False)
    
    
    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        super(EditEmployeesForm, self).__init__(*args, **kwargs)
        self.fields['phone'].initial = initial.get('phone', '')
        self.fields['address'].initial = initial.get('address', '')
        
        self.fields['city'] = forms.ChoiceField(
            choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.all().order_by('ciudad')],
            label='Ciudad de recidencia',
            widget=forms.Select(attrs={'data-control': 'select2'})
        )
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_editemployees'
        self.helper.layout = Layout(
            
            Row(
                Column('phone', css_class='form-group col-md-6 mb-0'),
                Column('cell', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('city', css_class='form-group col-md-6 mb-0'),
                Column('address', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('profile_picture', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            
            
        )




