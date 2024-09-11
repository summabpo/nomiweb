from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


class LoansForm(forms.Form):
    contract_id = forms.IntegerField(label='ID Contrato', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    employee_id = forms.IntegerField(label='ID Empleado', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    loan_amount = forms.IntegerField(label='Valor Prestamo', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    loan_date = forms.DateField(label='Fecha Prestamo', required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date' }))
    installments = forms.IntegerField(label='Cuotas Prestamo', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    installment_value = forms.IntegerField(label='Valor Cuota', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    loan_balance = forms.IntegerField(label='Saldo Prestamo', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    installments_paid = forms.IntegerField(label='Cuotas Pagadas', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    employee_name = forms.CharField(label='Empleado', max_length=40, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    loan_status = forms.BooleanField(label='Estado Prestamo', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    payment_method = forms.IntegerField(label='Forma de Pago', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    payment_day = forms.IntegerField(label='Día de Pago', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_loans'
        self.helper.enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Row(
                Column('employee_id', css_class='form-group mb-0'),
                Column('contract_id', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                Column('loan_amount', css_class='form-group mb-0'),
                Column('loan_date', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                Column('installments', css_class='form-group mb-0'),
                Column('installment_value', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                Column('loan_balance', css_class='form-group mb-0'),
                Column('installments_paid', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                Column('employee_name', css_class='form-group mb-0'),
                Column('loan_status', css_class='form-check form-check-custom form-check-danger form-check-solid d-flex align-items-center'),
                css_class='row'
            ),
            Row(
                Column('payment_method', css_class='form-group mb-0'),
                Column('payment_day', css_class='form-group mb-0'),
                css_class='row'
            ),
        )
    