from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, Submit
from apps.common.models import Contratos , Crearnomina
from django.urls import reverse


class BonusForm(forms.Form):
    
    init_Date = forms.CharField(
        label='Fecha Inicio periodo',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'id': 'kt_daterangepicker_1'
        })
    )

    end_date = forms.CharField(
        label='Fecha fin periodo',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'id': 'kt_daterangepicker_2'
        })
    )
    
    estimated_bonus = forms.IntegerField(
        label='Proyecion',
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': ''
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_bonus'
        
        self.helper.layout = Layout(
            Row(
                Column('init_Date', css_class='form-group col-md-5 mb-3'),
                Column('end_date', css_class='form-group col-md-5 mb-3'),
                Column('estimated_bonus', css_class='form-group col-md-2 mb-3'),
                css_class='row'
            ),
            Row(
                Column(
                    Div(
                        Submit('submit', 'Generar', css_class='btn btn-primary w-100'),
                        css_class='d-grid'  # para que el botón ocupe todo el ancho de la columna
                    ),
                    css_class='form-group col-md-12 mb-3'
                ),
                css_class='row'
            )
            
        )


TYPE_CHOICES = (
    ('', '----------'),
    ('1', 'Prima Regular'),
    ('2', 'Prima PP'),
)

class BonusAddForm(forms.Form):
    
    method_type = forms.ChoiceField(
        label='Estado',
        choices=TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        idempresa = kwargs.pop('idempresa', None)
        super().__init__(*args, **kwargs)
        
        self.fields['Payroll'] = forms.ChoiceField(
            choices=[('', '----------')] + [(nomina.idnomina, f" {nomina.nombrenomina}" ) for nomina in Crearnomina.objects.filter(estadonomina=True, id_empresa_id=idempresa).order_by('-idnomina')], 
            label='Nomina' ,
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'class': 'form-select',
                'data-hide-search': 'true',
            }), 
            )



        for field_name in ['estado']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'data-control': 'select2',
                    'class': 'form-select',
                    'data-hide-search':"true",

                })

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_bonus_add'
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


        self.helper.layout = Layout(
            Row(
                Column('Payroll', css_class='form-group col-md-6 mb-3'),
                Column('method_type', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            
        )
