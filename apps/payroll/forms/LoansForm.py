from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column ,HTML
from apps.common.models  import Contratos

class LoansForm(forms.Form):

    loan_amount = forms.IntegerField(required=True, label="Valor del Préstamo")
    installments_number = forms.IntegerField(
        required=False, 
        label="Cuotas del Préstamo",
    )
    installment_value = forms.IntegerField(required=True, label="Valor de la Cuota")
    
    loan_date = forms.CharField(
        label='Fecha Prestamo',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'id': 'kt_daterangepicker_1'
        })
    )

    def __init__(self, *args, **kwargs):
        id_empresa = kwargs.pop('id_empresa', None)  # Obtener id_empresa de los argumentos
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_loans'
        self.helper.enctype = 'multipart/form-data'

        # Configurar el campo contract dinámicamente
        self.fields['contract'] = forms.ChoiceField(
            choices=[('', '----------')] + [
                (item['idcontrato'], f"{item['idempleado__papellido']} {item['idempleado__sapellido']} {item['idempleado__pnombre']} {item['idempleado__snombre']} - {item['idcontrato']}")
                for item in Contratos.objects.filter(estadocontrato=1, id_empresa=id_empresa)
                .order_by('idempleado__papellido')
                .values('idempleado__pnombre', 'idempleado__snombre', 'idempleado__papellido', 'idempleado__sapellido', 'idcontrato')
            ],
            label="Contrato",
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-dropdown-parent': "#kt_modal_loans",
                'class': 'form-select'
            })
        )
        
        self.helper.layout = Layout(
            Row(
                Column('contract', css_class='form-group col-md-12 mb-3'),
                css_class='row'
            ),
            Row(
                Column('loan_amount', css_class='form-group col-md-4 mb-3'),
                Column('installment_value', css_class='form-group col-md-4 mb-3'),
                Column('installments_number', css_class='form-group col-md-4 mb-3'),
                css_class='row'
            ),
            Row(
                Column('loan_date', css_class='form-group col-md-12 mb-3'),
                css_class='row'
            )

        )

    def clean(self):
        cleaned_data = super().clean()
        loan_amount = cleaned_data.get("loan_amount")
        installments_number = cleaned_data.get("installments_number")
        installment_value = cleaned_data.get("installment_value")

        
        
        if loan_amount is not None and installment_value is not None:
            if loan_amount < installment_value:
                self.add_error('loan_amount', 'El valor del préstamo debe ser mayor o igual al valor de la cuota.')

        if installments_number is None:
            self.add_error('installments_number', 'El número de cuotas no puede estar vacío.')

        return cleaned_data