from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML
from apps.common.models import Entidadessegsocial, Contratos , Tipocontrato
from django.urls import reverse

class SettlementlistForm(forms.Form):
    contrato = forms.IntegerField(
        label='Contrato',
        required=True,
        widget=forms.NumberInput(attrs={'placeholder': 'Número de contrato'})
    )

    documento_identidad = forms.CharField(
        label='Documento de Identidad',
        required=True,
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Cédula o NIT'})
    )

    salario = forms.DecimalField(
        label='Salario',
        required=True,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': '0.00'})
    )

    motivo_retiro = forms.CharField(
        label='Motivo de Retiro',
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Motivo del retiro'})
    )

    fecha_inicio_contrato = forms.DateField(
        label='Fecha Inicio del Contrato',
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    fecha_final_contrato = forms.DateField(
        label='Fecha Final del Contrato',
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    dias_trabajados = forms.IntegerField(
        label='Días Trabajados',
        required=True,
        widget=forms.NumberInput(attrs={'placeholder': '0'})
    )

    base_cesantias = forms.DecimalField(
        label='Base Cesantías',
        required=True,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': '0.00'})
    )

    dias_cesantias = forms.IntegerField(
        label='Días Cesantías',
        required=True,
        widget=forms.NumberInput(attrs={'placeholder': '0'})
    )

    base_prima = forms.DecimalField(
        label='Base Prima',
        required=True,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': '0.00'})
    )

    dias_prima = forms.IntegerField(
        label='Días Prima',
        required=True,
        widget=forms.NumberInput(attrs={'placeholder': '0'})
    )

    base_vacaciones = forms.DecimalField(
        label='Base Vacaciones',
        required=True,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': '0.00'})
    )

    dias_vacaciones = forms.IntegerField(
        label='Días Vacaciones',
        required=True,
        widget=forms.NumberInput(attrs={'placeholder': '0'})
    )

    dias_suspension_cesantias = forms.IntegerField(
        label='Días Susp. Cesantías',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': '0'})
    )

    dias_suspension_vacaciones = forms.IntegerField(
        label='Días Susp. Vacaciones',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': '0'})
    )
    
    cesantias = forms.IntegerField(
        label='Cesantías',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': '0'})
    )
    
    intereses = forms.IntegerField(
        label='Intereses',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': '0'})
    )
    
    
    prima = forms.IntegerField(
        label='Prima',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': '0'})
    )

    vacaciones = forms.IntegerField(
        label='Vacaciones',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': '0'})
    )

    indemnizacion = forms.IntegerField(
        label='Indemnización',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': '0'})
    )

    total = forms.IntegerField(
        label='Total liquidacion',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': '0'})
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
            # 🔹 Identificación del contrato
            Row(
                Column('contrato', css_class='form-group col-md-6 mb-0'),
                Column('documento_identidad', css_class='form-group col-md-6 mb-0'),
                css_class='row'
            ),

            # 🔹 Información básica
            Row(
                Column('salario', css_class='form-group col-md-6 mb-0'),
                Column('motivo_retiro', css_class='form-group col-md-6 mb-0'),
                css_class='row'
            ),

            # 🔹 Fechas del contrato y Días trabajados
            Row(
                Column('fecha_inicio_contrato', css_class='form-group col-md-4 mb-0'),
                Column('fecha_final_contrato', css_class='form-group col-md-4 mb-0'),
                Column('dias_trabajados', css_class='form-group col-md-4 mb-0'),
                css_class='row'
            ),

            # 🔹 dias
            Row(
                
                Column('dias_cesantias', css_class='form-group col-md-4 mb-0'),
                Column('dias_prima', css_class='form-group col-md-4 mb-0'),
                Column('dias_vacaciones', css_class='form-group col-md-4 mb-0'),
                css_class='row'
            ),

            # 🔹 bases
            Row(
                Column('base_cesantias', css_class='form-group col-md-4 mb-0'),
                Column('base_prima', css_class='form-group col-md-4 mb-0'),
                Column('base_vacaciones', css_class='form-group col-md-4 mb-0'),
                css_class='row'
            ),

            # 🔹 Suspensiones (opcionales)
            Row(
                Column('dias_suspension_cesantias', css_class='form-group col-md-6 mb-0'),
                Column('dias_suspension_vacaciones', css_class='form-group col-md-6 mb-0'),
                css_class='row'
            ),
            HTML('<h3>Datos Calculados</h3>'),
            Row(
                Column(
                    'cesantias',
                    'intereses',
                    'prima',
                    'vacaciones',
                    'indemnizacion',
                    'total',
                    css_class='form-group col-md-6 mb-0'
                ),
                css_class='row'
            ),
            
        )
