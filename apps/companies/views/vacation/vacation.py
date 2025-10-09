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

    def clean_text(value):
        """Elimina 'no data', None o valores vacíos."""
        if isinstance(value, str) and value.strip().lower() == "no data":
            return ""
        return value or ""

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    selected_empleado = request.GET.get('empleado')

    # Obtener lista de empleados activos
    empleados_select = (
        Contratos.objects.filter(
            estadocontrato=1,
            tipocontrato__idtipocontrato__in=[1, 2, 3, 4],
            id_empresa_id=idempresa
        )
        .order_by('idempleado__papellido')
        .values(
            'idempleado__pnombre',
            'idempleado__snombre',
            'idempleado__papellido',
            'idempleado__sapellido',
            'idempleado__idempleado',
            'idcontrato'
        )
    )

    # Limpiar los posibles "no data" o None
    for emp in empleados_select:
        for campo in [
            'idempleado__pnombre',
            'idempleado__snombre',
            'idempleado__papellido',
            'idempleado__sapellido'
        ]:
            emp[campo] = clean_text(emp.get(campo))

    # Inicializar vacaciones
    vacaciones = []

    if selected_empleado:
        contrato = (
            Contratos.objects.filter(idempleado__idempleado=selected_empleado)
            .order_by('-idcontrato')
            .first()
        )

        if contrato:
            vacaciones_qs = Vacaciones.objects.filter(
                idcontrato=contrato,
                tipovac__idvac__in=[1, 2]
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

            # Limpieza profunda de los datos
            vacaciones = []
            for vac in vacaciones_qs:
                vac_limpia = {}
                for k, v in vac.items():
                    if k in ['diascalendario', 'diasvac']:
                        vac_limpia[k] = v if isinstance(v, (int, float)) else 0
                    else:
                        vac_limpia[k] = clean_text(v)
                vacaciones.append(vac_limpia)

    context = {
        'empleados_select': empleados_select,
        'selected_empleado': selected_empleado,
        'vacaciones': vacaciones,
    }

    return render(request, './companies/vacation.html', context)