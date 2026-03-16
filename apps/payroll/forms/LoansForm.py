from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from apps.common.models import Contratos
from django.urls import reverse

class LoansForm(forms.Form):
    loan_amount = forms.CharField(
        label="Valor del Préstamo",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': True,
            'x-mask:dynamic': "$money($input, '.', ',', 4)"
        })
    )
    
    installments_number = forms.CharField(
        required=False, 
        label="Cuotas del Préstamo",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'x-mask:dynamic': "$money($input, '.', ',', 0)"
        })
    )

    installment_value = forms.CharField(
        required=True, 
        label="Valor de la Cuota",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'x-mask:dynamic': "$money($input, '.', ',', 0)"
        })
    )

    loan_date = forms.CharField(
        label='Fecha Préstamo',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'id': 'kt_daterangepicker_1'
        })
    )

    state = forms.ChoiceField(
        required=False,
        label="estado prestamo",
        choices=[
            (1, 'Activo'),
            (0, 'Pagado'),
        ],
        widget=forms.Select(attrs={
            'data-choices': '',
            'data-control': 'select2',
            'data-hide-search': 'true',
            'data-choices-sorting-false': ''
        })
    )

    def __init__(self, *args, **kwargs):
        id_empresa = kwargs.pop('id_empresa', None)  
        modo = kwargs.pop('modo', 0)  
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_loans'
        self.helper.enctype = 'multipart/form-data'
        

        


        self.helper.attrs.update({
            'up-target': '#modal-content',
            'up-mode': 'replace',
            'up-layer': 'current',  # Clave para resolver el error
            'up-submit': reverse('payroll:employee_loans_modal_add'),
            'up-accept-location': reverse('payroll:employee_loans_modal_add'),
            'up-on-accepted': 'up.modal.close()',  # Cierra el modal al aceptar
        })

        self.fields['contract'] = forms.ChoiceField(
            choices = [('', '----------')] + [
                (
                    idcontrato,
                    f"{str(idempleado__papellido or '').strip()} "
                    f"{str(idempleado__sapellido or '').strip()} "
                    f"{str(idempleado__pnombre or '').strip()} "
                    f"{str(idempleado__snombre or '').strip()} "
                    f"- {idcontrato} - {str(idempleado__docidentidad or '').strip()}"
                )
                for idempleado__docidentidad, idempleado__pnombre, idempleado__snombre,
                    idempleado__papellido, idempleado__sapellido, idcontrato
                in Contratos.objects.filter(estadocontrato=1, id_empresa=id_empresa)
                .order_by('idempleado__papellido')
                .values_list(
                    'idempleado__docidentidad',
                    'idempleado__pnombre',
                    'idempleado__snombre',
                    'idempleado__papellido',
                    'idempleado__sapellido',
                    'idcontrato'
                )
            ],
            label="Contrato",
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-placeholder': 'Seleccione un Contrato',
                'class': 'form-select'
                
            })
        )


        if modo == 1: 
            self.fields['contract'].disabled = True
            self.fields['loan_amount'].disabled = True
            self.fields['loan_date'].disabled = True
            for field in self.fields.values():
                field.required = False


        layout_fields = [

            ##Información General ( va bloqueada )
            Row(
                Column('contract', css_class='form-group col-md-12 mb-3'),
                css_class='row'
            ),
            Row(
                Column('loan_amount', css_class='form-group col-md-6 mb-3'),
                Column('installment_value', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),

        ]


        if modo == 1 :
            layout_fields.append(
                ## Información Bancaria
                Row(
                    Column('loan_date', css_class='form-group col-md-6 mb-'),
                    Column('state', css_class='form-group col-md-6 mb-'),
                    css_class='row'
                )
            )

        else : 
            layout_fields.append(
                ## Información Bancaria
                Row(
                    Column('loan_date', css_class='form-group col-md-12 mb-3'),
                    css_class='row'
                )
            )



        self.helper.layout = Layout(*layout_fields)
        
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

