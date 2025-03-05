from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.common.models   import Contabgrupos
from django.urls import reverse

# class Centrotrabajo(models.Model):
#     nombrecentrotrabajo = models.CharField(max_length=30, blank=True, null=True)
#     tarifaarl = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
# 

class workplaceForm(forms.Form):
    
    TARIFA_CHOICES = [
        ('', '---------'),
        ('0.522', 'Riesgo  mínimo (Clase I) - 0.522'),
        ('1.044', 'Riesgo  bajo (Clase II) - 1.044'),
        ('2.436', 'Riesgo medio (Clase III) - 2.436'),
        ('4.350', 'Riesgo alto (Clase IV) - 4.350'),
        ('6.960', 'Riesgo máximo (Clase V) - 6.960'),
    ]
    
    nombrecentrotrabajo = forms.CharField(label='Nombre de Costo' , required=True ,widget=forms.TextInput(attrs={'placeholder': 'nombre de centro trabajo'}))
    tarifaarl = forms.ChoiceField(choices=TARIFA_CHOICES , label='Tarifa ARL' , required=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_charge'
        self.helper.enctype = 'multipart/form-data'
        
        
        self.helper.attrs.update({
            'hx-post': reverse('companies:workplace_modal'),  # Usa el nombre de la vista en urls.py
            'hx-target': '#modal-container',  # El elemento donde se actualizará el contenido
            'hx-swap': 'innerHTML',  # Cómo se actualizará el contenido del objetivo
        })
        
        self.fields['tarifaarl'].widget.attrs.update({
            'data-control': 'select2',
            'data-tags': 'true',
            'class': 'form-select',
            'data-dropdown-parent': '#conceptsModal',
            'data-hide-search': "true",
        })
        
        
        self.helper.layout = Layout(
            Row(
                Column('nombrecentrotrabajo', css_class='form-group mb-0'),
                Column('tarifaarl', css_class='form-group mb-0'),
                css_class='row'
            ),
        )
    