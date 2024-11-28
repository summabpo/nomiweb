from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column ,Button
from apps.common.models import Contabgrupos , Nomina , Contratosemp



CONCEPT_CHOICES = [
        ('', '---------------'),
        ('1', 'Concepto 1'),
        ('2', 'Concepto 2'),
        ('3', 'Concepto 3'),
        # Agrega más opciones según sea necesario
    ]


MONTH_CHOICES = [
    ('', '---------------'),
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
    ('DICIEMBRE', 'Diciembre'),
]





YEAR_CHOICES = [
    ('', '---------------'),
    ('2023', '2023'),
    ('2024', '2024'),
    ('2025', '2025'),
    # Agrega más opciones según sea necesario
]

EMPLOYEE_CHOICES = [
    ('', '---------------'),
    ('1', 'Pilar Castañeda'),
    ('2', 'Iván Paez')
]

COST_CENTER_CHOICES = [
    ('', '---------------'),
    ('1', 'Centro de Costos 1'),
    ('2', 'Centro de Costos 2')
]


class AbstractConceptForm(forms.Form):
    

    
    sconcept = forms.ChoiceField(choices=CONCEPT_CHOICES, label='Concepto' , required=False,widget=forms.Select(attrs={'data-control': 'select2'}))
    
    payroll = forms.ChoiceField(choices=EMPLOYEE_CHOICES, label='Nómina' , required=False,widget=forms.Select(attrs={'data-control': 'select2'}))
    
    employee = forms.ChoiceField(choices=EMPLOYEE_CHOICES, label='Empleado' , required=False,widget=forms.Select(attrs={'data-control': 'select2'}))
    
    month = forms.ChoiceField(choices=MONTH_CHOICES, label='Mes Acumular' , required=False)
    
    year = forms.ChoiceField(choices=YEAR_CHOICES, label='Año Acumular' , required=False)
    
    def clean(self):
        cleaned_data = super().clean()
        filled_fields_count = sum(1 for field in self.fields if cleaned_data.get(field))
        
        if filled_fields_count < 2:
            raise forms.ValidationError('Debe Seleccionar al menos dos campos.' )

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        idempresa = kwargs.pop('idempresa', None)
        super().__init__(*args, **kwargs)

        # Actualizar choices dinámicamente
        self.fields['sconcept'].choices = [('', '----------')] + [(concepto, concepto) for concepto in Nomina.objects.filter(idnomina__id_empresa = idempresa ).values_list('idconcepto__nombreconcepto', flat=True).distinct().order_by('idconcepto__nombreconcepto') ]
        self.fields['payroll'].choices = [('', '----------')] + [(idnomina, nombrenomina) for nombrenomina, idnomina in Nomina.objects.filter(idnomina__id_empresa = idempresa ).select_related('idnomina').values_list('idnomina__nombrenomina', 'idnomina').distinct().order_by('-idnomina')]
        self.fields['employee'].choices = [('', '----------')] + [(idempleado, f"{papellido} {sapellido} {pnombre} {snombre} ") for idempleado, pnombre, snombre, papellido, sapellido in Contratosemp.objects.filter(id_empresa = idempresa ).values_list('idempleado', 'pnombre', 'snombre', 'papellido', 'sapellido').distinct().order_by('papellido')]
        #self.fields['month'].choices = [('', '----------')] + [(mes, mes) for mes in range(1, 13)]
        #self.fields['year'].choices = [('', '----------')] + [(ano, ano) for ano in Nomina.objects.values_list('idnomina__anoacumular__ano', flat=True).distinct().order_by('-idnomina__anoacumular__ano')]
        
        self.fields['year'] = forms.ChoiceField(
            choices=[('', '----------')] + [(ano, ano) for ano in Nomina.objects.values_list('idnomina__anoacumular__ano', flat=True).distinct().order_by('-idnomina__anoacumular__ano')],
            label='Año Acumular',
            required=False,
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'data-hide-search': 'true',
                'class': 'form-select',
            })
        )
        
        self.fields['month'] = forms.ChoiceField(
            choices= MONTH_CHOICES ,
            required=False,
            label='Mes Acumular',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'data-hide-search': 'true',
                'class': 'form-select',
            })
        )

        # self.fields['cost_center'] = forms.ChoiceField(choices=[('', '----------')] + [(costo.idcosto, costo.nomcosto) for costo in Costos.objects.all()], label='Centro de Costos', required=False,)
        # self.fields['city'] = forms.ChoiceField(choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.all().order_by('ciudad')[:10]], label='Lugar de trabajo' , required=False, widget=forms.Select(attrs={'data-control': 'select2'}))

        self.helper = FormHelper()
        self.helper.form_id = 'Filto_conceptos'
        self.helper.layout = Layout(
            Row(
                Column('sconcept', css_class='form-group mb-0'),
                Column('payroll', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                Column('employee', css_class='form-group mb-0'),
                Column('month', css_class='form-group mb-0'),
                Column('year', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                Column(
                    Submit('submit', 'Filtrar', css_class='btn btn-light-info w-100'),  # Botón de envío
                    css_class='col-md-6'
                ),
                Column(
                    Button('button', 'Limpiar filtrado', css_class='btn btn-light-primary w-100', id='my-custom-button'),  # Botón sin acción de envío
                    css_class='col-md-6'
                ),
                css_class='row'
            ),
            
            
        )
    
    
