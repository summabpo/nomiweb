from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.filterform import FilterForm
from apps.components.decorators import role_required
from apps.companies.models import Contratosemp, Vacaciones, Contratos


def vacation(request):
    selected_empleado = request.GET.get('empleado')
    
    # Obtener la lista de empleados
    empleados_select = Contratos.objects.filter(estadocontrato=1 ,tipocontrato__idtipocontrato__in =[1,2,3,4] ).order_by('idempleado__papellido').values(
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
            tipovac__tipovac__in=[1,2]
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
        emp['idempleado__pnombre'] = emp.get('idempleado__pnombre', "")
        emp['idempleado__snombre'] = emp.get('idempleado__snombre', "")
        emp['idempleado__papellido'] = emp.get('idempleado__papellido', "")
        emp['idempleado__sapellido'] = emp.get('idempleado__sapellido', "")

    context = {
        'empleados_select': empleados_select,
        'selected_empleado': selected_empleado,
        'vacaciones': vacaciones,
    }

    return render(request, './companies/vacation.html', context)
