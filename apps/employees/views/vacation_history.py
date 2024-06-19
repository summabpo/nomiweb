# apps/employees/views.py
from django.views.generic import ListView
from django.db.models import Q, Sum
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from apps.employees.models import Vacaciones
from apps.components.decorators import custom_permission

@method_decorator([login_required, custom_permission('employees')], name='dispatch')
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
