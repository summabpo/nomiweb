from django.shortcuts import render, redirect, get_object_or_404
from apps.common.models  import Tipodocumento , Paises , Ciudades , Contratosemp , Contratos
from .EditForm import EmployeeForm
from django.contrib import messages
from apps.components.decorators import custom_login_required ,custom_permission

from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

@login_required
@role_required('company','accountant')
def EditEmployeeVisual(request,idempleado):
    empleado = Contratosemp.objects.get(idempleado=idempleado) 
    DicContract = {
        'nombre': (empleado.papellido or '') + ' ' + (empleado.sapellido or '') + ' ' + (empleado.pnombre or '') + ' ' + (empleado.snombre or ''),
        'id': empleado.idempleado
    }

    initial_data = {
        'identification_type':empleado.tipodocident.codigo,
        'identification_number':empleado.docidentidad,
        'expedition_date':str(empleado.fechaexpedicion),
        'expedition_city':empleado.ciudadexpedicion.idciudad,
        'first_name':empleado.pnombre,
        'second_name':empleado.snombre,
        'first_last_name':empleado.papellido,
        'second_last_name':empleado.sapellido,
        'sex':empleado.sexo,
        'height': str(empleado.estatura) if empleado.estatura not in [None,'None', ''] else "0",
        'marital_status':empleado.estadocivil,
        'weight': empleado.peso if empleado.peso not in [None,'None', ''] else 0,
        'first_name':empleado.pnombre,
        'second_name':empleado.snombre,
        'birthdate':str(empleado.fechanac),
        'education_level':empleado.niveleducativo,
        'birth_city':empleado.ciudadexpedicion.idciudad,
        'stratum':empleado.estrato,
        'birth_country':empleado.paisnacimiento.idpais,
        'military_id':empleado.numlibretamil,
        'blood_group':empleado.gruposanguineo,
        'profession':empleado.estrato,
        'residence_address':empleado.direccionempleado,
        'email':empleado.email,
        'residence_city':empleado.ciudadresidencia.idciudad,
        'cell_phone':empleado.celular,
        'residence_country':empleado.paisresidencia.idpais,
        'employee_phone':empleado.telefonoempleado,
        'pants_size':empleado.dotpantalon,
        'shirt_size':empleado.dotcamisa,
        'shoes_size':empleado.dotzapatos,

            }
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST)     
        
        if form.is_valid():
            
            # Campos del formulario y su relación con el modelo Contratosemp
            # Formulario Field         -> Modelo Field
            # -------------------------|-------------------------
            # height                   -> estatura 
            # marital_status           -> estadocivil
            # weight                   -> peso
            # education_level          -> niveleducativo
            # stratum                  -> estrato
            # military_id              -> numlibretamil
            # profession               -> profesion
            # residence_address        -> direccionempleado
            # email                    -> email
            # residence_city           -> ciudadresidencia
            # cell_phone               -> celular
            # residence_country        -> paisresidencia
            # employee_phone           -> telefonoempleado
            # pants_size               -> dotpantalon
            # shirt_size               -> dotcamisa
            # shoes_size               -> dotzapatos
            
            try:
                if form.cleaned_data['height'] != empleado.estatura:
                    empleado.estatura = form.cleaned_data['height']

                if form.cleaned_data['marital_status'] != empleado.estadocivil:
                    empleado.estadocivil = form.cleaned_data['marital_status']

                if form.cleaned_data['weight'] != empleado.peso:
                    empleado.peso = form.cleaned_data['weight']

                if form.cleaned_data['education_level'] != empleado.niveleducativo:
                    empleado.niveleducativo = form.cleaned_data['education_level']

                if form.cleaned_data['stratum'] != empleado.estrato:
                    empleado.estrato = form.cleaned_data['stratum']

                if form.cleaned_data['military_id'] != empleado.numlibretamil:
                    empleado.numlibretamil = form.cleaned_data['military_id']

                if form.cleaned_data['profession'] != empleado.profesion:
                    empleado.profesion = form.cleaned_data['profession']

                if form.cleaned_data['residence_address'] != empleado.direccionempleado:
                    empleado.direccionempleado = form.cleaned_data['residence_address']

                if form.cleaned_data['email'] != empleado.email:
                    empleado.email = form.cleaned_data['email']

                if form.cleaned_data['residence_city'] is not None:
                    ciudad_residencia = Ciudades.objects.get(idciudad=form.cleaned_data['residence_city'])
                    if ciudad_residencia != empleado.ciudadresidencia:
                        empleado.ciudadresidencia = ciudad_residencia

                if form.cleaned_data['cell_phone'] != empleado.celular:
                    empleado.celular = form.cleaned_data['cell_phone']

                if form.cleaned_data['residence_country'] is not None:
                    pais_residencia = Paises.objects.get(idpais=form.cleaned_data['residence_country'])
                    if pais_residencia != empleado.paisresidencia:
                        empleado.paisresidencia = pais_residencia

                if form.cleaned_data['employee_phone'] != empleado.telefonoempleado:
                    empleado.telefonoempleado = form.cleaned_data['employee_phone']

                if form.cleaned_data['pants_size'] != empleado.dotpantalon:
                    empleado.dotpantalon = form.cleaned_data['pants_size']

                if form.cleaned_data['shirt_size'] != empleado.dotcamisa:
                    empleado.dotcamisa = form.cleaned_data['shirt_size']

                if form.cleaned_data['shoes_size'] != empleado.dotzapatos:
                    empleado.dotzapatos = form.cleaned_data['shoes_size']

                # Guardar los cambios
                empleado.save()
                messages.success(request, 'El Empleado ha sido Actualizado')
                return  redirect('companies:startcompanies')
            except Exception as e:
                messages_error = 'Se produjo un error al guardar el Empleado.' + str(e.args)
                messages.error(request, messages_error)
                return redirect('companies:editemployeevisual',idempleado=empleado.idempleado)
            
            
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en el campo '{field}': {error}")
            return redirect('companies:editemployeevisual',idempleado=empleado.idempleado)
    else:
        form = EmployeeForm(initial=initial_data) 
          
        
    
    return render(request, './companies/EditEmployeevisual.html',{'DicContract':DicContract , 'form':form})



@login_required
@role_required('company')
def EditEmployeeSearch(request):
    contratos_empleados = Contratos.objects \
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





