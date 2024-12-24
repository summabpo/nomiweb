from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.common.models import Empresa

TIPE_CHOICES = (
    ('', '-------------'),
    ('1', 'Mensual'),
    ('2', 'Quincenal'),
    ('3', 'Por Horas'),
    ('4', 'Primas'),
    ('5', 'Cesantías'),
    ('6', 'Adicional'),
    ('7', 'Vacaciones'),
    ('8', 'Liquidación'),
    ('9', 'Catorcenal'),
    ('10', 'Int. de Cesantías'),
    ('11', 'Semanal'),
)

class PayrollForm(forms.Form):
    fechainicial = forms.DateField(
        label='Fecha Inicial',
        widget=forms.TextInput(attrs={'type': 'date', 'placeholder': 'Seleccione la fecha inicial'})
    )
    fechafinal = forms.DateField(
        label='Fecha Final',
        widget=forms.TextInput(attrs={'type': 'date', 'placeholder': 'Seleccione la fecha final'})
    )
    fechapago = forms.DateField(
        label='Fecha de Pago',
        widget=forms.TextInput(attrs={'type': 'date', 'placeholder': 'Seleccione la fecha de pago'})
    )
    tiponomina = forms.ChoiceField(
        label='Tipo de Nómina',
        choices=TIPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    diasnomina = forms.IntegerField(
        label='Días de Nómina',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': ''})
    )

    nombrenomina = forms.CharField(
        label='Nombre Nomina',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': ''})
    )
 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['tiponomina'].widget.attrs.update({
            'data-control': 'select2',
            'data-tags': 'true',
            'class': 'form-select',
            'data-hide-search': "true",
            'data-dropdown-parent':"#kt_modal_maintenance",
        })

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_payroll'
        self.helper.enctype = 'multipart/form-data'

        self.helper.layout = Layout(
            Row(
                Column('nombrenomina', css_class='form-group  col-md-10 mb-0'),
                Column('diasnomina', css_class='form-group  col-md-2 mb-0'),
                css_class='row'
            ),
            
            Row(
                Column('fechainicial', css_class='form-group  col-md-6 mb-0'),
                Column('fechafinal', css_class='form-group  col-md-6 mb-0'),
                
                css_class='row'
            ),
            Row(
                Column('tiponomina', css_class='form-group  col-md-6 mb-0'),
                Column('fechapago', css_class='form-group  col-md-6 mb-0'),
                css_class='row'
            ),
        )
