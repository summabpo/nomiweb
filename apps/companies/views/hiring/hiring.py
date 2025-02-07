from django.shortcuts import render, redirect
from apps.companies.forms.EmployeeForm import EmployeeForm
from django.contrib import messages
from apps.common.models  import Contratosemp,Tipodocumento,Costos,Subcostos,ModelosContratos,Sedes,Subtipocotizantes,Costos,Tiposalario,Ciudades,Paises,Empresa,Contratos,Tipocontrato,Cargos,Tipodenomina,Bancos,Centrotrabajo,Entidadessegsocial,Tiposdecotizantes
from apps.companies.forms.EmployeeForm import EmployeeForm
from apps.companies.forms.ContractForm  import ContractForm 
from django.http import JsonResponse

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
@role_required('company','accountant')
def hiring(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    empleados = {}
    form_empleados = EmployeeForm() 
    form_contratos = ContractForm(idempresa=idempresa)
    empleados = Contratosemp.objects.filter(estadocontrato=4 , id_empresa__idempresa = idempresa )  
    
    return render(request, './companies/hiring.html',{
        'empleados':empleados,
        'form_empleados':form_empleados ,
        'form_contratos':form_contratos ,
        'user': request.user})

@login_required
@role_required('company','accountant')
def hiring_employee(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    if request.method == 'POST':
        form_empleados = EmployeeForm(request.POST)
        
        if form_empleados.is_valid():
            tipodocumento = Tipodocumento.objects.get(codigo = form_empleados.cleaned_data['identification_type'] )
            ciudad1 = Ciudades.objects.get(idciudad = form_empleados.cleaned_data['birth_city'] )
            Paises1 = Paises.objects.get(idpais = form_empleados.cleaned_data['birth_country'] )
            
            ciudad2 = Ciudades.objects.get(idciudad = form_empleados.cleaned_data['residence_city'] )
            Paises2 = Paises.objects.get(idpais = form_empleados.cleaned_data['residence_country'])
            
            ciudad3 = Ciudades.objects.get(idciudad = form_empleados.cleaned_data['expedition_city'])
            
            empresa = Empresa.objects.get(idempresa = idempresa )
            
            height = form_empleados.cleaned_data['height']
            weight = form_empleados.cleaned_data['weight']
            height = height.replace(',', '.') if ',' in height else height
            weight = weight.replace(',', '.') if ',' in weight else weight
            height = float(height)
            weight = float(weight)

            
            contratosemp_instance = Contratosemp(
                docidentidad = form_empleados.cleaned_data['identification_number'],
                tipodocident = tipodocumento ,

                #Nombres y apellidos
                pnombre = form_empleados.cleaned_data['first_name'],
                snombre = form_empleados.cleaned_data['second_name'],
                papellido = form_empleados.cleaned_data['first_last_name'],
                sapellido = form_empleados.cleaned_data['second_last_name'],


                #Información de contacto
                email = form_empleados.cleaned_data['email'] ,
                telefonoempleado = form_empleados.cleaned_data['employee_phone'],
                celular = form_empleados.cleaned_data['cell_phone'],
                direccionempleado = form_empleados.cleaned_data['residence_address'],

                #Datos personales
                sexo = form_empleados.cleaned_data['sex'], 
                fechanac = form_empleados.cleaned_data['birthdate'],
                ciudadnacimiento = ciudad1, 
                paisnacimiento = Paises1,

                ciudadresidencia = ciudad2, 
                paisresidencia = Paises2,
                estadocivil = form_empleados.cleaned_data['marital_status'] , 

                #Datos académicos y profesionales
                profesion = form_empleados.cleaned_data['profession'] , 
                niveleducativo = form_empleados.cleaned_data['education_level'],

                #Información física
                estatura = height,
                peso = weight,
                gruposanguineo = form_empleados.cleaned_data['blood_group'],

                #Documentación
                fechaexpedicion = form_empleados.cleaned_data['expedition_date'],
                ciudadexpedicion = ciudad3 , 
                
                #Dotaciones
                dotpantalon = form_empleados.cleaned_data['pants_size'],
                dotcamisa = form_empleados.cleaned_data['shirt_size'],
                dotzapatos = form_empleados.cleaned_data['shoes_size'],

                #Otros datos
                estadocontrato = 4 ,
                estrato = form_empleados.cleaned_data['stratum'],
                numlibretamil = form_empleados.cleaned_data['military_id'],
                #Relación con la empresa
                id_empresa = empresa 
            )
            contratosemp_instance.save()
            return JsonResponse({'status': 'success', 'message': 'Empleado creado exitosamente'})
        else :
            #En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form_empleados.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")
    else:
        form_empleados = EmployeeForm()
    
    return render(request, './companies/partials/employeeModal.html',{'form_empleados':form_empleados })


@login_required
@role_required('company','accountant')
def hiring_contract(request,idempleado):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    if request.method == 'POST':
        form_contratos = ContractForm(request.POST,idempresa=idempresa ,empleado_actual = idempleado )
        if form_contratos.is_valid():
            empresa = Empresa.objects.get(idempresa = idempresa )
            cargos = get_or_none(Cargos, idcargo=form_contratos.cleaned_data['position'])
            tipocontrato = get_or_none(Tipocontrato, idtipocontrato=form_contratos.cleaned_data['contractType'])
            tipodenomina = get_or_none(Tipodenomina, idtiponomina=form_contratos.cleaned_data['payrollType'])
            bancos = get_or_none(Bancos, idbanco=form_contratos.cleaned_data['bankAccount'])
            centrotrabajo = get_or_none(Centrotrabajo, centrotrabajo=form_contratos.cleaned_data['arlWorkCenter'])
            ciudades = get_or_none(Ciudades, idciudad=form_contratos.cleaned_data['workLocation'])
            empleado = Contratosemp.objects.get(idempleado = idempleado )
            tiposdecotizantes = get_or_none(Tiposdecotizantes, tipocotizante=form_contratos.cleaned_data['contributor'])
            subtipocotizantes = get_or_none(Subtipocotizantes, subtipocotizante=form_contratos.cleaned_data['subContributor'])
            tiposalario = get_or_none(Tiposalario, idtiposalario=form_contratos.cleaned_data['salaryType'])
            costo = get_or_none(Costos, idcosto=form_contratos.cleaned_data['costCenter'])
            subcosto = get_or_none(Subcostos, idsubcosto=form_contratos.cleaned_data['subCostCenter'])
            sedes = get_or_none(Sedes, idsede=form_contratos.cleaned_data['workPlace'])
            eps = get_or_none(Entidadessegsocial, identidad=form_contratos.cleaned_data['eps'])
            pen = get_or_none(Entidadessegsocial, identidad=form_contratos.cleaned_data['pensionFund'])
            cjc = get_or_none(Entidadessegsocial, identidad=form_contratos.cleaned_data['CesanFund'])
            modelo = get_or_none(ModelosContratos, idmodelo=form_contratos.cleaned_data['contractModel'])
            
            contratos_instance = Contratos(
                    #* desde aqui 
                    cargo = cargos , 
                    fechainiciocontrato = form_contratos.cleaned_data['contractStartDate'],
                    fechafincontrato = form_contratos.cleaned_data['endDate'],
                    tipocontrato = tipocontrato , 
                    tiponomina = tipodenomina , 
                    bancocuenta = bancos , 
                    cuentanomina = form_contratos.cleaned_data['payrollAccount'], 
                    tipocuentanomina = form_contratos.cleaned_data['accountType'], 
                    centrotrabajo = centrotrabajo , 
                    ciudadcontratacion = ciudades , 
                    estadocontrato = 1 , 
                    salario = form_contratos.cleaned_data['salary'], 
                    idempleado = empleado ,
                    tipocotizante =  tiposdecotizantes ,
                    subtipocotizante =  subtipocotizantes ,
                    formapago = form_contratos.cleaned_data['paymentMethod'], 
                    metodoretefuente = '' , ## validar calculo 
                    porcentajeretefuente = 0, ## validar calculo 
                    valordeduciblevivienda = 0,## validar calculo 
                    saludretefuente = 0, ## validar calculo
                    pensionado = '2',
                    estadoliquidacion = 3,#choice Estadoliquidacion  
                    estadosegsocial = 3, #choice Estadosegsocial 
                    
                    tiposalario = tiposalario ,#Posible choice
                    idcosto = costo , 
                    idsubcosto = subcosto,
                    idsede = sedes, 
                    salariovariable = form_contratos.cleaned_data['salaryMode'],
                    codeps = eps, 
                    codafp = pen ,
                    codccf = cjc ,
                    auxiliotransporte = form_contratos.cleaned_data['livingPlace'],
                    dependientes = 0,
                    valordeduciblemedicina = 0,#manualmente 
                    jornada = '', #choice
                    idmodelo = modelo , #enlace modelos_contratos
                    riesgo_pension = False , 
                    id_empresa = empresa ,

                )
            contratos_instance.save()
            empleado.estadocontrato = 1
            empleado.save()
            return JsonResponse({'status': 'success','type': 'contract' ,'message': 'Contrato creado exitosamente'})
        else:
            for field, errors in form_contratos.errors.items():
                for error in errors:
                    print(f'{error} - {field} ' )
                    messages.error(request, f'{error}')
    else:
        form_contratos = ContractForm(idempresa=idempresa ,empleado_actual = idempleado )
    return render(request, './companies/partials/contractModal.html',{'form_contratos':form_contratos })



def get_or_none(model, **kwargs):
    """Obtiene un objeto de la base de datos o devuelve None si no se encuentra."""
    if any(v is None or v == '' for v in kwargs.values()):
        return None
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None  # Devuelve None si no existe


@login_required
@role_required('company','accountant')
def process_forms_contract(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    # Procesar los datos del formulario 2
    if request.method == 'POST':
        print(request.POST)
        form2 = ContractForm(request.POST,idempresa=idempresa)
        if form2.is_valid():
            empresa = Empresa.objects.get(idempresa = idempresa )
            cargos = get_or_none(Cargos, idcargo=form2.cleaned_data['position'])
            tipocontrato = get_or_none(Tipocontrato, idtipocontrato=form2.cleaned_data['contractType'])
            tipodenomina = get_or_none(Tipodenomina, idtiponomina=form2.cleaned_data['payrollType'])
            bancos = get_or_none(Bancos, idbanco=form2.cleaned_data['bankAccount'])
            centrotrabajo = get_or_none(Centrotrabajo, centrotrabajo=form2.cleaned_data['arlWorkCenter'])
            ciudades = get_or_none(Ciudades, idciudad=form2.cleaned_data['workLocation'])
            empleado = Contratosemp.objects.get(idempleado=form2.cleaned_data['Employees'])
            tiposdecotizantes = get_or_none(Tiposdecotizantes, tipocotizante=form2.cleaned_data['contributor'])
            subtipocotizantes = get_or_none(Subtipocotizantes, subtipocotizante=form2.cleaned_data['subContributor'])
            tiposalario = get_or_none(Tiposalario, idtiposalario=form2.cleaned_data['salaryType'])
            costo = get_or_none(Costos, idcosto=form2.cleaned_data['costCenter'])
            subcosto = get_or_none(Subcostos, idsubcosto=form2.cleaned_data['subCostCenter'])
            sedes = get_or_none(Sedes, idsede=form2.cleaned_data['workPlace'])
            eps = get_or_none(Entidadessegsocial, identidad=form2.cleaned_data['eps'])
            pen = get_or_none(Entidadessegsocial, identidad=form2.cleaned_data['pensionFund'])
            cjc = get_or_none(Entidadessegsocial, identidad=form2.cleaned_data['CesanFund'])
            modelo = get_or_none(ModelosContratos, idmodelo=form2.cleaned_data['contractModel'])
            
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
                    estadoliquidacion = 3,#choice Estadoliquidacion  
                    estadosegsocial = 3, #choice Estadosegsocial 
                    
                    tiposalario = tiposalario ,#Posible choice
                    idcosto = costo , 
                    idsubcosto = subcosto,
                    idsede = sedes, 
                    salariovariable = form2.cleaned_data['salaryMode'],
                    codeps = eps, 
                    codafp = pen ,
                    codccf = cjc ,
                    auxiliotransporte = form2.cleaned_data['livingPlace'],
                    dependientes = 0,
                    valordeduciblemedicina = 0,#manualmente 
                    jornada = '', #choice
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
                    print(f'{error} - {field} ' )
                    messages.error(request, f'{error}')
    
    return redirect('companies:hiring')



@login_required
@role_required('company')
def process_forms_employee(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    return redirect('companies:hiring')


