from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.companies.models import Contabgrupos

class CostcenterForm(forms.Form):
    nomcosto = forms.CharField(label='Nombre de Costo' , required=True ,widget=forms.TextInput(attrs={'placeholder': 'nombre de costo'}))
    suficosto = forms.CharField(label='Sufijo costo' , required=False ,widget=forms.TextInput(attrs={'placeholder': 'Sufijo costo'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['grupocontable'] = forms.ChoiceField(choices=[('', '----------')] + [(nomina.idgrupo, nomina.grupocontable) for nomina in Contabgrupos.objects.all()], label='Grupo Contable' , required=True)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('nomcosto', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                Column('suficosto', css_class='form-group mb-0'),
                Column('grupocontable', css_class='form-group mb-0'),
                css_class='row'
            ),
            Submit('submit', 'Guardar')
        )
    