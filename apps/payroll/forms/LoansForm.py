from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from apps.common.models import Contratos

class LoansForm(forms.Form):
    loan_amount = forms.CharField(
        label="Valor del Préstamo",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': True,
            'x-model': 'loanAmount',
            '@input': 'calculateInstallmentValue',
            'x-mask:dynamic': "$money($input, '.', ',', 4)"
        })
    )
    
    installments_number = forms.CharField(
        required=False, 
        label="Cuotas del Préstamo",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'x-model': 'installmentsNumber',
            '@input': 'calculateInstallmentValue',
            'x-mask:dynamic': "$money($input, '.', ',', 0)"
        })
    )

    installment_value = forms.CharField(
        required=True, 
        label="Valor de la Cuota",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'x-model': 'installmentValue',
            'placeholder': '0.0000'
        })
    )

    loan_date = forms.CharField(
        label='Fecha Préstamo',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'id': 'kt_daterangepicker_1'
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
                (idcontrato, f"{(idempleado__papellido or '').strip()} {(idempleado__sapellido or '').strip()} "
                            f"{(idempleado__pnombre or '').strip()} {(idempleado__snombre or '').strip()} - {idcontrato}")
                for idempleado__pnombre, idempleado__snombre, idempleado__papellido, idempleado__sapellido, idcontrato 
                in Contratos.objects.filter(estadocontrato=1, id_empresa=id_empresa)
                .order_by('idempleado__papellido')
                .values_list('idempleado__pnombre', 'idempleado__snombre', 'idempleado__papellido', 'idempleado__sapellido', 'idcontrato')
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
                Column('installments_number', css_class='form-group col-md-4 mb-3'),
                Column('installment_value', css_class='form-group col-md-4 mb-3'),
                css_class='row'
            ),
            Row(
                Column('loan_date', css_class='form-group col-md-12 mb-3'),
                css_class='row'
            )
        )
        
        
    def clean(self):
        cleaned_data = super().clean()
        loan_amount = cleaned_data.get("loan_amount", "0")
        installments_number = cleaned_data.get("installments_number", "0")
        installment_value = cleaned_data.get("installment_value")

        # Convertir loan_amount a entero eliminando comas y espacios
        try:
            loan_amount = int(float(loan_amount.replace(',', '').strip()))
        except ValueError:
            self.add_error('loan_amount', 'Ingrese un valor numérico válido para el préstamo.')
            loan_amount = 0  # Asignar valor predeterminado en caso de error

        # Convertir installments_number a entero asegurando que no sea menor que 1
        try:
            installments_number = int(float(installments_number.replace(',', '').strip()))
            if installments_number < 1:
                self.add_error('installments_number', 'El número de cuotas debe ser mayor a 0.')
        except ValueError:
            self.add_error('installments_number', 'Ingrese un número válido de cuotas.')
            installments_number = 0  # Asignar valor predeterminado en caso de error

        # Validar que loan_amount sea mayor o igual a installment_value
        if installment_value:
            try:
                installment_value = int(float(installment_value.replace(',', '').strip()))
                if loan_amount < installment_value:
                    self.add_error('loan_amount', 'El valor del préstamo debe ser mayor o igual al valor de la cuota.')
            except ValueError:
                self.add_error('installment_value', 'Ingrese un valor numérico válido para la cuota.')

        # Actualizar los valores en cleaned_data antes de retornarlos
        cleaned_data["loan_amount"] = loan_amount
        cleaned_data["installments_number"] = installments_number
        cleaned_data["installment_value"] = installment_value

        return cleaned_data

