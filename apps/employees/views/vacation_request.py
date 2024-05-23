from django.shortcuts import render, redirect
from django.views.generic import  ListView
from django.db.models import Q
from apps.employees.forms.vacation_request_form import EmpVacacionesForm
#models
from apps.employees.models import EmpVacaciones

class VacationRequestList(ListView):
    template_name = 'employees/vacations_request.html'
    paginate_by = 10
    context_object_name = 'vacation_request_list'
    model = EmpVacaciones
    ordering = 'id_sol_vac'
    
    def get_queryset(self):
        queryset = EmpVacaciones.objects.filter(Q(idcontrato=3778) & (Q(tipovac=1) | Q(tipovac=2) | Q(tipovac= 3) | Q(tipovac=4))).select_related('tipovac')
        return queryset
   # return render(request, 'employees/vacations_request_list.html')

def vacations_request(request):
    if request.method == 'POST':
        form = EmpVacacionesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vacation_request_list')
    else:
        form = EmpVacacionesForm()

    return render(request, 'employees/vacations_request.html', {'form': form})

