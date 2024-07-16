from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.companies.models import Contabgrupos , Nomina
from apps.companies.models import Tipodocumento ,Cargos, Centrotrabajo,Paises , Tipodenomina , Ciudades , Tipocontrato , ModelosContratos ,Tiposalario , Bancos , Costos ,Subcostos , Entidadessegsocial,Sedes


CONCEPT_CHOICES = [
        ('', '---------------'),
        ('1', 'Concepto 1'),
        ('2', 'Concepto 2'),
        ('3', 'Concepto 3'),
        # Agrega más opciones según sea necesario
    ]


MONTH_CHOICES = [
    ('', '---------------'),
    ('1', 'Enero'),
    ('2', 'Febrero'),
    ('3', 'Marzo'),
    ('4', 'Abril'),
    ('5', 'Mayo'),
    ('6', 'Junio'),
    ('7', 'Julio'),
    ('8', 'Agosto'),
    ('9', 'Septiembre'),
    ('10', 'Octubre'),
    ('11', 'Noviembre'),
    ('12', 'Diciembre'),
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
    month = forms.ChoiceField(choices=MONTH_CHOICES, label='Mes' , required=False)
    year = forms.ChoiceField(choices=YEAR_CHOICES, label='Año' , required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['sconcept'] = forms.ChoiceField(choices=[('', '----------')] + [(concepto, concepto) for concepto in Nomina.objects.values_list('nombreconcepto', flat=True).distinct() ], label='Empleado', required=False,)
        self.fields['year'] = forms.ChoiceField(
            choices=[('', '----------')] + [(ano, ano) for ano in Nomina.objects.values_list('anoacumular', flat=True).distinct()],
            label='Año Acumular',
            required=False
        )
        
        # self.fields['cost_center'] = forms.ChoiceField(choices=[('', '----------')] + [(costo.idcosto, costo.nomcosto) for costo in Costos.objects.all()], label='Centro de Costos', required=False,)
        # self.fields['city'] = forms.ChoiceField(choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.all().order_by('ciudad')[:10]], label='Lugar de trabajo' , required=False, widget=forms.Select(attrs={'data-control': 'select2'}))

        self.helper = FormHelper()
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
        )
    
    
