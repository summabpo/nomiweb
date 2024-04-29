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
    # Datos de Contrato
    endDate = forms.DateField(label='Fecha de Terminación', widget=forms.DateInput(attrs={'type': 'date'}), required=False)  
    payrollType = forms.ChoiceField(choices=[('', '----------')] + [(nomina.tipodenomina, nomina.tipodenomina) for nomina in Tipodenomina.objects.all()], label='Tipo de Nómina', required=False)
    position = forms.ChoiceField(choices=[('', '----------')] + [(cargo.nombrecargo, cargo.nombrecargo) for cargo in Cargos.objects.all().order_by('nombrecargo')], label='Cargo', required=False , widget=forms.Select(attrs={'data-control': 'select2'}))
    workLocation = forms.ChoiceField(choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.all().order_by('ciudad')], label='Lugar de trabajo' , required=False ,widget=forms.Select(attrs={'data-control': 'select2'}))
    contractStartDate = forms.DateField(label='Fecha de inicio de contrato', required=False, widget=forms.DateInput(attrs={'type': 'date'}))   
    contractType = forms.ChoiceField(choices=[('', '----------')] + [(contrato.idtipocontrato, contrato.tipocontrato) for contrato in Tipocontrato.objects.all()], label='Tipo de Contrato',required=False)
    contractModel = forms.ChoiceField(choices=[('', '----------')] + [(modelo.tipocontrato, modelo.nombremodelo) for modelo in ModelosContratos.objects.all()], label='Modelo de Contrato',required=False)
    # Compensación
    salary = forms.CharField(label='Salario', max_length=100, required=False)   
    salaryType = forms.ChoiceField(choices=[('', '----------')] + [(salario.idtiposalario, salario.tiposalario) for salario in Tiposalario.objects.all()], label='Tipo Salario', required=False ) 
    salaryMode = forms.ChoiceField(label='Modalidad Salario', choices=ModalidadSalario, required=False)
    livingPlace = forms.BooleanField(label='Vive en el lugar de trabajo', required=False)
    paymentMethod = forms.ChoiceField(label='Forma de pago', choices=FormaPago, required=False)
    bankAccount = forms.ChoiceField(choices=[('', '----------')] + [(banco.nombanco, banco.nombanco) for banco in Bancos.objects.all().order_by('nombanco')], label='Banco de la Cuenta', required=False, widget=forms.Select(attrs={'data-control': 'select2'}) )
    # Información de Cuenta
    accountType = forms.ChoiceField(label='Tipo de Cuenta', choices=TipoCcuenta, required=False)                                     
    payrollAccount = forms.CharField(label='Cuenta de Nómina', max_length=100, required=False)    
    costCenter = forms.ChoiceField(choices=[('', '----------')] + [(costo.idcosto, costo.nomcosto) for costo in Costos.objects.all()], label='Centro de Costos', required=False)
    subCostCenter = forms.ChoiceField(choices=[('', '----------')] + [(subcosto.idsubcosto, subcosto.nomsubcosto) for subcosto in Subcostos.objects.all()], label='Sub centro de Costos', required=False)
    # Seguridad Social 
    eps = forms.ChoiceField(choices=[('', '----------')] + [(entidad.codigo, entidad.entidad) for entidad in Entidadessegsocial.objects.using("lectaen").filter(tipoentidad='EPS').order_by('entidad')], label='Eps', required=False , widget=forms.Select(attrs={'data-control': 'select2'})) 
    pensionFund = forms.ChoiceField(choices=[('', '----------')] + [(entidad.codigo, entidad.entidad) for entidad in Entidadessegsocial.objects.using("lectaen").filter(tipoentidad='AFP').order_by('entidad')], label='Pension', required=False , widget=forms.Select(attrs={'data-control': 'select2'})) 
    CesanFund = forms.ChoiceField(choices=[('', '----------')] + [(entidad.codigo, entidad.entidad) for entidad in Entidadessegsocial.objects.using("lectaen").filter(tipoentidad='CCF').order_by('entidad')], label='Fondo Cesantias', required=False , widget=forms.Select(attrs={'data-control': 'select2'})) 
    workPlace = forms.ChoiceField(choices=[('', '----------')] + [(sede.idsede, sede.nombresede) for sede in Sedes.objects.using("lectaen").all()], label='Sede de Trabajo', required=False)
    arlWorkCenter  = forms.ChoiceField(choices=[('', '----------')] + [(centro.centrotrabajo, centro.nombrecentrotrabajo) for centro in Centrotrabajo.objects.using("lectaen").all()], label='Centro de Trabajo ARL', required=False)
    # Información Adicional
    # contributorType = forms.CharField(label='Documento de Identidad', max_length=100, required=False)
    # contributorSubtype = forms.CharField(label='Documento de Identidad', max_length=100, required=False)      
    # pensioner = forms.CharField(label='Documento de Identidad', max_length=100, required=False)
    
    
    def clean(self):
        cleaned_data = super().clean()
        payrollAccount = cleaned_data.get('payrollAccount')
        if payrollAccount:
            try:
                float(payrollAccount)
            except ValueError:
                self.add_error('payrollAccount', 'El salario debe ser un número válido (entero o flotante).')
        return cleaned_data
    
    
    
    def __init__(self, *args, **kwargs):
        super(ContractForm, self).__init__(*args, **kwargs)
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
        
        
        
