# apps/employees/views.py
from django.views.generic import ListView
from django.db.models import Q, Sum
from django.views.generic import  ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from apps.common.models import Vacaciones, Contratos
from apps.components.decorators import  role_required
from django.shortcuts import render, redirect, get_object_or_404

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

