from django.db.models import Q, Sum
from django.shortcuts import render
from django.views.generic import  ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from apps.employees.models import Vacaciones, Contratos
from apps.components.decorators import custom_permission

@method_decorator([login_required, custom_permission('employees')], name='dispatch')


class VacationList(ListView):
    template_name = 'employees/vacation_history.html'
    paginate_by = 10
    context_object_name = 'vacation_history'
    model = Vacaciones
    ordering = 'idvacaciones'
    
    def get_queryset(self):
        ide = self.request.session.get('idempleado')
        contrato = Contratos.objects.filter(idempleado=ide, estadocontrato=1).first()
        idc = contrato.idcontrato if contrato else None
        
        queryset = Vacaciones.objects.filter(Q(idcontrato=idc) & (Q(tipovac=1) | Q(tipovac=2))).select_related('tipovac')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_dias_habiles = self.get_queryset().aggregate(Sum('diasvac'))['diasvac__sum']
        context['total_dias_habiles'] = total_dias_habiles
        return context