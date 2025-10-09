from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.urls import reverse
from django.utils.safestring import mark_safe
from apps.common.models import Entidadessegsocial, Contratos , Tipocontrato

class TimeForm(forms.Form):
    fechaingreso = forms.DateField(
        label='Fecha de ingreso',
        widget=forms.DateInput(
            attrs={
                'placeholder': 'dd-mm-aaaa',
                'class': 'form-control',
                'type': 'date',  # HTML5 date picker
            },
            format='%Y-%m-%d'
        ),
        input_formats=['%Y-%m-%d', '%d-%m-%Y'],
    )
    fechasalida = forms.DateField(
        label='Fecha de salida',
        widget=forms.DateInput(
            attrs={
                'placeholder': 'dd-mm-aaaa',
                'class': 'form-control',
                'type': 'date',  # HTML5 date picker
            },
            format='%Y-%m-%d'
        ),
        input_formats=['%Y-%m-%d', '%d-%m-%Y'],
    )

    horaingreso = forms.TimeField(
        label='Hora de ingreso',
        widget=forms.TimeInput(
            attrs={
                'placeholder': 'hh:mm',
                'class': 'form-control',
                'type': 'time',  # HTML5 time picker
            },
            format='%H:%M'
        ),
        input_formats=['%H:%M', '%H:%M:%S'],
    )

    horasalida = forms.TimeField(
        label='Hora de salida',
        widget=forms.TimeInput(
            attrs={
                'placeholder': 'hh:mm',
                'class': 'form-control',
                'type': 'time',
            },
            format='%H:%M'
        ),
        input_formats=['%H:%M', '%H:%M:%S'],
    )

    horasdescuentos = forms.DecimalField(
        label='Horas de descuento',
        max_digits=5,
        decimal_places=2,
        initial=0,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Horas de descuento',
            'class': 'form-control'
        })
    )

    def __init__(self, *args, **kwargs):
        idempresa = kwargs.pop('idempresa', None)
        super().__init__(*args, **kwargs)

        self.fields['contract'] = forms.ChoiceField(
            choices=[
                ('', 'Seleccione un contrato')
            ] + [
                (
                    item['idcontrato'],
                    f"{item['idempleado__papellido']} {item['idempleado__pnombre']} - Contrato #{item['idcontrato']}" 
                )
                for item in Contratos.objects.filter(
                    estadocontrato=1,
                    id_empresa=idempresa
                ).exclude(
                    tipocontrato__idtipocontrato__in=[5, 6]
                ).order_by('idempleado__papellido')
                .values(
                    'idempleado__pnombre', 'idempleado__snombre',
                    'idempleado__papellido', 'idempleado__sapellido',
                    'idcontrato',
                )
            ],
            label="Contrato",
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-placeholder': 'Seleccione un contrato',
                'data-allow-clear': "true",
                'id': 'contract-select'
            }),
            required=True
        )
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_time'
        self.helper.enctype = 'multipart/form-data'

        self.helper.attrs.update({
            'up-target': '#modal-content',
            'up-mode': 'replace',
            'up-layer': 'current',
            # 'up-submit': reverse('payroll:time_edit'),
            # 'up-accept-location': reverse('payroll:time_edit'),
            'up-on-accepted': 'up.modal.close()',
        })

        self.helper.layout = Layout(
            Row(
                Column('contract', css_class='form-group col-md-12 mb-0'),
                css_class='row'
            ),
            Row(
                Column('fechaingreso', css_class='form-group col-md-6 mb-0'),
                Column('fechasalida', css_class='form-group col-md-6 mb-0'),
                css_class='row'
            ),
            Row(
                Column('horaingreso', css_class='form-group col-md-4 mb-0'),
                Column('horasalida', css_class='form-group col-md-4 mb-0'),
                Column('horasdescuentos', css_class='form-group col-md-4 mb-0'),
                css_class='row'
            ),
        )