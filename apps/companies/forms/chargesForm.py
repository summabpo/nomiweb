from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.common.models import Nivelesestructura
from django.urls import reverse

class ChargesForm(forms.Form):
    nombrecargo = forms.CharField(label='Nombre Cargo' , widget=forms.TextInput(attrs={'placeholder': 'Nombre cargo'}))
    
    def __init__(self, *args, **kwargs):
        idempresa = kwargs.pop('idempresa', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar Nivelesestructura por idempresa si está disponible
        niveles = Nivelesestructura.objects.all().exclude(idnivel=10).order_by('idnivel')
        
        # Crear el campo nivelcargo con las opciones filtradas
        self.fields['nivelcargo'] = forms.ChoiceField(
            choices=[('', '----------')] + [(n.idnivel, n.nombrenivel) for n in niveles],
            label='Nivel de Cargo',
            required=True
        )
        
        # Configurar la apariencia del campo nivelcargo
        self.fields['nivelcargo'].widget.attrs.update({
            'data-control': 'select2',
            'data-tags': 'true',
            'class': 'form-select',
            'data-dropdown-parent': '#conceptsModal',
            'data-hide-search': "true",
        })
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_charge'
        self.helper.enctype = 'multipart/form-data'
        
        
        self.helper.attrs.update({
            'hx-post': reverse('companies:charges_modal'),  # Usa el nombre de la vista en urls.py
            'hx-target': '#modal-container',  # El elemento donde se actualizará el contenido
            'hx-swap': 'innerHTML',  # Cómo se actualizará el contenido del objetivo
        })
        
        
        
        self.helper.layout = Layout(
            Row(
                Column('nombrecargo', css_class='form-group mb-0'),
                Column('nivelcargo', css_class='form-group mb-0'),
                css_class='row'
            ),
        )
    