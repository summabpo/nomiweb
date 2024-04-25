from django import forms
from apps.companies.models import Tipodocumento ,Cargos, Centrotrabajo,Paises , Tipodenomina , Ciudades , Tipocontrato , ModelosContratos ,Tiposalario , Bancos , Costos ,Subcostos , Entidadessegsocial
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit,HTML


class EmployeeForm(forms.Form):
    identification_type = forms.ChoiceField(choices=[('', '----------')] + [(documento.codigo, documento.documento) for documento in Tipodocumento.objects.all()], label='Tipo de documento de identidad ')
    identification_number = forms.IntegerField(label='Documento de Identidad ')
    expedition_date = forms.DateField(label='Fecha de expedición ')
    expedition_city = forms.ChoiceField(choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.all().order_by('ciudad')], label='Ciudad de expedición ')
    first_name = forms.CharField(label='Primer Nombre ')
    second_name = forms.CharField(label='Segundo Nombre', required=False)
    first_last_name = forms.CharField(label='Primer Apellido ')
    second_last_name = forms.CharField(label='Segundo Apellido', required=False)
    sex = forms.ChoiceField(choices=[('', '----------'), ('masculino', 'Masculino'), ('femenino', 'Femenino')], label='Sexo ')
    height = forms.CharField(label='Estatura (Mts)', required=False)
    marital_status = forms.ChoiceField(choices=[('', '----------'), ('soltero', 'Soltero'), ('casado', 'Casado'), ('viudo', 'Viudo'), ('divorciado', 'Divorciado'), ('unionlibre', 'Unión Libre')], label='Estado Civil ')
    weight = forms.CharField(label='Peso (Kg)', required=False)
    birthdate = forms.DateField(label='Fecha de Nacimiento ')
    education_level = forms.ChoiceField(choices=[('', '----------'), ('primaria', 'Primaria'), ('Bachiller', 'Bachiller'), ('bachillerinc', 'Bachiller Incompleto'), ('tecnico', 'Técnico'), ('tecnologo', 'Tecnólogo'), ('universitario', 'Universitario'), ('universitarioinc', 'Universitario Incompleto'), ('postgrado', 'Postgrado'), ('magister', 'Magíster')], label='Nivel Educativo', required=False)
    birth_city = forms.ChoiceField(choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.all().order_by('ciudad')], label='Ciudad de Nacimiento')
    stratum = forms.ChoiceField(choices=[('', '----------'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6')], label='Estrato', required=False)
    birth_country = forms.ChoiceField(choices=[('', '----------')] + [(country.pais, country.pais) for country in Paises.objects.all()], label='País de Nacimiento')
    military_id = forms.CharField(label='Libreta Militar', required=False)
    blood_group = forms.ChoiceField(choices=[('', '----------'), ('O-', 'O-'), ('O+', 'O+'), ('A-', 'A-'), ('A+', 'A+'), ('B-', 'B-'), ('B+', 'B+'), ('AB-', 'AB-'), ('AB+', 'AB+')], label='Grupo Sanguíneo', required=False)
    profession = forms.ChoiceField(choices=[('', '----------')] + [(profesion.idcargo, profesion.nombrecargo) for profesion in Cargos.objects.all()], label='Profesión', required=False)
    residence_address = forms.CharField(label='Dirección de Residencia *')
    email = forms.EmailField(label='E-mail *')
    residence_city = forms.ChoiceField(choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.all().order_by('ciudad')], label='Ciudad de Residencia')
    cell_phone = forms.CharField(label='Celular')
    residence_country = forms.ChoiceField(choices=[('', '----------')] + [(country.pais, country.pais) for country in Paises.objects.all()], label='País de residencia')
    employee_phone = forms.CharField(label='Teléfono del Empleado', required=False)
    pants_size = forms.ChoiceField(choices=[('', '----------'), ('6', '6'), ('8', '8'), ('10', '10'), ('12', '12'), ('14', '14'), ('16', '16'), ('28', '28'), ('30', '30'), ('32', '32'), ('34', '34'), ('36', '36'), ('38', '38'), ('40', '40')], label='Talla Pantalón')
    shirt_size = forms.ChoiceField(choices=[('', '----------'), ('38', '38'), ('40', '40'), ('42', '42'), ('44', '44'), ('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL')], label='Talla Camisa')
    shoes_size = forms.ChoiceField(choices=[('', '----------'), ('34', '34'), ('35', '35'), ('36', '36'), ('37', '37'), ('38', '38'), ('39', '39'), ('40', '40'), ('41', '41'), ('42', '42'), ('43', '43'), ('44', '44')], label='Talla Zapatos')

    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'container'
        self.helper.layout = Layout(
            Div(
                HTML('<h3>Datos de Identificación</h3>'),
                Div(
                    Div('identification_type', css_class='col'),
                    Div('identification_number', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('expedition_date', css_class='col'),
                    Div('expedition_city', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('first_name', css_class='col'),
                    Div('second_name', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('first_last_name', css_class='col'),
                    Div('second_last_name', css_class='col'),
                    css_class='row'
                ),
                css_class='container'
            ),
            Div(
                HTML('<h3>Datos Personales</h3>'),
                Div(
                    Div('sex', css_class='col'),
                    Div('height', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('marital_status', css_class='col'),
                    Div('weight', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('birthdate', css_class='col'),
                    Div('education_level', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('birth_city', css_class='col'),
                    Div('stratum', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('birth_country', css_class='col'),
                    Div('military_id', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('blood_group', css_class='col'),
                    Div('profession', css_class='col'),
                    css_class='row'
                ),
                css_class='container'
            ),
            Div(
                HTML('<h3>Datos de Contacto</h3>'),
                Div(
                    Div('residence_address', css_class='col'),
                    Div('email', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('residence_city', css_class='col'),
                    Div('cell_phone', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('residence_country', css_class='col'),
                    Div('employee_phone', css_class='col'),
                    css_class='row'
                ),
                css_class='container'
            ),
            Div(
                HTML('<h3>Tallas</h3>'),
                Div(
                    Div('pants_size', css_class='col'),
                    Div('shirt_size', css_class='col'),
                    Div('shoes_size', css_class='col'),
                    css_class='row'
                ),
                css_class='container'
            ),
            Submit('submit', 'Guardar Empleado', css_class='btn btn-primary mt-3'),
        )



# class EmployeeForm(forms.Form):
#     identificationType = forms.ModelChoiceField(
#         label='Tipo de documento de identidad',
#         queryset=Tipodocumento.objects.using("lectaen").all(),
#         required=True,
#         widget=forms.Select(attrs={'class': 'form-control'})
#     )
    
#     identificationNumber = forms.CharField(
#         label='Documento de Identidad',
#         max_length=100,
#         required=True,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     expeditionDate = forms.DateField(
#         label='Fecha de expedición',
#         required=True,
#         widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
#     )
#     expeditionCity = forms.CharField(
#         label='Ciudad de expedición',
#         max_length=100,
#         required=True,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     firstName = forms.CharField(
#         label='Primer Nombre',
#         max_length=100,
#         required=True,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     secondName = forms.CharField(
#         label='Segundo Nombre',
#         max_length=100,
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     firstLastName = forms.CharField(
#         label='Primer Apellido',
#         max_length=100,
#         required=True,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     secondLastName = forms.CharField(
#         label='Segundo Apellido',
#         max_length=100,
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     sex = forms.ChoiceField(
#         label='Sexo',
#         choices=(
#             ('M', 'Masculino'),
#             ('F', 'Femenino'),
#         ),
#         required=True,
#         widget=forms.Select(attrs={'class': 'form-control'})
#     )
#     height = forms.FloatField(
#         label='Estatura (Mts)',
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     maritalStatus = forms.ChoiceField(
#         label='Estado Civil',
#         choices=(
#             ('', 'Seleccione --------------'),
#             ('soltero', 'Soltero'),
#             ('casado', 'Casado'),
#             ('viudo', 'Viudo'),
#             ('divorciado', 'Divorciado'),
#             ('union_libre', 'Union Libre'),
#         ),
#         required=True,
#         widget=forms.Select(attrs={'class': 'form-control'})
#     )
#     weight = forms.FloatField(
#         label='Peso (Kg)',
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     birthDate = forms.DateField(
#         label='Fecha de Nacimiento',
#         required=True,
#         widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
#     )
#     educationLevel = forms.CharField(
#         label='Nivel Educativo',
#         max_length=100,
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     birthCity = forms.CharField(
#         label='Ciudad de Nacimiento',
#         max_length=100,
#         required=True,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     stratum = forms.IntegerField(
#         label='Estrato',
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     birthCountry = forms.CharField(
#         label='País de nacimiento',
#         max_length=100,
#         required=True,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     militaryId = forms.CharField(
#         label='Libreta Militar',
#         max_length=100,
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     bloodGroup = forms.CharField(
#         label='Grupo Sanguíneo',
#         max_length=100,
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     profession = forms.CharField(
#         label='Profesión',
#         max_length=100,
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     residenceAddress = forms.CharField(
#         label='Dirección de Residencia',
#         max_length=200,
#         required=True,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     email = forms.EmailField(
#         label='E-mail',
#         required=True,
#         widget=forms.EmailInput(attrs={'class': 'form-control'})
#     )
#     residenceCity = forms.CharField(
#         label='Ciudad de Residencia',
#         max_length=100,
#         required=True,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     phone = forms.CharField(
#         label='Teléfono del Empleado',
#         max_length=20,
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     mobile = forms.CharField(
#         label='Celular',
#         max_length=20,
#         required=True,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     residenceCountry = forms.CharField(
#         label='País de residencia',
#         max_length=100,
#         required=True,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )



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
    # Datos de Contrato
    endDate = forms.DateField(label='Fecha de expedición', widget=forms.DateInput(attrs={'type': 'date'}))  
    payrollType = forms.ModelChoiceField(label='Tipo de Nómina', queryset=Tipodenomina.objects.using("lectaen").all().values_list('tipodenomina', flat=True), required=True)  
    position = forms.ModelChoiceField(label='Cargo', queryset=Cargos.objects.using("lectaen").values_list('nombrecargo', flat=True), required=True)
    workLocation = forms.ChoiceField(choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.all().order_by('ciudad')], label='Lugar de trabajo' , required=True)
    
    
    contractStartDate = forms.DateField(label='Fecha de inicio de contrato', required=True, widget=forms.DateInput(attrs={'type': 'date'}))   
    contractType = forms.ModelChoiceField(label='Tipo de Contrato', queryset=Tipocontrato.objects.none(), to_field_name='idtipocontrato', required=True)  
    contractModel = forms.ModelChoiceField(label='Modelo de Contrato', queryset=ModelosContratos.objects.none(), to_field_name='idmodelo', required=True)    
    # Compensación
    salary = forms.CharField(label='Salario', max_length=100, required=True)   
    salaryType = forms.ModelChoiceField(label='Tipo Salario', queryset=Tiposalario.objects.none(), to_field_name='idtiposalario', required=True) 
    salaryMode = forms.ChoiceField(label='Modalidad Salario', choices=ModalidadSalario, required=True)
    livingPlace = forms.BooleanField(label='Vive en el lugar de trabajo', required=True)
    paymentMethod = forms.ChoiceField(label='Forma de pago', choices=FormaPago, required=True)
    bankAccount = forms.ModelChoiceField(label='Banco de la Cuenta', queryset=Bancos.objects.none(), to_field_name='nombanco', required=True)
    
    # Información de Cuenta
    accountType = forms.ChoiceField(label='Tipo de Cuenta', choices=TipoCcuenta, required=True)                                     
    payrollAccount = forms.CharField(label='Cuenta de Nómina', max_length=100, required=True)             
    costCenter = forms.ModelChoiceField(label='Centro de Costos', queryset=Costos.objects.none(), to_field_name='idcosto', required=True)
    subCostCenter = forms.ModelChoiceField(label='Sub centro de Costos', queryset=Subcostos.objects.none(), to_field_name='idsubcosto', required=True)
    
    # Seguridad Social 
    eps = forms.ModelChoiceField(label='Eps', queryset=Entidadessegsocial.objects.none(), to_field_name='entidad', required=True)  
    pensionFund = forms.ModelChoiceField(label='Pension', queryset=Entidadessegsocial.objects.none(), to_field_name='entidad', required=True) 
    CesanFund = forms.ModelChoiceField(label='Fondo Cesantias', queryset=Entidadessegsocial.objects.none(), to_field_name='entidad', required=True) 
    arlWorkCenter = forms.ModelChoiceField(label='Centro de Trabajo ARL', queryset=Centrotrabajo.objects.none(), to_field_name='centrotrabajo', required=True)
    workPlace = forms.ModelChoiceField(label='Sede de Trabajo', queryset=Centrotrabajo.objects.none(), to_field_name='centrotrabajo', required=True)  
    
    # Información Adicional
    contributorType = forms.CharField(label='Documento de Identidad', max_length=100, required=True)
    contributorSubtype = forms.CharField(label='Documento de Identidad', max_length=100, required=True)      
    pensioner = forms.CharField(label='Documento de Identidad', max_length=100, required=True)
    
    
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
                Div('CesanFund', css_class='col'),
                Div('arlWorkCenter', css_class='col'),
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
        
        
        
