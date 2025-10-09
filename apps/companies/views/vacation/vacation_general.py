from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.filterform import FilterForm 
from apps.components.decorators import  role_required
from apps.common.models  import Contratosemp , Vacaciones ,Contratos 
from django.http import JsonResponse
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

@login_required
@role_required('company','accountant')
def vacation_general(request):
    """
    Vista que muestra una lista general de empleados activos con contrato para la empresa actual,
    con el propósito de gestionar vacaciones.

    Requiere que el usuario esté autenticado y tenga el rol de 'company' o 'accountant'.

    Recupera los contratos activos de empleados pertenecientes a la empresa del usuario actual,
    formatea correctamente los nombres para evitar valores None, y los pasa al contexto de la plantilla.

    Template renderizado: './companies/vacation_general.html'

    Contexto:
        - contratos_empleados (list): Lista de diccionarios con la información del empleado y su contrato.

    Returns:
        HttpResponse: Página renderizada con los datos de los empleados.
    """
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    # Obtener la lista de empleados activos
    contratos_empleados = (
        Contratos.objects
        .select_related('idempleado')
        .filter(
            estadocontrato=1,
            tipocontrato__idtipocontrato__in=[1, 2, 3, 4],
            id_empresa_id=idempresa
        )
        .values(
            'idempleado__docidentidad',
            'idempleado__sapellido',
            'idempleado__papellido',
            'idempleado__pnombre',
            'idempleado__snombre',
            'idempleado__idempleado',
            'idcontrato'
        )
    )

    # Limpiar nombres: eliminar None y "no data"
    for emp in contratos_empleados:
        for campo in [
            'idempleado__pnombre',
            'idempleado__snombre',
            'idempleado__papellido',
            'idempleado__sapellido'
        ]:
            valor = emp.get(campo)
            if valor is None or str(valor).strip().lower() == 'no data':
                emp[campo] = ''
    
    context = {
        'contratos_empleados': contratos_empleados,
    }
    
    return render(request, './companies/vacation_general.html', context)



