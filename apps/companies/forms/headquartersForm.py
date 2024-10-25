from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.common.models  import Entidadessegsocial




class headquartersForm(forms.Form):
    nombresede = forms.CharField(label='Nombre de la Sede' , required=True ,widget=forms.TextInput(attrs={'placeholder': 'Nombre de la Sede'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['cajacompensacion'] = forms.ChoiceField(choices=[('', '----------')] + [(entidad.codigo, entidad.entidad) for entidad in Entidadessegsocial.objects.filter(tipoentidad='CCF').order_by('entidad')], label='Caja de Compensación Familiar' , required=True , widget=forms.Select(attrs={'data-control': 'select2'}) )
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('nombresede', css_class='form-group mb-0'),
                Column('cajacompensacion', css_class='form-group mb-0'),
                css_class='row'
            ),
            Submit('submit', 'Guardar')
        )
    