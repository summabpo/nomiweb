from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.companies.models import Contabgrupos


# class Centrotrabajo(models.Model):
#     nombrecentrotrabajo = models.CharField(max_length=30, blank=True, null=True)
#     tarifaarl = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
# 

class workplaceForm(forms.Form):
    
    TARIFA_CHOICES = [
        ('', 'Escoger -----&gt;'),
        ('0.522', 'Riesgo I - 0.522'),
        ('1.044', 'Riesgo II - 1.044'),
        ('2.436', 'Riesgo III - 2.436'),
        ('4.350', 'Riesgo IV - 4.350'),
        ('6.960', 'Riesgo V - 6.960'),
    ]
    
    nombrecentrotrabajo = forms.CharField(label='Nombre de Costo' , required=True ,widget=forms.TextInput(attrs={'placeholder': 'nombre de centro trabajo'}))
    tarifaarl = forms.ChoiceField(choices=TARIFA_CHOICES , label='Tarifa ARL' , required=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('nombrecentrotrabajo', css_class='form-group mb-0'),
                Column('tarifaarl', css_class='form-group mb-0'),
                css_class='row'
            ),
            Submit('submit', 'Guardar')
        )
    