@login_required
@role_required('company', 'accountant')
def vacation_resumen(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    vacaciones = Vacaciones.objects.filter(
        idcontrato__id_empresa=idempresa, 
        tipovac__idvac__in=[1, 2]
    ).values(
        "idcontrato__idempleado__docidentidad",
        "idcontrato__idempleado__papellido",
        "idcontrato__idempleado__sapellido",
        "idcontrato__idempleado__pnombre",
        "idcontrato__idempleado__snombre",
        "idcontrato",
        "fechainicialvac",
        "idvacaciones",
    ).order_by('-fechainicialvac')
    
    # Limpiar los valores "no data" y None
    vacaciones = [
        {
            k: (
                "" if (v is None or str(v).strip().lower() == "no data") 
                else v
            )
            for k, v in vac.items()
        }
        for vac in vacaciones
    ]
    
    context = {
        'vacaciones': vacaciones
    }
    
    return render(request, './companies/vacation_resumen.html', context)


@login_required
@role_required('company','accountant')
def vacation_resumen_data(request,id):
    
    
    vacaciones = Vacaciones.objects.get(idvacaciones=id)
        
    context = {
        'vacaciones' : vacaciones
    }
    
    return render(request, './companies/partials/vacation_resumen_data.html', context)


@login_required
@role_required('company', 'accountant')
def absences_resumen(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    vacaciones = Vacaciones.objects.filter(
        idcontrato__id_empresa=idempresa, 
        tipovac__idvac__in=[3, 4, 5]
    ).values(
        "idcontrato__idempleado__docidentidad",
        "idcontrato__idempleado__papellido",
        "idcontrato__idempleado__sapellido",
        "idcontrato__idempleado__pnombre",
        "idcontrato__idempleado__snombre",
        "idcontrato",
        "idvacaciones",
    ).order_by('-idvacaciones')
    
    # Limpiar "no data" y valores nulos
    vacaciones = [
        {
            k: (
                "" if (v is None or str(v).strip().lower() == "no data")
                else v
            )
            for k, v in vac.items()
        }
        for vac in vacaciones
    ]
    
    context = {
        'vacaciones': vacaciones
    }
    
    return render(request, './companies/absences_resumen.html', context)

@login_required
@role_required('company','accountant')
def absences_resumen_data(request,id):
    
    
    vacaciones = Vacaciones.objects.get(idvacaciones=id)
        
    context = {
        'vacaciones' : vacaciones
    }
    
    return render(request, './companies/partials/vacation_resumen_data.html', context)




@login_required
@role_required('company','accountant')
def get_novedades(request):
    """
    API View que retorna las novedades de tipo 'Vacaciones' o 'Ausencias/licencias no remuneradas'
    asociadas a un contrato específico en formato JSON.

    Requiere autenticación y rol de 'company' o 'accountant'.

    Parámetros GET:
        - tipo (str): Tipo de novedad a consultar ('Vacaciones' o cualquier otro para ausencias/licencias).
        - idcontrato (int): ID del contrato del cual se desean consultar las novedades.

    Returns:
        JsonResponse: Diccionario que contiene el nombre completo del empleado y una lista de novedades,
                      cada una con datos como fecha de inicio, último día, días calendario, días de vacaciones,
                      pago, periodo de inicio y fin, y ID de la novedad.

    Estructura del JSON:
    {
        "nombre_empleado": "Nombre Apellido",
        "novedades": [
            {
                "novedad": "Tipo de novedad",
                "fecha_inicial": "YYYY-MM-DD",
                "ultimo_dia": "YYYY-MM-DD",
                "dias_cal": "X",
                "dias_vac": "X",
                "pago": "XXX.XX",
                "periodo_ini": "YYYY-MM-DD",
                "periodo_fin": "YYYY-MM-DD",
                "id": X
            },
            ...
        ]
    }
    """
    tipo_novedad = request.GET.get('tipo', '')  
    idcontaro = request.GET.get('idcontrato', '')  
    # Obtenemos el contrato y el nombre del empleado relacionado
    contrato = Contratos.objects.filter(idcontrato=idcontaro).first()
    nombre_empleado = f" {contrato.idempleado.papellido}  {contrato.idempleado.sapellido} {contrato.idempleado.pnombre}  {contrato.idempleado.snombre} " 

    # Inicializamos la estructura de datos con el nombre del empleado
    data = {
        "nombre_empleado": nombre_empleado,
        "novedades": []  # Aquí almacenaremos las novedades
    }

    if tipo_novedad == 'Vacaciones':
        vacaciones = Vacaciones.objects.filter(idcontrato__idcontrato=idcontaro, tipovac__idvac__in=[1,2]) 
        for vacacion in vacaciones:
            novedad = {
                "novedad": vacacion.tipovac.nombrevacaus if vacacion.tipovac and vacacion.tipovac.nombrevacaus else '',
                "fecha_inicial": vacacion.fechainicialvac.strftime('%Y-%m-%d') if vacacion.fechainicialvac else '',
                "ultimo_dia": vacacion.ultimodiavac.strftime('%Y-%m-%d') if vacacion.ultimodiavac else '',
                "dias_cal": vacacion.diascalendario if vacacion.diascalendario is not None else '0',
                "dias_vac": vacacion.diasvac if vacacion.diasvac is not None else '0',
                "pago": str(vacacion.pagovac) if vacacion.pagovac is not None else '0',
                "periodo_ini": vacacion.perinicio.strftime('%Y-%m-%d') if vacacion.perinicio else '',
                "periodo_fin": vacacion.perfinal.strftime('%Y-%m-%d') if vacacion.perfinal else '',
                "id": vacacion.idvacaciones
            }
            data["novedades"].append(novedad)
            
    else:  # Asumimos 'ausencias' o 'licencias no remuneradas'
        vacaciones = Vacaciones.objects.filter(idcontrato__idcontrato=idcontaro, tipovac__idvac__in=[3,4,5]) 
        for vacacion in vacaciones:
            novedad = {
                "novedad": vacacion.tipovac.nombrevacaus if vacacion.tipovac and vacacion.tipovac.nombrevacaus else '',
                "fecha_inicial": vacacion.fechainicialvac.strftime('%Y-%m-%d') if vacacion.fechainicialvac else '',
                "ultimo_dia": vacacion.ultimodiavac.strftime('%Y-%m-%d') if vacacion.ultimodiavac else '',
                "dias_cal": vacacion.diascalendario if vacacion.diascalendario is not None else '0',
                "dias_vac": vacacion.diasvac if vacacion.diasvac is not None else '0',
                "pago": str(vacacion.pagovac) if vacacion.pagovac is not None else '0',
                "periodo_ini": vacacion.perinicio.strftime('%Y-%m-%d') if vacacion.perinicio else '',
                "periodo_fin": vacacion.perfinal.strftime('%Y-%m-%d') if vacacion.perfinal else '',
                "id": vacacion.idvacaciones
            }
            data["novedades"].append(novedad)
            
    return JsonResponse(data, safe=False)

