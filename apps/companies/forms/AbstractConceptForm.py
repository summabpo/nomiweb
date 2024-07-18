from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column , Div
from apps.companies.models import Contabgrupos , Nomina
from apps.companies.models import Contratosemp


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
    

    
    sconcept = forms.ChoiceField(choices=CONCEPT_CHOICES, label='Concepto' , required=False)
    
    payroll = forms.ChoiceField(choices=EMPLOYEE_CHOICES, label='Nómina' , required=False)
    
    employee = forms.ChoiceField(choices=EMPLOYEE_CHOICES, label='Empleado' , required=False)
    
    month = forms.ChoiceField(choices=MONTH_CHOICES, label='Mes Acumular' , required=False)
    
    year = forms.ChoiceField(choices=YEAR_CHOICES, label='Año Acumular' , required=False)
    
    def clean(self):
        cleaned_data = super().clean()
        filled_fields_count = sum(1 for field in self.fields if cleaned_data.get(field))
        
        if filled_fields_count < 2:
            raise forms.ValidationError('Debe completar al menos dos campos.')

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['sconcept'] = forms.ChoiceField(choices=[('', '----------')] + [(concepto, concepto) for concepto in Nomina.objects.values_list('nombreconcepto', flat=True).distinct() ], label='Concepto', required=False, widget=forms.Select(attrs={'data-control': 'select2'}) )
        
        self.fields['year'] = forms.ChoiceField(
            choices=[('', '----------')] + [(ano, ano) for ano in Nomina.objects.values_list('anoacumular', flat=True).distinct()],
            label='Año Acumular',
            required=False
        )
                
        self.fields['employee'] = forms.ChoiceField(
            choices=[('', '----------')] + [(idempleado, f"{pnombre} {snombre} {papellido} {sapellido}") for idempleado, pnombre, snombre, papellido, sapellido , in Contratosemp.objects.values_list('idempleado', 'pnombre', 'papellido','snombre', 'sapellido')],
            label='Empleado',
            required=False, 
            widget=forms.Select(attrs={'data-control': 'select2'})
        )
        
        self.fields['payroll'] = forms.ChoiceField(
            choices=[('', '----------')] + [(idnomina, nombrenomina) for nombrenomina, idnomina in Nomina.objects.select_related('idnomina').values_list('idnomina__nombrenomina', 'idnomina').distinct().order_by('-idnomina')],
            label='Nómina',
            required=False,
            widget=forms.Select(attrs={'data-control': 'select2'})
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
                    Submit('submit', 'Filtrar', css_class='btn btn-light-info w-100'),  # 100% ancho de la columna
                    css_class='col-md-6'  # Ancho especificado
                ),
                Column(
                    Submit('submit', 'Limpiar filtrado', css_class='btn btn-light-primary w-100'),  # 100% ancho de la columna
                    css_class='col-md-6'  # Ancho especificado
                ),
                css_class='row'
            )
            
        )
    
    
