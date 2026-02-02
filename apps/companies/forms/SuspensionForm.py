from django import forms
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from apps.common.models import Contratos


SUSPENSION_TYPE_CHOICES = (
    ('', '----------'),
    
)

ABSENCE_TYPE_CHOICES = (
    ('', '----------'),
    ('3', 'Licencia Remunerada'),
    ('4', 'Licencia No Remunerada'),
    ('5', 'Suspension'),
)


class SuspensionForm(forms.Form):

    initial_date = forms.CharField(
            label='Fecha de Inicio de la Novedad',
            widget=forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Seleccione una fecha',
                'id': 'kt_daterangepicker_1'
            })
        )
        
    sus_days = forms.IntegerField(
                label="Días de Novedad",
                initial=0,
                min_value=0,
                widget=forms.NumberInput(attrs={'class': 'form-control'})
            )
        
    end_date  = forms.CharField(
            label="Fin de la Novedad",
            required=False ,
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '',
                'id': 'kt_daterangepicker_2' 
            })
        )
    


    def __init__(self, *args, **kwargs):
        idempresa = kwargs.pop('idempresa', None)
        super().__init__(*args, **kwargs)

        self.fields['contract'] = forms.ChoiceField(
            label="Contrato",
            choices=[('', '----------')] + [
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
                ).order_by('idempleado__papellido').values(
                    'idempleado__pnombre',
                    'idempleado__snombre',
                    'idempleado__papellido',
                    'idempleado__sapellido',
                    'idcontrato',
                    'cargo__nombrecargo'
                )
            ],
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-placeholder': 'Seleccione un contrato',
                'class': 'form-select'
            })
        )



        self.fields['absence_type'] = forms.ChoiceField(
            label="Tipo de ausencia",
            choices=ABSENCE_TYPE_CHOICES,
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-placeholder': 'Tipo de ausencia',
                'class': 'form-select'
            })
        )

        # 🔹 Crispy
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'container'
        self.helper.form_id = 'form_suspension'
        self.helper.enctype = 'multipart/form-data'

        self.helper.attrs.update({
            'up-target': '#modal-content',
            'up-mode': 'replace',
            'up-layer': 'current',
            'up-submit': reverse('companies:suspension_list_add'),
            'up-accept-location': reverse('companies:suspension_list_add'),
        })

        self.helper.layout = Layout(

            Row(
                Column('contract', css_class='col-md-6 mb-2'),
                Column('absence_type', css_class='col-md-6 mb-2'),
            ),

            Row(
                Column('initial_date', css_class='col-md-4 mb-2'),
                Column('sus_days', css_class='col-md-4 mb-2'),
                Column('end_date', css_class='col-md-4 mb-2'),
            ),
        )


