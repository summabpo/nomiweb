from django.shortcuts import render, redirect
from django.db.models import Sum
from apps.employees.forms.vacation_request_form import EmpVacacionesForm
from apps.employees.models import EmpVacaciones, Vacaciones

def vacation_request_function(request):
    idc = request.session.get('idcontrato')
    form = EmpVacacionesForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('employees:form_vac')

    dias_vacaciones = Vacaciones.objects.filter(idcontrato=idc).aggregate(Sum('diasvac'))['diasvac__sum'] or 0

    vacation_list = EmpVacaciones.objects.all()

    context = {
        'form': form,
        'dias_vacaciones': dias_vacaciones,
        'vacation_list': vacation_list,
        'idc': idc,
    }

    return render(request, 'employees/vacations_request.html', context)
