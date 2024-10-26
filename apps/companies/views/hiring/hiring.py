from django.shortcuts import render, redirect
from apps.companies.forms.EmployeeForm import EmployeeForm
from django.contrib import messages
from apps.common.models  import Contratosemp,Tipodocumento,Subcostos,ModelosContratos,Sedes,Subtipocotizantes,Costos,Tiposalario,Ciudades,Paises,Empresa,Contratos,Tipocontrato,Cargos,Tipodenomina,Bancos,Centrotrabajo,Entidadessegsocial,Tiposdecotizantes
from apps.companies.forms.EmployeeForm import EmployeeForm
from apps.companies.forms.ContractForm  import ContractForm 
from apps.common.models import User


from django.contrib.auth.hashers import make_password
from apps.components.mail import send_template_email

import random
import string
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required


def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    random_password = ''.join(random.choice(characters) for i in range(length))
    return random_password

@login_required
@role_required('company')
def hiring(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    empleados = {}
    idempleado = 2
    
    if request.method == 'POST':
        # Procesar los datos del formulario 1
        form1 = EmployeeForm(request.POST, prefix='form1')
        if form1.is_valid():
            tipodocumento = Tipodocumento.objects.get(codigo = form1.cleaned_data['identification_type'] )
            ciudad1 = Ciudades.objects.get(idciudad = form1.cleaned_data['birth_city'] )
            Paises1 = Paises.objects.get(idpais = form1.cleaned_data['birth_country'] )
            
            ciudad2 = Ciudades.objects.get(idciudad = form1.cleaned_data['residence_city'] )
            Paises2 = Paises.objects.get(idpais = form1.cleaned_data['residence_country'])
            
            ciudad3 = Ciudades.objects.get(idciudad = form1.cleaned_data['expedition_city'])
            
            empresa = Empresa.objects.get(idempresa = idempresa )
            
            height = form1.cleaned_data['height']
            weight = form1.cleaned_data['weight']
            height = height.replace(',', '.') if ',' in height else height
            weight = weight.replace(',', '.') if ',' in weight else weight
            height = float(height)
            weight = float(weight)

            
            contratosemp_instance = Contratosemp(
                docidentidad = form1.cleaned_data['identification_number'],
                tipodocident = tipodocumento ,

                # Nombres y apellidos
                pnombre = form1.cleaned_data['first_name'],
                snombre = form1.cleaned_data['second_name'],
                papellido = form1.cleaned_data['first_last_name'],
                sapellido = form1.cleaned_data['second_last_name'],


                # Información de contacto
                email = form1.cleaned_data['email'] ,
                telefonoempleado = form1.cleaned_data['employee_phone'],
                celular = form1.cleaned_data['cell_phone'],
                direccionempleado = form1.cleaned_data['residence_address'],

                # Datos personales
                sexo = form1.cleaned_data['sex'], 
                fechanac = form1.cleaned_data['birthdate'],
                ciudadnacimiento = ciudad1, 
                paisnacimiento = Paises1,

                ciudadresidencia = ciudad2, 
                paisresidencia = Paises2,
                estadocivil = form1.cleaned_data['marital_status'] , 

                # Datos académicos y profesionales
                profesion = form1.cleaned_data['profession'] , 
                niveleducativo = form1.cleaned_data['education_level'],

                # Información física
                estatura = height,
                peso = weight,
                gruposanguineo = form1.cleaned_data['blood_group'],

                # Documentación
                fechaexpedicion = form1.cleaned_data['expedition_date'],
                ciudadexpedicion = ciudad3 , 
                
                # Dotaciones
                dotpantalon = form1.cleaned_data['pants_size'],
                dotcamisa = form1.cleaned_data['shirt_size'],
                dotzapatos = form1.cleaned_data['shoes_size'],

                # Otros datos
                estadocontrato = 4 ,
                estrato = form1.cleaned_data['stratum'],
                numlibretamil = form1.cleaned_data['military_id'],
                # Relación con la empresa
                id_empresa = empresa 
            )
            contratosemp_instance.save()
            
            messages.success(request, 'El Empleado ha sido creado')
            return redirect('companies:hiring')
        else:
            for field, errors in form1.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')

        # Procesar los datos del formulario 2
        form2 = ContractForm(request.POST , prefix='form2')
        if form2.is_valid():
            #* data aqui 
            empresa = Empresa.objects.get(idempresa = idempresa )
            cargos = Cargos.objects.get( idcargo = form2.cleaned_data['position'] )
            tipocontrato = Tipocontrato.objects.get(idtipocontrato=form2.cleaned_data['contractType'] )
            tipodenomina =  Tipodenomina.objects.get( idtiponomina = form2.cleaned_data['payrollType'], )
            bancos = Bancos.objects.get( idbanco = form2.cleaned_data['bankAccount'] )
            centrotrabajo = Centrotrabajo.objects.get(centrotrabajo = form2.cleaned_data['arlWorkCenter'] )
            ciudades = Ciudades.objects.get(idciudad =  form2.cleaned_data['workLocation'])
            fondo = Entidadessegsocial.objects.get( identidad = form2.cleaned_data['CesanFund'] )
            empleado = Contratosemp.objects.get( idempleado = idempleado) 
            tiposdecotizantes = Tiposdecotizantes.objects.get( tipocotizante  = form2.cleaned_data['contributor']  )
            subtipocotizantes = Subtipocotizantes.objects.get( subtipocotizante = form2.cleaned_data['subContributor'] )
            tiposalario = Tiposalario.objects.get( idtiposalario =  form2.cleaned_data['salaryType'] ) 
            costo = Costos.object.get(idcosto =  form2.cleaned_data['costCenter'] )
            subcosto = Subcostos.objects.get( idsubcosto =  form2.cleaned_data['subCostCenter'] )   
            sedes = Sedes.objects.get( idsede =   form2.cleaned_data['workPlace'] ) 
            eps = Entidadessegsocial.objects.get( identidad = form2.cleaned_data['eps'] )
            pen = Entidadessegsocial.objects.get( identidad = form2.cleaned_data['pensionFund'] )
            cjc = Entidadessegsocial.objects.get( identidad = form2.cleaned_data['accountType'] )
            modelo = ModelosContratos.objects.get( idmodelo = form2.cleaned_data['contractModel']) 
            
            contratos_instance = Contratos(
                    #* desde aqui 
                    cargo = cargos , 
                    fechainiciocontrato = form2.cleaned_data['contractStartDate'],
                    fechafincontrato = form2.cleaned_data['endDate'],
                    tipocontrato = tipocontrato , 
                    tiponomina = tipodenomina , 
                    bancocuenta = bancos , 
                    cuentanomina = form2.cleaned_data['payrollAccount'], 
                    tipocuentanomina = form2.cleaned_data['accountType'], 
                    centrotrabajo = centrotrabajo , 
                    ciudadcontratacion = ciudades , 
                    fondocesantias =  fondo , 
                    estadocontrato = 1 , 
                    salario = form2.cleaned_data['salary'], 
                    idempleado = empleado ,
                    tipocotizante =  tiposdecotizantes ,
                    subtipocotizante =  subtipocotizantes ,
                    formapago = form2.cleaned_data['paymentMethod'], 
                    metodoretefuente = '' , ## validar calculo 
                    porcentajeretefuente = 0, ## validar calculo 
                    valordeduciblevivienda = 0,## validar calculo 
                    saludretefuente = 0, ## validar calculo
                    pensionado = '2',
                    estadoliquidacion = 1,#choice Estadoliquidacion  
                    estadosegsocial = 0, #choice Estadosegsocial 
                    
                    tiposalario = tiposalario ,#Posible choice
                    idcosto = idcosto , 
                    idsubcosto = subcosto,
                    idsede = sedes, 
                    salariovariable = form2.cleaned_data['salaryMode'],
                    codeps = eps, 
                    codafp = pen ,
                    codccf = cjc ,
                    auxiliotransporte = True,
                    dependientes = 0,
                    valordeduciblemedicina = 0,#manualmente 
                    jornada = '',#choice
                    idmodelo = modelo , #enlace modelos_contratos
                    riesgo_pension = False , 
                    id_empresa = empresa ,

                )
            contratos_instance.save()
            empleado.estadocontrato = 1
            empleado.save()
            messages.success(request, 'El Contrato ha sido creado')
            return redirect('companies:hiring')
        else:
            for field, errors in form2.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else: 
        form_empleados = EmployeeForm(prefix='form1') 
        form_contratos = ContractForm(idempresa=idempresa,prefix='form2')
        empleados = Contratosemp.objects.filter(estadocontrato=4 , id_empresa__idempresa = idempresa )       
    
    return render(request, './companies/hiring.html',{'empleados':empleados,'form_empleados':form_empleados , 'form_contratos':form_contratos})
