from django.shortcuts import render, redirect
from django.db.models import Q, Sum
from apps.employees.forms.vacation_request_form import EmpVacacionesForm
# models
from apps.employees.models import EmpVacaciones, Vacaciones

idc = 3778


def vacation_request_function(request):
    idc = 3778  # Obtén el ID del contrato como corresponda
    if request.method == 'POST':
        form = EmpVacacionesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employees:form_vac')
    else:
        form = EmpVacacionesForm()

    # Obtener la suma de días de vacaciones disfrutadas
    resultado_vacaciones = Vacaciones.objects.filter(idcontrato=idc).aggregate(dias_vacaciones=Sum('diasvac'))
    dias_vacaciones = resultado_vacaciones['dias_vacaciones'] if resultado_vacaciones['dias_vacaciones'] is not None else 0

    vacation_list = EmpVacaciones.objects.all()
    
    context = {
        'form': form,
        'dias_vacaciones': dias_vacaciones,
        'vacation_list': vacation_list,
        'idc': idc,
    }

    return render(request, 'employees/vacations_request.html', context)