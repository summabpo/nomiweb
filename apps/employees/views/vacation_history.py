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
    
    """
    Muestra el historial de vacaciones del empleado.

    Esta vista muestra las vacaciones solicitadas por el empleado. Filtra las vacaciones asociadas al contrato del empleado que sean de tipo "vacaciones" o "descanso compensatorio". Los datos se obtienen a través del modelo `Vacaciones`, que está relacionado con el modelo `Contratos` para obtener las vacaciones asociadas al contrato del empleado.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP que contiene la información de la sesión del usuario y los datos relacionados con las vacaciones del empleado.

    Returns
    -------
    HttpResponse
        Renderiza la página `vacation_history.html` con el historial de vacaciones del empleado.

    Notes
    -----
    - Solo accesible para empleados autenticados.
    - La vista obtiene el primer contrato asociado al empleado autenticado y luego obtiene las vacaciones que corresponden a ese contrato.
    - Filtra las vacaciones de tipo 1 (vacaciones) y tipo 2 (descanso compensatorio).
    - El resultado se muestra en la plantilla `vacation_history.html`.
    """

    usuario = request.session.get('usuario', {})
    ide = usuario['idempleado']
    contrato = Contratos.objects.filter(idempleado=ide).first()
    vacation_history = Vacaciones.objects.filter(Q(idcontrato_id=contrato.idcontrato) & (Q(tipovac__idvac=1) | Q(tipovac__idvac=2))).select_related('tipovac')

    context = {
            'vacation_history': vacation_history 
        }

    return render(request, 'employees/vacation_history.html', context)

