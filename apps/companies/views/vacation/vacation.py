from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.filterform import FilterForm 
from apps.components.decorators import  role_required
from apps.companies.models import Contratosemp , Vacaciones ,Contratos 



def vacation(request):
    selected_empleado = request.GET.get('empleado')
    
    # Obtener la lista de empleados
    empleados_select = Contratosemp.objects.all().order_by('papellido').values(
        'pnombre', 'snombre', 'papellido', 'sapellido', 'idempleado'
    )
    
    if selected_empleado:
        # Obtener el contrato más reciente del empleado seleccionado
        contrato = Contratos.objects.filter(
            idempleado__idempleado=selected_empleado
        ).order_by('-idcontrato').first()

        # Obtener las vacaciones relacionadas con el contrato
        vacaciones = Vacaciones.objects.filter(
            idcontrato=contrato
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
    else:
        vacaciones = []

    # Manejar valores nulos en empleados_select
    for emp in empleados_select:
        emp['pnombre'] = emp.get('pnombre', "")
        emp['snombre'] = emp.get('snombre', "")
        emp['papellido'] = emp.get('papellido', "")
        emp['sapellido'] = emp.get('sapellido', "")

    context = {
        'empleados_select': empleados_select,
        'selected_empleado': selected_empleado,
        'vacaciones': vacaciones,
    }
    
    return render(request, './companies/vacation.html', context)


