from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.common.models import Entidadessegsocial, Contratos , Tipocontrato
from django.urls import reverse

class updatesalaryForm(forms.Form):
    Salario_Actual = forms.DecimalField(
        label='Salario Actual',
        required=True,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': '0.00'})
    )
    Salario_nuevo = forms.DecimalField(
        label='Salario Nuevo',
        required=True,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': '0.00'})
    )
    fecha_nuevo = forms.DateField(
        label='Fecha Nuevo Salario',
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
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
                    f"{item['idempleado__papellido']} {item['idempleado__pnombre']} - "
                    f"{item['cargo__nombrecargo']} - Contrato #{item['idcontrato']}"
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
                    'idcontrato', 'cargo__nombrecargo'
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

        self.fields['contractType'] = forms.ChoiceField(
            choices=[
                (contrato.idtipocontrato, contrato.tipocontrato)
                for contrato in Tipocontrato.objects.exclude(
                    idtipocontrato__in=[5, 6, 7]
                ).order_by('-tipocontrato')
            ],
            label='Tipo de Contrato',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'class': 'form-select',
                'data-placeholder': 'Seleccione un tipo',
                'data-hide-search': 'true',
            }),
            required=True
        )

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_family'
        self.helper.enctype = 'multipart/form-data'

        self.helper.attrs.update({
            'up-target': '#modal-content',
            'up-mode': 'replace',
            'up-layer': 'current',  # Clave para resolver el error
            'up-submit': reverse('companies:update_salary_add'),
            'up-accept-location': reverse('companies:update_salary_add'),
            'up-on-accepted': 'up.modal.close()',  # Cierra el modal al aceptar
        })
        
        
        self.helper.layout = Layout(
            Row(
                Column('contract', css_class='form-group col-md-12 mb-0'),
                css_class='row'
            ),
            Row(
                Column('Salario_Actual', css_class='form-group col-md-12 mb-0'),
                css_class='row'
            ),
            Row(
                Column('Salario_nuevo', css_class='form-group col-md-12 mb-0'),
                css_class='row'
            ),
            Row(
                Column('fecha_nuevo', css_class='form-group col-md-12 mb-0'),
                css_class='row'
            ),
                Row(
                Column('contractType', css_class='form-group col-md-12 mb-0'),
                css_class='row'
            ),
        )
