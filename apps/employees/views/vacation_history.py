from django.db.models import Q, Sum
from django.shortcuts import render
# Create your views here.
from django.views.generic import  ListView

#models
from apps.employees.models import Vacaciones


#security
#from apps.components.decorators import custom_login_required ,custom_permission

#@custom_login_required
#@custom_permission('employees')

class VacationList(ListView):
    template_name = 'employees/vacation_history.html'
    paginate_by = 10
    context_object_name = 'vacation_history'
    model = Vacaciones
    ordering = 'idvacaciones'
    
    def get_queryset(self):
        queryset = Vacaciones.objects.filter(Q(idcontrato=3313) & (Q(tipovac=1) | Q(tipovac=2))).select_related('tipovac')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_dias_habiles = self.get_queryset().aggregate(Sum('diasvac'))['diasvac__sum']
        context['total_dias_habiles'] = total_dias_habiles
        return context