from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.common.models  import Entidadessegsocial
from django.urls import reverse



class headquartersForm(forms.Form):
    nombresede = forms.CharField(label='Nombre de la Sede' , required=True ,widget=forms.TextInput(attrs={'placeholder': 'Nombre de la Sede'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['cajacompensacion'] = forms.ChoiceField(choices=[('', '----------')] + [(entidad.codigo, entidad.entidad) for entidad in Entidadessegsocial.objects.filter(tipoentidad='CCF').order_by('entidad')], label='Caja de Compensación Familiar' , required=True , widget=forms.Select(attrs={'data-control': 'select2'}) )
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_headquarters'
        self.helper.enctype = 'multipart/form-data'
        
        
        # Configurar la apariencia del campo nivelcargo
        self.fields['cajacompensacion'].widget.attrs.update({
            'data-control': 'select2',
            'data-tags': 'true',
            'class': 'form-select',
            'data-dropdown-parent': '#conceptsModal',
        })
        
        self.helper.attrs.update({
            'hx-post': reverse('companies:headquarters_modal'),  # Usa el nombre de la vista en urls.py
            'hx-target': '#modal-container',  # El elemento donde se actualizará el contenido
            'hx-swap': 'innerHTML',  # Cómo se actualizará el contenido del objetivo
        })
        
        self.helper.layout = Layout(
            Row(
                Column('nombresede', css_class='form-group mb-0'),
                Column('cajacompensacion', css_class='form-group mb-0'),
                css_class='row'
            ),
        )
    