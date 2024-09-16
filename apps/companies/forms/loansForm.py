from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column ,HTML
from apps.companies.models  import Contratos,Entidadessegsocial ,Diagnosticosenfermedades

class LoansForm(forms.Form):
    
    loan_amount = forms.IntegerField(label='Valor Prestamo', required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    # loan_date = forms.DateField(label='Fecha Prestamo', required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date' }))
    # installments = forms.IntegerField(label='Cuotas Prestamo', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    installment_value = forms.IntegerField(label='Valor Cuota', required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    # loan_balance = forms.IntegerField(label='Saldo Prestamo', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    # installments_paid = forms.IntegerField(label='Cuotas Pagadas', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    # employee_name = forms.CharField(label='Empleado', max_length=40, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    loan_status = forms.BooleanField(label='Estado Prestamo', required=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    # payment_method = forms.IntegerField(label='Forma de Pago', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    # payment_day = forms.IntegerField(label='Día de Pago', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    
    
    loan_date = forms.CharField(
        label='Fecha Prestamo',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'id': 'kt_daterangepicker_1'
        })
    )
    
    def __init__(self, *args, **kwargs):
        dropdown_parent = kwargs.pop('dropdown_parent', '#kt_modal_1')
        select2_ids = kwargs.pop('select2_ids', {})
        super().__init__(*args, **kwargs)
        
        self.fields['contract'] = forms.ChoiceField(
            choices=[('', '----------')] + [
                (item['idcontrato'], f"{item['idempleado__papellido']} {item['idempleado__sapellido']} {item['idempleado__pnombre']} {item['idempleado__snombre']} - {item['idcontrato']}")
                for item in Contratos.objects.filter(estadocontrato=1)
                .order_by('idempleado__papellido')  # Aplica el orden antes de hacer el slice
                .values('idempleado__pnombre', 'idempleado__snombre', 'idempleado__papellido', 'idempleado__sapellido', 'idcontrato')
            ],
            label="Contrato" , 
        )
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_loans'
        self.helper.enctype = 'multipart/form-data'
        
        
        for field_name in ['entity', 'contract', 'diagnosis_code']:
            field_id = select2_ids.get(field_name, f'{field_name}_{dropdown_parent.strip("#")}')
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'data-control': 'select2',
                    'data-dropdown-parent': dropdown_parent,
                    'class': 'form-select',
                    'id': field_id,
                })
        
        
        
        self.helper.layout = Layout(
            Row(
                Column('contract', css_class='form-group col-md-12 mb-3'),
                css_class='row'
            ),
            Row(
                Column('loan_amount', css_class='form-group col-md-6 mb-3'),
                Column('loan_date', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('installment_value', css_class='form-group col-md-4 mb-3'),
                Column('loan_status', css_class='form-check form-check-custom form-check-danger form-check-solid d-flex align-items-end col-md-4 mb-3'),
                HTML('<button id="loan_status_btn" type="button" class="btn btn-bg-success" disabled> Activo </button>'),
                css_class='row'
            ),

        )
    