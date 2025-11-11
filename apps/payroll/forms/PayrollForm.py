from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.common.models import Empresa
from django.urls import reverse

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

        
        self.fields['tiponomina'] = forms.ChoiceField(
            choices=TIPE_CHOICES,
            label='Tipo de Nómina',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-placeholder': 'Seleccione un tipo',
                'data-hide-search': "true",
            })
        )

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_payroll'
        self.helper.enctype = 'multipart/form-data'


        self.helper.attrs.update({
            'up-target': '#modal-content',
            'up-mode': 'replace',
            'up-layer': 'current',  # Clave para resolver el error
            'up-submit': reverse('payroll:payroll_create_add'),
            'up-accept-location': reverse('payroll:payroll_create_add'),
            'up-on-accepted': 'up.modal.close()',  # Cierra el modal al aceptar
        })
        
        self.helper.layout = Layout(
            
            Row(
                Column('tiponomina', css_class='form-group  col-md-6 mb-0'),
                Column('fechapago', css_class='form-group  col-md-6 mb-0'),
                css_class='row'
            ),
            Row(
                Column('fechainicial', css_class='form-group  col-md-6 mb-0'),
                Column('fechafinal', css_class='form-group  col-md-6 mb-0'),
                
                css_class='row'
            ),
            Row(
                Column('nombrenomina', css_class='form-group  col-md-10 mb-0'),
                Column('diasnomina', css_class='form-group  col-md-2 mb-0'),
                css_class='row'
            ),
           
        )



