from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.filterform import FilterForm 
from apps.components.decorators import  role_required
from apps.companies.models import Contratosemp , Vacaciones ,Contratos 
from django.http import JsonResponse


def vacation_general(request):
    # Obtener la lista de empleados
    contratos_empleados = Contratos.objects\
        .select_related('idempleado') \
        .filter(estadocontrato=1 ,tipocontrato__idtipocontrato__in =[1,2,3,4] ) \
        .values('idempleado__docidentidad','idempleado__sapellido', 'idempleado__papellido', 'idempleado__pnombre',
                'idempleado__snombre','idempleado__idempleado','idcontrato') 
    
    context = {
        'contratos_empleados': contratos_empleados,
    }
    
    return render(request, './companies/vacation_general.html', context)


def get_novedades(request):
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

    if tipo_novedad == 'vacaciones':
        vacaciones = Vacaciones.objects.filter(idcontrato__idcontrato=idcontaro, tipovac__tipovac__in=[1,2]) 
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
        vacaciones = Vacaciones.objects.filter(idcontrato__idcontrato=idcontaro, tipovac__tipovac__in=[3,4,5]) 
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

