from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.companies.models import Contabgrupos
from apps.companies.models import Tipodocumento ,Cargos, Centrotrabajo,Paises , Tipodenomina , Ciudades , Tipocontrato , ModelosContratos ,Tiposalario , Bancos , Costos ,Subcostos , Entidadessegsocial,Sedes


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

CITY_CHOICES = [
    ('', '---------------'),
    ('1', 'Ciudad 1'),
    ('2', 'Ciudad 2')
]



class ReportFilterForm(forms.Form):
    

    start_date = forms.DateField(required=False, label='Fecha Inicial', widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField( required=False, label='Fecha Final', widget=forms.DateInput(attrs={'type': 'date'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['employee'] = forms.ChoiceField(choices=[('', '----------')] + [(costo.idcosto, costo.nomcosto) for costo in Costos.objects.all()], label='Empleado', required=False,)
        self.fields['cost_center'] = forms.ChoiceField(choices=[('', '----------')] + [(costo.idcosto, costo.nomcosto) for costo in Costos.objects.all()], label='Centro de Costos', required=False,)
        self.fields['city'] = forms.ChoiceField(choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.all().order_by('ciudad')[:10]], label='Lugar de trabajo' , required=False, widget=forms.Select(attrs={'data-control': 'select2'}))

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('employee', css_class='form-group mb-0'),
                Column('cost_center', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                Column('city', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                Column('start_date', css_class='form-group mb-0'),
                Column('end_date', css_class='form-group mb-0'),
                css_class='row'
            ),
        )
    
    
