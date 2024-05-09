import re
# Django
from django import forms
from apps.companies.models import Tipodocumento ,Cargos, Centrotrabajo,Paises , Tipodenomina , Ciudades , Tipocontrato , ModelosContratos ,Tiposalario , Bancos , Costos ,Subcostos , Entidadessegsocial,Sedes
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit,HTML



ModalidadSalario = (
    ('', '----------'),
    ('1', 'Variable'),
    ('2', 'Fijo'),
    ('3', 'Mixto'),
)

FormaPago = (
    ('', '----------'),
    ('1', 'Abono a cuenta'),
    ('2', 'Cheque'),
    ('3', 'Efectivo'),
)


TipoCcuenta = [
    ('', '----------'),
    ('ahorros', 'Ahorros'),
    ('corriente', 'Corriente'),
]

#forms.ChoiceField(choices=[('', '----------')] + [(documento.codigo, documento.documento) for documento in Tipodocumento.objects.all()], label='Tipo de documento de identidad ')


class ContractForm(forms.Form):
#     # Datos de Contrato
#     endDate = forms.DateField(label='Fecha de Terminación', widget=forms.DateInput(attrs={'type': 'date'}), required=False)  
#     payrollType = forms.ChoiceField(choices=[('', '----------')] + [(nomina.tipodenomina, nomina.tipodenomina) for nomina in Tipodenomina.objects.all()], label='Tipo de Nómina')
#     position = forms.ChoiceField(choices=[('', '----------')] + [(cargo.nombrecargo, cargo.nombrecargo) for cargo in Cargos.objects.all().order_by('nombrecargo')], label='Cargo', required=True , widget=forms.Select(attrs={'data-control': 'select2'}))
#     workLocation = forms.ChoiceField(choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.all().order_by('ciudad')], label='Lugar de trabajo' , required=True ,widget=forms.Select(attrs={'data-control': 'select2'}))
#     contractStartDate = forms.DateField(label='Fecha de inicio de contrato', required=True, widget=forms.DateInput(attrs={'type': 'date'}))   
#     contractType = forms.ChoiceField(choices=[('', '----------')] + [(contrato.idtipocontrato, contrato.tipocontrato) for contrato in Tipocontrato.objects.all()], label='Tipo de Contrato',required=True)
#     contractModel = forms.ChoiceField(choices=[('', '----------')] + [(modelo.idmodelo, modelo.nombremodelo) for modelo in ModelosContratos.objects.all()], label='Modelo de Contrato',required=True)
#     # Compensación
#     salary = forms.CharField(label='Salario', max_length=100, required=True)   
#     salaryType = forms.ChoiceField(choices=[('', '----------')] + [(salario.idtiposalario, salario.tiposalario) for salario in Tiposalario.objects.all()], label='Tipo Salario', required=True ) 
#     salaryMode = forms.ChoiceField(label='Modalidad Salario', choices=ModalidadSalario, required=True)
#     livingPlace = forms.BooleanField(label='Vive en el lugar de trabajo', required=False)
#     paymentMethod = forms.ChoiceField(label='Forma de pago', choices=FormaPago, required=True)
#     bankAccount = forms.ChoiceField(choices=[('', '----------')] + [(banco.nombanco, banco.nombanco) for banco in Bancos.objects.all().order_by('nombanco')], label='Banco de la Cuenta', required=True, widget=forms.Select(attrs={'data-control': 'select2'}) )
#     # Información de Cuenta
#     accountType = forms.ChoiceField(label='Tipo de Cuenta', choices=TipoCcuenta, required=True)                                     
#     payrollAccount = forms.CharField(label='Cuenta de Nómina', max_length=100, required=True)    
#     costCenter = forms.ChoiceField(choices=[('', '----------')] + [(costo.idcosto, costo.nomcosto) for costo in Costos.objects.all()], label='Centro de Costos', required=True)
#     subCostCenter = forms.ChoiceField(choices=[('', '----------')] + [(subcosto.idsubcosto, subcosto.nomsubcosto) for subcosto in Subcostos.objects.all()], label='Sub centro de Costos', required=True)
#     # Seguridad Social 
#     eps = forms.ChoiceField(choices=[('', '----------')] + [(entidad.codigo, entidad.entidad) for entidad in Entidadessegsocial.objects.filter(tipoentidad='EPS').order_by('entidad')], label='Eps', required=True , widget=forms.Select(attrs={'data-control': 'select2'})) 
#     pensionFund = forms.ChoiceField(choices=[('', '----------')] + [(entidad.codigo, entidad.entidad) for entidad in Entidadessegsocial.objects.filter(tipoentidad='AFP').order_by('entidad')], label='Pension', required=True , widget=forms.Select(attrs={'data-control': 'select2'})) 
#     CesanFund = forms.ChoiceField(choices=[('', '----------')] + [(entidad.codigo, entidad.entidad) for entidad in Entidadessegsocial.objects.filter(tipoentidad='CCF').order_by('entidad')], label='Fondo Cesantias', required=True , widget=forms.Select(attrs={'data-control': 'select2'})) 
#     workPlace = forms.ChoiceField(choices=[('', '----------')] + [(sede.idsede, sede.nombresede) for sede in Sedes.objects.all()], label='Sede de Trabajo', required=True)
#     arlWorkCenter  = forms.ChoiceField(choices=[('', '----------')] + [(centro.centrotrabajo, centro.nombrecentrotrabajo) for centro in Centrotrabajo.objects.all()], label='Centro de Trabajo ARL', required=True)
#     # Información Adicional
    # contributorType = forms.CharField(label='Documento de Identidad', max_length=100, required=True)
    # contributorSubtype = forms.CharField(label='Documento de Identidad', max_length=100, required=True)      
    # pensioner = forms.CharField(label='Documento de Identidad', max_length=100, required=True)
    
    
    def clean(self):
        cleaned_data = super().clean()
        payrollAccount = cleaned_data.get('payrollAccount')
        if payrollAccount:
            try:
                float(payrollAccount)
            except ValueError:
                self.add_error('payrollAccount', 'El salario debe ser un número válido (entero o flotante).')
        return cleaned_data
    
    def set_premium_fields(self, premium=False):
        fields_to_adjust = [
            'endDate', 'payrollType', 'position', 'workLocation', 'contractStartDate',
            'contractType', 'contractModel', 'salary', 'salaryType', 'salaryMode',
            'eps', 'pensionFund', 'CesanFund', 'arlWorkCenter', 'workPlace'
        ]

        for field_name in fields_to_adjust:
            field = self.fields.get(field_name)
            if field:
                field.disabled = not premium
                field.required = premium
        


    def __init__(self, *args, **kwargs):
        super(ContractForm, self).__init__(*args, **kwargs)
        
        
        self.fields['endDate'] = forms.DateField(label='Fecha de Terminación', widget=forms.DateInput(attrs={'type': 'date'}), required=False)
        self.fields['payrollType'] = forms.ChoiceField(choices=[('', '----------')] + [(nomina.tipodenomina, nomina.tipodenomina) for nomina in Tipodenomina.objects.all()], label='Tipo de Nómina')
        self.fields['position'] = forms.ChoiceField(choices=[('', '----------')] + [(cargo.nombrecargo, cargo.nombrecargo) for cargo in Cargos.objects.all().order_by('nombrecargo')], label='Cargo', required=True , widget=forms.Select(attrs={'data-control': 'select2'}))
        self.fields['workLocation'] = forms.ChoiceField(choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.all().order_by('ciudad')], label='Lugar de trabajo' , required=True ,widget=forms.Select(attrs={'data-control': 'select2'}))
        self.fields['contractStartDate'] = forms.DateField(label='Fecha de inicio de contrato', required=True, widget=forms.DateInput(attrs={'type': 'date'}))   
        self.fields['contractType'] = forms.ChoiceField(choices=[('', '----------')] + [(contrato.idtipocontrato, contrato.tipocontrato) for contrato in Tipocontrato.objects.all()], label='Tipo de Contrato',required=True)
        self.fields['contractModel'] = forms.ChoiceField(choices=[('', '----------')] + [(modelo.idmodelo, modelo.nombremodelo) for modelo in ModelosContratos.objects.all()], label='Modelo de Contrato',required=True)
        self.fields['salary'] = forms.CharField(label='Salario', max_length=100, required=True)   
        self.fields['salaryType'] = forms.ChoiceField(choices=[('', '----------')] + [(salario.idtiposalario, salario.tiposalario) for salario in Tiposalario.objects.all()], label='Tipo Salario', required=True ) 
        self.fields['salaryMode'] = forms.ChoiceField(label='Modalidad Salario', choices=ModalidadSalario, required=True)
        self.fields['livingPlace'] = forms.BooleanField(label='Vive en el lugar de trabajo', required=False)
        self.fields['paymentMethod'] = forms.ChoiceField(label='Forma de pago', choices=FormaPago, required=True)
        self.fields['bankAccount'] = forms.ChoiceField(choices=[('', '----------')] + [(banco.nombanco, banco.nombanco) for banco in Bancos.objects.all().order_by('nombanco')], label='Banco de la Cuenta', required=True, widget=forms.Select(attrs={'data-control': 'select2'}) )
        self.fields['accountType'] = forms.ChoiceField(label='Tipo de Cuenta', choices=TipoCcuenta, required=True)                                     
        self.fields['payrollAccount'] = forms.CharField(label='Cuenta de Nómina', max_length=100, required=True)    
        self.fields['costCenter'] = forms.ChoiceField(choices=[('', '----------')] + [(costo.idcosto, costo.nomcosto) for costo in Costos.objects.all()], label='Centro de Costos', required=True)
        self.fields['subCostCenter'] = forms.ChoiceField(choices=[('', '----------')] + [(subcosto.idsubcosto, subcosto.nomsubcosto) for subcosto in Subcostos.objects.all()], label='Sub centro de Costos', required=True)
        self.fields['eps'] = forms.ChoiceField(choices=[('', '----------')] + [(entidad.codigo, entidad.entidad) for entidad in Entidadessegsocial.objects.filter(tipoentidad='EPS').order_by('entidad')], label='Eps', required=True , widget=forms.Select(attrs={'data-control': 'select2'})) 
        self.fields['pensionFund'] = forms.ChoiceField(choices=[('', '----------')] + [(entidad.codigo, entidad.entidad) for entidad in Entidadessegsocial.objects.filter(tipoentidad='AFP').order_by('entidad')], label='Pension', required=True , widget=forms.Select(attrs={'data-control': 'select2'})) 
        self.fields['CesanFund'] = forms.ChoiceField(choices=[('', '----------')] + [(entidad.codigo, entidad.entidad) for entidad in Entidadessegsocial.objects.filter(tipoentidad='AFP').order_by('entidad')], label='Fondo Cesantias', required=True , widget=forms.Select(attrs={'data-control': 'select2'})) 
        self.fields['workPlace'] = forms.ChoiceField(choices=[('', '----------')] + [(sede.idsede, sede.nombresede) for sede in Sedes.objects.all()], label='Sede de Trabajo', required=True)
        self.fields['arlWorkCenter'] = forms.ChoiceField(choices=[('', '----------')] + [(centro.centrotrabajo, centro.nombrecentrotrabajo) for centro in Centrotrabajo.objects.all()], label='Centro de Trabajo ARL', required=True)
        
        
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'container'
        
        self.helper.layout = Layout(
            HTML('<h3>Contrato</h3>'),
            Div(
                Div('endDate', css_class='col' ),
                Div('payrollType', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('position', css_class='col'),
                Div('workLocation', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('contractStartDate', css_class='col'),
                Div('contractType', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('contractModel', css_class='col'),
                css_class='row'
            ),

            HTML('<h3>Compensación</h3>'),
            # compenasion 
            Div(
                Div('salary', css_class='col'),
                Div('salaryType', css_class='col'),
                css_class='row'
            ),
            
            Div(
                Div('salaryMode', css_class='col'),
                Div('livingPlace', css_class='col'),
                css_class='row'
            ),
            
            Div(
                Div('paymentMethod', css_class='col'),
                Div('bankAccount', css_class='col'),
                css_class='row'
            ),
            
            Div(
                Div('accountType', css_class='col'),
                Div('payrollAccount', css_class='col'),
                css_class='row'
            ),
            
            Div(
                Div('costCenter', css_class='col'),
                Div('subCostCenter', css_class='col'),
                css_class='row'
            ),
            
            HTML('<h3>Seguridad Social</h3>'),
            
            Div(
                Div('eps', css_class='col'),
                Div('pensionFund', css_class='col'),
                css_class='row'
            ),
            
            
            Div(
                Div('CesanFund', css_class='col'),
                Div('arlWorkCenter', css_class='col'),
                css_class='row'
            ),
            
            Div(
                Div('workPlace', css_class='col'),
                #Div('arlWorkCenter', css_class='col'),
                css_class='row'
            ),
            
            Div(
                Submit('submit', 'Guardar Contrato', css_class='btn btn-primary'),
                css_class='row justify-content-center'
            )
        )
        
        
        