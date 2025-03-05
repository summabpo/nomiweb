
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.common.models import Nivelesestructura
from django.urls import reverse

class accountinggroupForm(forms.Form):
    grupo = forms.CharField(label='Nombre del Grupo',max_length=2, widget=forms.TextInput(attrs={'placeholder': 'Ingrese el nombre del grupo'}))
    grupocontable = forms.CharField(label='Grupo Contable' , widget=forms.TextInput(attrs={'placeholder': 'Grupo Contable'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_accountinggroup'
        self.helper.enctype = 'multipart/form-data'
        
        
        self.helper.attrs.update({
            'hx-post': reverse('companies:accountinggroup_modal'),  # Usa el nombre de la vista en urls.py
            'hx-target': '#modal-container',  # El elemento donde se actualizará el contenido
            'hx-swap': 'innerHTML',  # Cómo se actualizará el contenido del objetivo
        })
        
        self.helper.layout = Layout(
            Row(
                Column('grupo', css_class='form-group mb-0'),
                Column('grupocontable', css_class='form-group mb-0'),
                css_class='row'
            ),
        )
    
    def clean_grupo(self):
        grupo = self.cleaned_data.get('grupo')
        if len(grupo) > 2:
            raise forms.ValidationError('El nombre del grupo no puede tener más de 2 caracteres.')
        return grupo
    