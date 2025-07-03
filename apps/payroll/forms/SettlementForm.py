from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.common.models import Conceptosdenomina , Indicador, Contratos
from django.urls import reverse
from django.utils.safestring import mark_safe

TIPE_CHOICES = [
    ('', '-------------'),
    ('renuncia voluntaria', 'Renuncia Voluntaria'),
    ('despido sin justa causa', 'Despido sin justa causa'),
    ('despido con justa causa', 'Despido con justa causa'),
    ('finalizacion contrato', 'Finalización del contrato'),
    ('cambio salario integral', 'Cambio a salario integral'),
    ('muerte trabajador', 'Muerte del trabajador'),
    ('despido periodo prueba', 'Despido en periodo de prueba'),
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
        super().__init__(*args, **kwargs)
        
        
        
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_settlement'
        self.helper.enctype = 'multipart/form-data'

        self.helper.attrs.update({
            'up-target': '#modal-content',
            'up-mode': 'replace',
            'up-layer': 'current',  # Clave para resolver el error
            'up-submit': reverse('payroll:settlement_create'),
            'up-accept-location': reverse('payroll:settlement_create'),
            'up-on-accepted': 'up.modal.close()',  # Cierra el modal al aceptar
        })
        
        
        self.fields['contract'] = forms.ChoiceField(
            choices=[('', '----------')] + [
                (idcontrato, f"{(idempleado__papellido or '').strip()} {(idempleado__sapellido or '').strip()} "
                            f"{(idempleado__pnombre or '').strip()} {(idempleado__snombre or '').strip()} - {idcontrato}")
                for idempleado__pnombre, idempleado__snombre, idempleado__papellido, idempleado__sapellido, idcontrato 
                in Contratos.objects.filter(estadocontrato=1, id_empresa=idempresa)
                .order_by('idempleado__papellido')
                .values_list('idempleado__pnombre', 'idempleado__snombre', 'idempleado__papellido', 'idempleado__sapellido', 'idcontrato')
            ],
            label="Contrato",
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'class': 'form-select'
            })
        )
        
        self.fields['reason_for_termination'].widget.attrs.update({
            'data-control': 'select2',
            'data-tags': 'true',
            'class': 'form-select',
            'data-hide-search': "true",

        })
        
        self.helper.layout = Layout(
            
            Row(
                Column('contract', css_class='form-group  col-md-4 mb-0'),
                Column('end_date', css_class='form-group col-md-4 mb-0'),
                Column('reason_for_termination', css_class='form-group  col-md-4 mb-0'),
                css_class='row'
            ),
            
            Row(
                
                css_class='row'
            ),

        )




class FamilyForm2(forms.Form):
    

    name = forms.CharField(
        label='Nombre de la familia',
        required=False ,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre de la familia',
            'class': 'form-control',  # Bootstrap o compatible
            'disabled': 'disabled'
    
        })
    )
    
    
    descrip = forms.CharField(
        label='Descripción',
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Escribe una pequeña descripción',
            'maxlength':"35",
            'class': 'form-control',  # Bootstrap o compatible
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')

        if name:
            if Indicador.objects.filter(nombre=name).exists():
                self.add_error(
                    'name', 
                    "Este nombre de familia ya está en uso. Por favor, elige uno diferente."
                )

        return cleaned_data

    
    def __init__(self, *args, **kwargs):
        idempresa = kwargs.pop('idempresa', None)
        super().__init__(*args, **kwargs)
        
        
        self.fields['idconcepto'] = forms.MultipleChoiceField(
            choices=[(concepto.idconcepto, f"{concepto.nombreconcepto}") for concepto in Conceptosdenomina.objects.filter( id_empresa = idempresa ).order_by('nombreconcepto')],
            required=False,
            label='Seleccione un Concepto',
            widget=forms.SelectMultiple(attrs={
                'data-control': 'select2',
                'data-close-on-select': "false",
                'data-placeholder': 'Seleccione un Indicador',
                'data-allow-clear': "true",
                'multiple': "multiple",

            })
        )
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_family'
        self.helper.enctype = 'multipart/form-data'

        self.helper.attrs.update({
            'up-target': '#modal-content2',
            'up-mode': 'replace',
            'up-layer': 'current',  # Clave para resolver el error
            'up-submit': reverse('payroll:family_create'),
            'up-accept-location': reverse('payroll:family_create'),
            'up-on-accepted': 'up.modal.close()',  # Cierra el modal al aceptar
        })
        
        self.helper.layout = Layout(
            
            Row(
                Column('name', css_class='form-group  col-md-6 mb-0'),
                Column('descrip', css_class='form-group col-md-6 mb-0'),
                css_class='row'
            ),
            
            Row(
                Column('idconcepto', css_class='form-group  col-md-12 mb-0'),
                css_class='row'
            ),

        )
