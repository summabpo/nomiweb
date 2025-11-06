from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column,Button , HTML
from apps.common.models import Costos,Sedes,Contratosemp,Anos

# Definir los choices para los años (2015-2024)
AÑO_CHOICES = [('', '--------------')] + [(str(year), str(year)) for year in range(2024, 2014, -1)]


# Definir los choices para los meses
MES_CHOICES = [
    ('', '--------------'),
    ('ENERO', 'Enero'),
    ('FEBRERO', 'Febrero'),
    ('MARZO', 'Marzo'),
    ('ABRIL', 'Abril'),
    ('MAYO', 'Mayo'),
    ('JUNIO', 'Junio'),
    ('JULIO', 'Julio'),
    ('AGOSTO', 'Agosto'),
    ('SEPTIEMBRE', 'Septiembre'),
    ('OCTUBRE', 'Octubre'),
    ('NOVIEMBRE', 'Noviembre'),
    ('DICIEMBRE', 'Diciembre')
]


class FilterBasicForm(forms.Form):
    
    mst_init = forms.ChoiceField(
        choices=MES_CHOICES,
        required=True,
        label='Mes Inicial',
        widget=forms.Select(attrs={'class': 'form-control'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)    
    
        self.fields['year_init'] = forms.ChoiceField(
                choices=[('', '----------')] + [(n.ano, n.ano) for n in Anos.objects.all().order_by('-ano')], 
                label='Año Inicial' , 
                required=True ,
                widget=forms.Select(attrs={
                        'data-control': 'select2',
                        'data-tags': 'true',
                        'class': 'form-select',
                        'data-hide-search': 'true',
                    }),
                )
        
        self.fields['mst_init'].widget.attrs.update({
            'data-control': 'select2',
            'data-hide-search': 'true' ,
            'class': 'form-select',
            
        })
    
        self.helper = FormHelper()
        self.helper.form_id = 'Filter_basic'
        self.helper.layout = Layout(
            Row(
                HTML('<div class="text-gray-900">Los campos marcados con un <span class="text-danger">*</span> son obligatorios.</div><br>'),
                css_class='row'
            ),
            Row(
                Column('mst_init', css_class='form-group mb-0'),
                Column('year_init', css_class='form-group mb-0'),
                css_class='row'
            ),

            Row(
                HTML('<div class="separator border-3 my-5"></div>'),
                css_class='row'
            ),
            
            Row(
                Column(
                    Button('button', 'Limpiar filtrado', css_class='btn btn-light-primary w-100', id='my-custom-button'), # 100% ancho de la columna
                    css_class='col-md-6'  # Ancho especificado
                ),
                Column(
                    Submit('submit', 'Filtrar', css_class='btn btn-light-info w-100'),  # 100% ancho de la columna
                    css_class='col-md-6'  # Ancho especificado
                ),
                
                css_class='row'
            ),
            
        )
