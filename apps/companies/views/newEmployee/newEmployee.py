from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.forms.EmployeeForm import EmployeeForm
from apps.companies.models import Tipodocumento , Paises , Ciudades , Contratosemp,Profesiones
from apps.companies.forms.EmployeeForm import EmployeeForm

def newEmployee(request):
    
    form = EmployeeForm    
    if request.method == 'POST':
        

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
    return render(request, './companies/NewEmployee.html',{'form':form})
