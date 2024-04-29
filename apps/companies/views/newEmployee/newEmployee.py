from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.forms.EmployeeForm import EmployeeForm
from django.contrib import messages
from apps.companies.models import Tipodocumento , Paises , Ciudades , Contratosemp,Profesiones
from apps.companies.forms.EmployeeForm import EmployeeForm

def newEmployee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            try:
                
                height = form.cleaned_data['height']
                weight = form.cleaned_data['weight']
                height = height.replace(',', '.') if ',' in height else height
                weight = weight.replace(',', '.') if ',' in weight else weight
                height = float(height)
                weight = float(weight)
                
                contratosemp_instance = Contratosemp(
                docidentidad=form.cleaned_data['identification_number'],
                tipodocident=form.cleaned_data['identification_type'],
                pnombre=form.cleaned_data['first_name'],
                snombre=form.cleaned_data['second_name'],
                papellido=form.cleaned_data['first_last_name'],
                sapellido=form.cleaned_data['second_last_name'],
                fechanac=form.cleaned_data['birthdate'],
                ciudadnacimiento=form.cleaned_data['birth_city'],
                telefonoempleado=form.cleaned_data['employee_phone'],
                direccionempleado=form.cleaned_data['residence_address'],
                sexo=form.cleaned_data['sex'],
                email=form.cleaned_data['email'],
                ciudadresidencia=form.cleaned_data['residence_city'],
                estadocivil=form.cleaned_data['marital_status'],
                paisnacimiento=form.cleaned_data['birth_country'],
                paisresidencia=form.cleaned_data['residence_country'],
                celular=form.cleaned_data['cell_phone'],
                profesion=form.cleaned_data['profession'],
                niveleducativo=form.cleaned_data['education_level'],
                gruposanguineo=form.cleaned_data['blood_group'],
                estatura=height,
                peso=weight,
                fechaexpedicion=form.cleaned_data['expedition_date'],
                ciudadexpedicion=form.cleaned_data['expedition_city'],
                dotpantalon=form.cleaned_data['pants_size'],
                dotcamisa=form.cleaned_data['shirt_size'],
                dotzapatos=form.cleaned_data['shoes_size'],
                estrato=form.cleaned_data['stratum'],
                numlibretamil=form.cleaned_data['military_id'],
                estadocontrato=4
            )
                contratosemp_instance.save()
                messages.success(request, 'El Empleado ha sido creado')
                return  redirect('companies:newemployee')
            except Exception as e:
                messages_error = 'Se produjo un error al guardar el empleado.' + str(e.args)
                messages.error(request, messages_error)
                return redirect('companies:newemployee')
    else:
        form = EmployeeForm    
    return render(request, './companies/NewEmployee.html',{'form':form})
