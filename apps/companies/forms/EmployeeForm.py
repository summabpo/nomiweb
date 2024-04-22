from django import forms
from apps.companies.models import Tipodocumento ,Cargos, Centrotrabajo,Paises , Tipodenomina , Ciudades , Tipocontrato , ModelosContratos ,Tiposalario , Bancos , Costos ,Subcostos , Entidadessegsocial
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit,HTML


class EmployeeForm(forms.Form):
    identificationType = forms.ModelChoiceField(
        label='Tipo de documento de identidad',
        queryset=Tipodocumento.objects.using("lectaen").all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    identificationNumber = forms.CharField(
        label='Documento de Identidad',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    expeditionDate = forms.DateField(
        label='Fecha de expedición',
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    expeditionCity = forms.CharField(
        label='Ciudad de expedición',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    firstName = forms.CharField(
        label='Primer Nombre',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    secondName = forms.CharField(
        label='Segundo Nombre',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    firstLastName = forms.CharField(
        label='Primer Apellido',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    secondLastName = forms.CharField(
        label='Segundo Apellido',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    sex = forms.ChoiceField(
        label='Sexo',
        choices=(
            ('M', 'Masculino'),
            ('F', 'Femenino'),
        ),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    height = forms.FloatField(
        label='Estatura (Mts)',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    maritalStatus = forms.ChoiceField(
        label='Estado Civil',
        choices=(
            ('', 'Seleccione --------------'),
            ('soltero', 'Soltero'),
            ('casado', 'Casado'),
            ('viudo', 'Viudo'),
            ('divorciado', 'Divorciado'),
            ('union_libre', 'Union Libre'),
        ),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    weight = forms.FloatField(
        label='Peso (Kg)',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    birthDate = forms.DateField(
        label='Fecha de Nacimiento',
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    educationLevel = forms.CharField(
        label='Nivel Educativo',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    birthCity = forms.CharField(
        label='Ciudad de Nacimiento',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    stratum = forms.IntegerField(
        label='Estrato',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    birthCountry = forms.CharField(
        label='País de nacimiento',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    militaryId = forms.CharField(
        label='Libreta Militar',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    bloodGroup = forms.CharField(
        label='Grupo Sanguíneo',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    profession = forms.CharField(
        label='Profesión',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    residenceAddress = forms.CharField(
        label='Dirección de Residencia',
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='E-mail',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    residenceCity = forms.CharField(
        label='Ciudad de Residencia',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        label='Teléfono del Empleado',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    mobile = forms.CharField(
        label='Celular',
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    residenceCountry = forms.CharField(
        label='País de residencia',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )



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
class ContractForm(forms.Form):
    endDate = forms.DateField(
        label='Fecha de expedición',
        widget=forms.DateInput(attrs={'type': 'date'})
    )  
    
    payrollType  = forms.ModelChoiceField( #! el tipo viene de una tabla 
        label='Tipo de Nómina',
        queryset=Tipodenomina.objects.using("lectaen").all(),
        to_field_name='tipodenomina', 
        required=True,
        
    )   
    
    position =  forms.ModelChoiceField( #! viene de una tabla 
        label='Cargo',
        queryset=Cargos.objects.using("lectaen").values_list('nombrecargo', flat=True),
        to_field_name='nombrecargo', 
        required=True,
        
    )   
    
    workLocation = forms.ModelChoiceField(
        label='Lugar de trabajo',
        queryset=Ciudades.objects.all(),  
        to_field_name='idciudad', 
        required=True,
        
    ) 
    
    contractStartDate  = forms.DateField(
        label='Fecha de expedición',
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )   
                    
    contractType  =  forms.ModelChoiceField( #! viene de una tabla 
        label='Tipo de Contrato',
        queryset=Tipocontrato.objects.using("lectaen").all(),
        to_field_name='idtipocontrato', 
        required=True,
        
    )  
    
    
    contractModel = forms.ModelChoiceField( #! viene de una tabla 
        label='Modelo de Contrato',
        queryset=ModelosContratos.objects.using("lectaen").all(),
        to_field_name='idmodelo', 
        required=True,
        
    )   
    
    # #* Compensación
    salary  =  forms.CharField(
        label='Salario *',
        max_length=100,
        required=True,
        
    )   
    salaryType   =  forms.ModelChoiceField( 
        label='Tipo Salario *',
        queryset=Tiposalario.objects.using("lectaen").all(), 
        to_field_name='idtiposalario', 
        required=True,
        
    ) 
    
    salaryMode = forms.ChoiceField( 
        label='Modalidad Salario',
        choices=ModalidadSalario,
        required=True,
        
    ) 
    
    livingPlace  = forms.BooleanField(  
        label='Vive en el lugar de trabajo',
        required=True,
        
    )  
    
    paymentMethod = forms.ChoiceField( #! viene de una tabla
        label='Forma de pago',
        choices=FormaPago,
        required=True,
        
    )       
    
    bankAccount = forms.ModelChoiceField( #! viene de una tabla
        label='Banco de la Cuenta',
        queryset=Bancos.objects.using("lectaen").all(), 
        to_field_name='nombanco', 
        required=True,
        
    )    
    #* 
    
    
    accountType = forms.ChoiceField( 
        label='Tipo de Cuenta',
        choices=TipoCcuenta,
        required=True,
        
    )                                     
    payrollAccount = forms.CharField( 
        label='Cuenta de Nómina',
        max_length=100,
        required=True,
        
    )             
    costCenter  = forms.ModelChoiceField( 
        label='Centro de Costos',
        queryset=Costos.objects.using("lectaen").all(), 
        to_field_name='idcosto', 
        required=True,
        
    )                   
    subCostCenter = forms.ModelChoiceField( 
        label='Sub centro de Costos',
        queryset=Subcostos.objects.using("lectaen").all(), 
        to_field_name='idsubcosto', 
        required=True,
        
    ) 
    
    # #* seguridad social 
    eps = forms.ModelChoiceField( 
        label='Eps',
        queryset=Entidadessegsocial.objects.using("lectaen").filter(tipoentidad='EPS'), 
        to_field_name='entidad', 
        
        required=True,
        
    )  
    
    pensionFund = forms.ModelChoiceField( 
        label='Pension',
        queryset=Entidadessegsocial.objects.using("lectaen").filter(tipoentidad='AFP'), 
        to_field_name='entidad', 
        required=True,
        
    ) 
    
    CesanFund = forms.ModelChoiceField( 
        label='Fondo Cesantias',
        queryset=Entidadessegsocial.objects.using("lectaen").filter(tipoentidad='AFP'), 
        to_field_name='entidad', 
        required=True,
        
    ) 
    
    arlWorkCenter = forms.ModelChoiceField( #! viene de una tabla
        label='Centro de Trabajo ARL',
        queryset=Centrotrabajo.objects.using("lectaen").all(), 
        to_field_name='centrotrabajo', 
        required=True,
        
    )  
    
    workPlace = forms.CharField( #! viene de una tabla
        label='Documento de Identidad',
        max_length=100,
        required=True,
        
    )  
    # #arlRate                      #todo : se requiere calcular o traer y  visualizar 
    # #compensationFund                      #todo : se rerequiere visualizar basado en la ciudad 
    # contributorType    = forms.CharField( #! viene de una tabla
    #     label='Documento de Identidad',
    #     max_length=100,
    #     required=True,
        
    # )                    #*
    # contributorSubtype  = forms.CharField( #! viene de una tabla
    #     label='Documento de Identidad',
    #     max_length=100,
    #     required=True,
        
    # )      
    
    
    # pensioner = forms.CharField( #! chekbox
    #     label='Documento de Identidad',
    #     max_length=100,
    #     required=True,
        
    # )      
    
    
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
                Submit('submit', 'Submit', css_class='btn btn-primary'),
                css_class='row justify-content-center'
            )
        )
        
        
        
