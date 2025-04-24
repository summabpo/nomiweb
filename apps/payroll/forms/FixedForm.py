from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.common.models import Empresa, Contratos, Conceptosdenomina
from django.urls import reverse
from django.utils.safestring import mark_safe


TIPO_CHOICES = (
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

ESTADO_CHOICES = (
    (True, 'Activo'),
    (False, 'Cerrado'),
)

PAGO_CHOICES = (
    ('', '-------------'),
    ('mensual', 'Mensual'),
    ('quincenal', 'Quincenal'),
    ('anual', 'Anual'),
)

class FixidForm(forms.Form):
    idcontrato = forms.ChoiceField(
        label='Empleado',
        choices=TIPO_CHOICES,  # Suponiendo que esto se cambia luego por contratos reales
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    valor = forms.IntegerField(
        label='Valor',
        widget=forms.NumberInput(attrs={'placeholder': 'Ej: 100000'})
    )

    descrip = forms.CharField(
        label='Descripción',
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Escribe una descripción detallada...',
            #'rows': 3,
            'maxlength':"35",
            'class': 'form-control',  # Bootstrap o compatible
            #'style': 'resize: none; height: 100px; max-width: 600px;'  # ancho fino y redimensionable verticalmente
        })
    )

    idconcepto = forms.ChoiceField(
        label='Concepto',
        choices=TIPO_CHOICES,  # Esto también sería ideal cambiarlo por Conceptosdenomina reales
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    estado = forms.ChoiceField(
        label='Estado',
        choices=ESTADO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


    fecha = forms.DateField(
        label='Fecha fin',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def __init__(self, *args, **kwargs):
        idempresa = kwargs.pop('idempresa', None)
        
        super().__init__(*args, **kwargs)
        
        self.fields['descrip'].help_text = mark_safe(
            '<span class="fs-6 text-muted"> Máximo 35 caracteres. Describe brevemente la situación. </span> '
        )

        self.fields['idconcepto'].choices = [('', '-------------')] + [(concepto.idconcepto, f"{concepto.nombreconcepto}") for concepto in Conceptosdenomina.objects.all()]
        self.fields['idcontrato'].choices = [('', '-------------')] + [(contra.idcontrato, f"{contra.idempleado.papellido } {contra.idempleado.sapellido } {contra.idempleado.pnombre } -- {contra.cargo.nombrecargo } -- Contrato #{contra.idcontrato} ") for contra in Contratos.objects.filter(estadocontrato=1, id_empresa=idempresa) .order_by('idempleado__papellido')]
        

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_login'
        self.helper.enctype = 'multipart/form-data'

        # Atributos específicos para Unpoly
        self.helper.attrs.update({
            'up-target': '#modal-content',
            'up-mode': 'replace',
            'up-layer': 'current',
            'up-submit': reverse('payroll:fixed_modal'),
            'up-accept-location': reverse('payroll:fixedconcepts'),
            'up-on-accepted': ""
        })


        for field_name in ['idconcepto', 'idcontrato']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'data-control': 'select2',
                    'class': 'form-select',
                })


        for field_name in ['estado']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'data-control': 'select2',
                    'class': 'form-select',
                    'data-hide-search':"true",

                })


        self.helper.layout = Layout(
            Row(
                Column('idcontrato', css_class='form-group  col-md-12 mb-0'),
                css_class='row'
            ),
            
            Row(
                Column('idconcepto', css_class='form-group  col-md-6 mb-0'),
                Column('valor', css_class='form-group  col-md-6 mb-0'),
                css_class='row'
            ),

            Row(
                Column('estado', css_class='form-group  col-md-6 mb-0'),
                Column('fecha', css_class='form-group  col-md-6 mb-0'),
                css_class='row'
            ),
            Row(
                Column('descrip', css_class='form-group  col-md-12 mb-0'),
                css_class='row'
            ),

        )
