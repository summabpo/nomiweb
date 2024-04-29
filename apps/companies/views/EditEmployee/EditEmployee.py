from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Tipodocumento , Paises , Ciudades , Contratosemp , Contratos
from apps.companies.forms.EmployeeForm import EmployeeForm
from django.contrib import messages



def EditEmployeeVisual(request,idempleado):
    empleado = Contratosemp.objects.using("lectaen").get(idempleado=idempleado) 
    
    tipo_documento = Tipodocumento.objects.using("lectaen").get(codigo=empleado.tipodocident) 
    
    
    
    ciudadex = Ciudades.objects.using("lectaen").get(idciudad=empleado.ciudadexpedicion) 
    ciudadna = Ciudades.objects.using("lectaen").get(idciudad=empleado.ciudadnacimiento) 
    
    
    campos_a_ajustar = [
    'identification_type', 'identification_number', 'expedition_date', 'expedition_city', 'first_name',
    'second_name', 'first_last_name', 'second_last_name', 'sex', 'birthdate', 'birth_city','birth_country','blood_group'
    ]
    
    DicContract = {
        'ciudadexpedicion':ciudadex.ciudad + ' - ' + ciudadex.departamento,
        'ciudadnaci': ciudadna.ciudad + ' - ' + ciudadna.departamento,
        'nombre': empleado.papellido + ' ' + empleado.sapellido + ' ' + empleado.pnombre + ' ' + empleado.snombre,
        'id': empleado.idempleado
    }
    
    
    
    initial_data = {
        'identification_type':empleado.tipodocident,
        'identification_number':empleado.docidentidad,
        'expedition_date':str(empleado.fechaexpedicion),
        'expedition_city':empleado.ciudadexpedicion,
        'first_name':empleado.pnombre,
        'second_name':empleado.snombre,
        'first_last_name':empleado.papellido,
        'second_last_name':empleado.sapellido,
        'sex':empleado.sexo,
        'height':str(empleado.estatura),
        'marital_status':empleado.estadocivil,
        'weight':empleado.peso,
        'first_name':empleado.pnombre,
        'second_name':empleado.snombre,
        'birthdate':str(empleado.fechanac),
        'education_level':empleado.niveleducativo,
        'birth_city':empleado.ciudadexpedicion,
        'stratum':str(empleado.estrato),
        'birth_country':empleado.paisnacimiento,
        'military_id':empleado.numlibretamil,
        'blood_group':empleado.gruposanguineo,
        'profession':empleado.estrato,
        'residence_address':empleado.direccionempleado,
        'email':empleado.email,
        'residence_city':empleado.ciudadresidencia,
        'cell_phone':empleado.celular,
        'residence_country':empleado.paisresidencia,
        'employee_phone':empleado.telefonoempleado,
        'pants_size':empleado.dotpantalon,
        'shirt_size':empleado.dotcamisa,
        'shoes_size':empleado.dotzapatos,

            }
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST)            
        if form.is_valid():
            
            messages.success(request, 'El Contrato ha sido creado')
            return  redirect('companies:newcontractvisual')
            # try:
                
            # except Exception as e:
            #     print(e)
            #     messages_error = 'Se produjo un error al guardar el Contrato.' + str(e.args)
            #     messages.error(request, messages_error)
            #     return redirect('companies:newemployee')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en el campo '{field}': {error}")
            return redirect('companies:newemployee')
    else:
        
        
        activate = request.GET.get('premium', False)
        form = EmployeeForm(initial=initial_data) 
        form.set_premium_fields(premium=activate, fields_to_adjust=campos_a_ajustar) 
        
    
    return render(request, './companies/EditEmployeevisual.html',{'DicContract':DicContract , 'form':form})




def EditEmployeeSearch(request):
    contratos_empleados = Contratos.objects.using("lectaen") \
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede') \
        .filter(estadocontrato=1) \
        .values('idempleado__docidentidad', 'idempleado__papellido', 'idempleado__sapellido','idempleado__pnombre',
                'idempleado__snombre', 'fechainiciocontrato', 'cargo', 'idempleado__direccionempleado',
                'ciudadcontratacion__ciudad','idempleado__celular','idempleado__email','idempleado__idempleado')

    empleados = []
    for contrato in contratos_empleados:
        nombre_empleado = f"{contrato['idempleado__papellido']} {contrato['idempleado__sapellido']}  {contrato['idempleado__pnombre']} {contrato['idempleado__snombre']}"
        contrato_data = {
            'documento': contrato['idempleado__docidentidad'],
            'nombre': nombre_empleado,
            'fechainiciocontrato': contrato['fechainiciocontrato'],
            'cargo': contrato['cargo'],
            'dirección': contrato['idempleado__direccionempleado'],
            'ciudad': contrato['ciudadcontratacion__ciudad'],
            'celular': contrato['idempleado__celular'],
            'mail': contrato['idempleado__email'],
            'id':contrato['idempleado__idempleado'],
        }

        empleados.append(contrato_data)
        
    return render(request, './companies/EditEmployeesearch.html', {'empleados': empleados})





