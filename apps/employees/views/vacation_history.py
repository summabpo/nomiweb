# apps/employees/views.py
from django.views.generic import ListView
from django.db.models import Q, Sum
from django.views.generic import  ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from apps.common.models import Vacaciones, Contratos
from apps.components.decorators import  role_required
from django.shortcuts import render, redirect, get_object_or_404
from apps.components.decorators import  role_required

@login_required
@role_required('employee')
def vacationHistori(request):
    usuario = request.session.get('usuario', {})
    ide = usuario['idempleado']
    contrato = Contratos.objects.filter(idempleado=ide, estadocontrato=1).first()
    vacation_history = Vacaciones.objects.filter(Q(idcontrato_id=contrato.idcontrato) & (Q(tipovac__idvac=1) | Q(tipovac__idvac=2))).select_related('tipovac')

    context = {
            'vacation_history': vacation_history 
        }

    return render(request, 'employees/vacation_history.html', context)



@method_decorator([login_required, role_required('employees')], name='dispatch')
class VacationList(ListView):
    template_name = 'employees/vacation_history.html'
    paginate_by = 10
    context_object_name = 'vacation_history'
    model = Vacaciones
    
    def get_queryset(self):
        ide = self.request.session.get('idempleado')
        contrato = Contratos.objects.filter(idempleado=ide, estadocontrato=1).first()
        idc = contrato.idcontrato if contrato else None
        
        queryset = Vacaciones.objects.filter(Q(idcontrato=idc) & (Q(tipovac=1) | Q(tipovac=2))).select_related('tipovac').order_by('-fechapago')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_dias_habiles = self.get_queryset().aggregate(Sum('diasvac'))['diasvac__sum']
        context['total_dias_habiles'] = total_dias_habiles
        return context

