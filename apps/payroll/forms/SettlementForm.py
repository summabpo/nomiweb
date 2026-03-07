from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django.urls import reverse
from apps.common.models import Conceptosdenomina, Indicador, Contratos

TIPE_CHOICES = [
    ('', '-------------'),
    ('1', 'Renuncia Voluntaria'),
    ('2', 'Despido sin justa causa'),
    ('3', 'Despido con justa causa'),
    ('4', 'Finalización del contrato'),
    ('5', 'Cambio a salario integral'),
    ('6', 'Muerte del trabajador'),
    ('7', 'Despido en periodo de prueba'),
]


class SettlementForm(forms.Form):
    end_date = forms.CharField(
        label='Fecha fin Contrato',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'kt_daterangepicker_2'
        })
    )

    reason_for_termination = forms.ChoiceField(
        label='Motivo de Retiro',
        choices=TIPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        idempresa = kwargs.pop('idempresa', None)
        recibida = kwargs.pop('recibida', None)  # ✅ palabra clave para controlar edición
        super().__init__(*args, **kwargs)

        # 🧩 Construcción dinámica de contratos activos
        contratos_choices = [('', '----------')] + [
            (
                idcontrato,
                f"{(pap or '').strip()} {(sap or '').strip()} {(pnom or '').strip()} {(snom or '').strip()} - {idcontrato}"
            )
            for pnom, snom, pap, sap, idcontrato in
            Contratos.objects.filter(estadocontrato=1, id_empresa=idempresa)
            .order_by('idempleado__papellido')
            .values_list('idempleado__pnombre', 'idempleado__snombre',
                         'idempleado__papellido', 'idempleado__sapellido', 'idcontrato')
        ]

        self.fields['contract'] = forms.ChoiceField(
            label="Contrato",
            choices=contratos_choices,
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'class': 'form-select'
            })
        )

        # 🧠 Si la acción es editar, se bloquea el campo contrato
        if recibida == "edit":
            self.fields['contract'].widget.attrs['disabled'] = True
            self.fields['contract'].required = False

        # ✅ Configuración adicional del select motivo
        self.fields['reason_for_termination'].widget.attrs.update({
            'data-control': 'select2',
            'data-tags': 'true',
            'class': 'form-select',
            'data-hide-search': "true",
        })

        # 🧱 Configuración del helper Crispy
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_settlement'
        self.helper.enctype = 'multipart/form-data'

        self.helper.attrs.update({
            'up-target': '#modal-content',
            'up-mode': 'replace',
            'up-layer': 'current',
            'up-submit': reverse('payroll:settlement_create'),
            'up-accept-location': reverse('payroll:settlement_create'),
            'up-on-accepted': 'up.modal.close()',
        })

        self.helper.layout = Layout(
            Row(
                Column('contract', css_class='form-group col-md-4 mb-0'),
                Column('end_date', css_class='form-group col-md-4 mb-0'),
                Column('reason_for_termination', css_class='form-group col-md-4 mb-0'),
            )
        )
