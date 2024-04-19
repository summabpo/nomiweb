from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.forms.EmployeeForm import EmployeeForm
from apps.companies.models import Tipodocumento , Paises , Ciudades , Contratosemp,Profesiones


def newEmployee(request):
    TipoDocumento = Tipodocumento.objects.using("lectaen").all()
    ciudades = Ciudades.objects.using("lectaen").all()
    paises = Paises.objects.using("lectaen").all()
    profesiones = Profesiones.objects.using("lectaen").all()
    
    if request.method == 'POST':
        identificationType = request.POST.get('identification_type')
        identificationNumber = request.POST.get('identification_number')
        expeditionDate = request.POST.get('expedition_date')
        expeditionCity = request.POST.get('expedition_city')
        firstName = request.POST.get('first_name').upper()
        secondName = request.POST.get('second_name').upper()
        firstLastName = request.POST.get('first_last_name').upper()
        secondLastName = request.POST.get('second_last_name').upper()
        sex = request.POST.get('sex')
        height = request.POST.get('height')
        maritalStatus = request.POST.get('marital_status')
        weight = request.POST.get('weight')
        birthdate = request.POST.get('birthdate')
        educationLevel = request.POST.get('education_level')
        birthCity = request.POST.get('birth_city')
        stratum = request.POST.get('stratum')
        birthCountry = request.POST.get('birth_country')
        militaryId = request.POST.get('military_id')
        bloodGroup = request.POST.get('blood_group')
        profession = request.POST.get('profession')
        residenceAddress = request.POST.get('residence_address')
        email = request.POST.get('email')
        residenceCity = request.POST.get('residence_city')
        cellPhone = request.POST.get('cell_phone')
        residenceCountry = request.POST.get('residence_country')
        employeePhone = request.POST.get('employee_phone')
        
        pantsSize = request.POST.get('pants_size')
        shirtSize = request.POST.get('shirt_size')
        shoesSize = request.POST.get('shoes_size')

        #! falta dato para que se vea que le falta contrato 
        # Crear una nueva instancia del modelo Contratosemp y guardar los datos
        nuevo_empleado = Contratosemp(
            docidentidad=identificationNumber,
            tipodocident=identificationType,
            pnombre=firstName,
            snombre=secondName,
            papellido=firstLastName,
            sapellido=secondLastName,
            fechanac=birthdate,
            ciudadnacimiento=birthCity,
            telefonoempleado=employeePhone,
            direccionempleado=residenceAddress,
            sexo=sex,
            email=email,
            ciudadresidencia=residenceCity,
            estadocivil=maritalStatus,
            paisnacimiento=birthCountry,
            paisresidencia=residenceCountry,
            celular=cellPhone,
            profesion=profession,
            niveleducativo=educationLevel,
            gruposanguineo=bloodGroup,
            estatura=height,
            peso=weight,
            fechaexpedicion=expeditionDate,
            ciudadexpedicion=expeditionCity,
            estrato=stratum,
            numlibretamil=militaryId,
            dotpantalon = pantsSize,
            dotcamisa = shirtSize,
            dotzapatos = shoesSize ,
        )
        nuevo_empleado.save()        
    return render(request, './companies/NewEmployee.html',
                    {'TipoDocumento':TipoDocumento
                    ,'Ciudades':ciudades
                    ,'paises':paises,
                    'profesiones':profesiones
                    })
