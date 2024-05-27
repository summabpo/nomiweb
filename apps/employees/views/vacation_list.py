from django.db.models import Q, Sum
from django.shortcuts import render
# Create your views here.
from django.views.generic import  ListView

#models
from apps.employees.models import EmpVacaciones
from apps.employees.models import Vacaciones



#security
#from apps.components.decorators import custom_login_required ,custom_permission

#@custom_login_required
#@custom_permission('employees')

class VacationListAll(ListView):
    template_name = 'employees/vacation_list.html'
    paginate_by = 10
    context_object_name = 'vacation_list'
    model = EmpVacaciones

    
    def get_queryset(self):
        queryset = EmpVacaciones.objects.all()
        return queryset
    
    