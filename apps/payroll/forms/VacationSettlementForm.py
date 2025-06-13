from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML
from apps.common.models import Contratos

class VacationSettlementForm(forms.Form):

    TYPE_CHOICES = (

        ('', ''),
        ('1', 'Vacaciones'),
        ('2', 'Ausensias'),
        
    )

    pay_date = forms.CharField(
        label='Fecha de pago',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Seleccione una fecha',
        })
    )

    type_novedad = forms.ChoiceField(
        label='Tipo de Novedad',
        choices=TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select input-group-sm',
            'data-control': 'select2',
            'data-hide-search': 'true',
            'data-placeholder': 'Seleccione Novedad',
        })
    )



    def __init__(self, *args, **kwargs):
        id_empresa = kwargs.pop('id_empresa', None)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_loans'
        self.helper.enctype = 'multipart/form-data'

        self.fields['contract'] = forms.ChoiceField(
            choices=[('', '----------')] + [
                (
                    idcontrato,
                    f"{(idempleado__papellido or '').strip()} {(idempleado__sapellido or '').strip()} "
                    f"{(idempleado__pnombre or '').strip()} {(idempleado__snombre or '').strip()} - {idcontrato}"
                )
                for idempleado__pnombre, idempleado__snombre, idempleado__papellido, idempleado__sapellido, idcontrato
                in Contratos.objects.filter(
                    estadocontrato=1,
                    id_empresa=id_empresa
                ).order_by('idempleado__papellido')
                .values_list(
                    'idempleado__pnombre',
                    'idempleado__snombre',
                    'idempleado__papellido',
                    'idempleado__sapellido',
                    'idcontrato'
                )
            ],
            label="Empleado",
            widget=forms.Select(attrs={
                'class': 'form-select input-group-sm',
                'data-control': 'select2'
            })
        )

        self.helper.layout = Layout(
            Row(
                Column('contract', css_class='form-group col-md-12 mb-3'),
                css_class='row'
            ),
            Row(
                Column('pay_date', css_class='form-group col-md-6 mb-3'),
                Column('type_novedad', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            HTML('<div class="separator my-10"></div>'),
            # Row(
            #     Column('novedad', css_class='form-group col-md-2'),
            #     Column('init_date', css_class='form-group col-md-2'),
            #     Column('end_date', css_class='form-group col-md-2'),
            #     Column('day_c', css_class='form-group col-md-1'),
            #     Column('day_r', css_class='form-group col-md-1'),
            #     Column('base', css_class='form-group col-md-2'),
            #     Column('value', css_class='form-group col-md-2'),
            #     css_class='row'
            # ),
            
        )



class BenefitForm(forms.Form):
    name = forms.CharField(label="Nombre del beneficio", max_length=100)
    amount = forms.DecimalField(label="Monto", max_digits=10, decimal_places=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # para evitar form en cada fila
        self.helper.layout = Layout(
            Row(
                Column('name', css_class="col-md-6"),
                Column('amount', css_class="col-md-4"),
            )
        )

BenefitFormSet = forms.formset_factory(BenefitForm, extra=1, can_delete=True)