from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.common.models import Contabgrupos
from django.urls import reverse


class CostcenterForm(forms.Form):
    nomcosto = forms.CharField(label='Nombre de Costo' , required=True ,widget=forms.TextInput(attrs={'placeholder': 'nombre de costo'}))
    suficosto = forms.CharField(label='Sufijo costo' , required=False ,widget=forms.TextInput(attrs={'placeholder': 'Sufijo costo'}))
    
    def __init__(self, *args, **kwargs):
        idempresa = kwargs.pop('idempresa', None)
        super().__init__(*args, **kwargs)
        
        self.fields['grupocontable'] = forms.ChoiceField(choices=[('', '----------')] + [(nomina.idgrupo, nomina.grupocontable) for nomina in Contabgrupos.objects.filter(id_empresa = idempresa)], label='Grupo Contable' , required=True)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_costcenter'
        self.helper.enctype = 'multipart/form-data'
        
        
        self.helper.attrs.update({
            'hx-post': reverse('companies:costcenter_modal'),  # Usa el nombre de la vista en urls.py
            'hx-target': '#modal-container',  # El elemento donde se actualizará el contenido
            'hx-swap': 'innerHTML',  # Cómo se actualizará el contenido del objetivo
        })
        
        self.fields['grupocontable'].widget.attrs.update({
            'data-control': 'select2',
            'data-tags':'true',
            'class': 'form-select',
            'data-dropdown-parent': '#conceptsModal',
            'data-hide-search' : "true" , 
            
        })
        
        self.helper.layout = Layout(
            Row(
                Column('nomcosto', css_class='form-group col-md-12 mb-3'),
                css_class='row'
            ),
            Row(
                Column('suficosto', css_class='form-group col-md-4 mb-3'),
                Column('grupocontable', css_class='form-group col-md-8 mb-3'),
                css_class='row'
            ),
        )

    def clean_suficosto(self):
        suficosto = self.cleaned_data.get('suficosto')
        if len(suficosto) > 2:
            raise forms.ValidationError('El sufijo de costo no puede tener más de 2 caracteres.')
        return suficosto
