from django.shortcuts import render, redirect
from apps.employees.forms.vacation_request_form import EmpVacacionesForm

def vacations_request(request):
    if request.method == 'POST':
        form = EmpVacacionesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_url')  
    else:
        form = EmpVacacionesForm()

    return render(request, 'employees/vacations_request.html', {'form': form})