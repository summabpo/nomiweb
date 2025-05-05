from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.filterform import FilterForm
from apps.components.decorators import role_required
from apps.common.models  import Contratosemp, Vacaciones, Contratos
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

@login_required
@role_required('company','accountant')
def vacation(request):
    """
    Vista para consultar y visualizar el historial de vacaciones de los empleados activos en la empresa.

    Esta vista permite a usuarios con el rol 'company' o 'accountant' visualizar las vacaciones registradas para un 
    empleado específico, siempre que tenga un contrato activo. El usuario puede seleccionar al empleado desde una lista 
    y ver sus periodos vacacionales anteriores.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene la sesión del usuario autenticado y posibles parámetros GET, como el ID del empleado seleccionado.

    Returns
    -------
    HttpResponse
        Renderiza el template 'companies/vacation.html' con la información de los empleados y sus vacaciones, si aplica.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol 'company' o 'accountant' para acceder a esta vista.
    Solo se muestran empleados con contratos activos de tipo 1, 2, 3 o 4.
    Se aplican validaciones para manejar valores nulos tanto en los nombres de empleados como en los campos de vacaciones.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    selected_empleado = request.GET.get('empleado')
    
    # Obtener la lista de empleados
    empleados_select = Contratos.objects.filter(estadocontrato=1 ,tipocontrato__idtipocontrato__in =[1,2,3,4] , id_empresa_id = idempresa ).order_by('idempleado__papellido').values(
        'idempleado__pnombre', 'idempleado__snombre', 'idempleado__papellido', 'idempleado__sapellido', 'idempleado__idempleado','idcontrato'
    )
    
    if selected_empleado:
        # Obtener el contrato más reciente del empleado seleccionado
        contrato = Contratos.objects.filter(
            idempleado__idempleado=selected_empleado
        ).order_by('-idcontrato').first()

        # Obtener las vacaciones relacionadas con el contrato
        vacaciones = Vacaciones.objects.filter(
            idcontrato=contrato,
            tipovac__idvac__in=[1,2]
        ).values(
            'idcontrato__idempleado__docidentidad',
            'idcontrato__idcontrato',
            'idcontrato__idempleado__pnombre',
            'idcontrato__idempleado__snombre',
            'idcontrato__idempleado__papellido',
            'idcontrato__idempleado__sapellido',
            'tipovac__nombrevacaus',
            'fechainicialvac',
            'ultimodiavac',
            'diascalendario',
            'diasvac',
            'perinicio',
            'perfinal'
        )

        # Reemplazar los valores None de forma personalizada
        vacaciones = [
            {k: (0 if k in ['diascalendario', 'diasvac'] and v is None else ("" if v is None else v))
                for k, v in vac.items()}
            for vac in vacaciones
        ]
    else:
        vacaciones = []

    # Manejar valores nulos en empleados_select
    for emp in empleados_select:
        emp['idempleado__pnombre'] = '' if emp['idempleado__pnombre'] is None else emp['idempleado__pnombre']  
        emp['idempleado__snombre'] = '' if emp['idempleado__snombre'] is None else emp['idempleado__snombre']  
        emp['idempleado__papellido'] = '' if emp['idempleado__papellido'] is None else emp['idempleado__papellido']  
        emp['idempleado__sapellido'] = '' if emp['idempleado__sapellido'] is None else emp['idempleado__sapellido']  

    context = {
        'empleados_select': empleados_select,
        'selected_empleado': selected_empleado,
        'vacaciones': vacaciones,
    }

    return render(request, './companies/vacation.html', context)
