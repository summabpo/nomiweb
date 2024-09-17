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
        .filter(estadocontrato=1) \
        .values('idempleado__docidentidad','idempleado__sapellido', 'idempleado__papellido', 'idempleado__pnombre',
                'idempleado__snombre','idempleado__idempleado','idcontrato')[:20]
    
    context = {
        'contratos_empleados': contratos_empleados,
    }
    
    return render(request, './companies/vacation_general.html', context)


def get_novedades(request):
    tipo_novedad = request.GET.get('tipo', 'vacaciones')  


    if tipo_novedad == 'vacaciones':
        data = [
            {"novedad": "Vacaciones", "fecha_inicial": "2024-01-01", "ultimo_dia": "2024-01-10", "dias_cal": 10, "dias_vac": 5, "pago": "500", "periodo_ini": "2024-01-01", "periodo_fin": "2024-01-10", "id": 1},
            {"novedad": "Licencia Remunerada", "fecha_inicial": "2024-02-01", "ultimo_dia": "2024-02-05", "dias_cal": 5, "dias_vac": 2, "pago": "200", "periodo_ini": "2024-02-01", "periodo_fin": "2024-02-05", "id": 2},
            {"novedad": "Vacaciones", "fecha_inicial": "2024-03-15", "ultimo_dia": "2024-03-20", "dias_cal": 6, "dias_vac": 3, "pago": "300", "periodo_ini": "2024-03-15", "periodo_fin": "2024-03-20", "id": 3},
            {"novedad": "Licencia Remunerada", "fecha_inicial": "2024-04-01", "ultimo_dia": "2024-04-04", "dias_cal": 4, "dias_vac": 1, "pago": "150", "periodo_ini": "2024-04-01", "periodo_fin": "2024-04-04", "id": 4},
            {"novedad": "Vacaciones", "fecha_inicial": "2024-05-10", "ultimo_dia": "2024-05-15", "dias_cal": 6, "dias_vac": 4, "pago": "400", "periodo_ini": "2024-05-10", "periodo_fin": "2024-05-15", "id": 5},
            {"novedad": "Licencia Remunerada", "fecha_inicial": "2024-06-01", "ultimo_dia": "2024-06-03", "dias_cal": 3, "dias_vac": 2, "pago": "120", "periodo_ini": "2024-06-01", "periodo_fin": "2024-06-03", "id": 6},
            {"novedad": "Vacaciones", "fecha_inicial": "2024-07-15", "ultimo_dia": "2024-07-25", "dias_cal": 11, "dias_vac": 6, "pago": "550", "periodo_ini": "2024-07-15", "periodo_fin": "2024-07-25", "id": 7},
            {"novedad": "Licencia Remunerada", "fecha_inicial": "2024-08-01", "ultimo_dia": "2024-08-07", "dias_cal": 7, "dias_vac": 3, "pago": "250", "periodo_ini": "2024-08-01", "periodo_fin": "2024-08-07", "id": 8},
            {"novedad": "Vacaciones", "fecha_inicial": "2024-09-10", "ultimo_dia": "2024-09-15", "dias_cal": 6, "dias_vac": 4, "pago": "350", "periodo_ini": "2024-09-10", "periodo_fin": "2024-09-15", "id": 9},
            {"novedad": "Licencia Remunerada", "fecha_inicial": "2024-10-01", "ultimo_dia": "2024-10-05", "dias_cal": 5, "dias_vac": 2, "pago": "180", "periodo_ini": "2024-10-01", "periodo_fin": "2024-10-05", "id": 10},
            {"novedad": "Vacaciones", "fecha_inicial": "2024-11-05", "ultimo_dia": "2024-11-15", "dias_cal": 10, "dias_vac": 5, "pago": "500", "periodo_ini": "2024-11-05", "periodo_fin": "2024-11-15", "id": 11},
            {"novedad": "Licencia Remunerada", "fecha_inicial": "2024-12-01", "ultimo_dia": "2024-12-04", "dias_cal": 4, "dias_vac": 2, "pago": "150", "periodo_ini": "2024-12-01", "periodo_fin": "2024-12-04", "id": 12},
            {"novedad": "Vacaciones", "fecha_inicial": "2024-12-20", "ultimo_dia": "2024-12-30", "dias_cal": 11, "dias_vac": 7, "pago": "600", "periodo_ini": "2024-12-20", "periodo_fin": "2024-12-30", "id": 13},
            {"novedad": "Licencia Remunerada", "fecha_inicial": "2024-01-10", "ultimo_dia": "2024-01-15", "dias_cal": 6, "dias_vac": 3, "pago": "220", "periodo_ini": "2024-01-10", "periodo_fin": "2024-01-15", "id": 14}
        ]
    else:  # Asumimos 'ausencias' o 'licencias no remuneradas'
        print('aqui ando')
        data = [
            {"novedad": "Ausencia", "fecha_inicial": "2024-01-01", "ultimo_dia": "2024-01-03", "dias_cal": 3, "dias_vac": 1, "pago": "100", "periodo_ini": "2024-01-01", "periodo_fin": "2024-01-03", "id": 1},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2024-02-01", "ultimo_dia": "2024-02-10", "dias_cal": 10, "dias_vac": 5, "pago": "0", "periodo_ini": "2024-02-01", "periodo_fin": "2024-02-10", "id": 2},
            {"novedad": "Ausencia", "fecha_inicial": "2024-03-01", "ultimo_dia": "2024-03-03", "dias_cal": 3, "dias_vac": 1, "pago": "100", "periodo_ini": "2024-03-01", "periodo_fin": "2024-03-03", "id": 3},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2024-04-01", "ultimo_dia": "2024-04-15", "dias_cal": 15, "dias_vac": 7, "pago": "0", "periodo_ini": "2024-04-01", "periodo_fin": "2024-04-15", "id": 4},
            {"novedad": "Ausencia", "fecha_inicial": "2024-05-01", "ultimo_dia": "2024-05-04", "dias_cal": 4, "dias_vac": 2, "pago": "120", "periodo_ini": "2024-05-01", "periodo_fin": "2024-05-04", "id": 5},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2024-06-01", "ultimo_dia": "2024-06-12", "dias_cal": 12, "dias_vac": 6, "pago": "0", "periodo_ini": "2024-06-01", "periodo_fin": "2024-06-12", "id": 6},
            {"novedad": "Ausencia", "fecha_inicial": "2024-07-01", "ultimo_dia": "2024-07-05", "dias_cal": 5, "dias_vac": 2, "pago": "150", "periodo_ini": "2024-07-01", "periodo_fin": "2024-07-05", "id": 7},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2024-08-01", "ultimo_dia": "2024-08-20", "dias_cal": 20, "dias_vac": 10, "pago": "0", "periodo_ini": "2024-08-01", "periodo_fin": "2024-08-20", "id": 8},
            {"novedad": "Ausencia", "fecha_inicial": "2024-09-01", "ultimo_dia": "2024-09-07", "dias_cal": 7, "dias_vac": 3, "pago": "200", "periodo_ini": "2024-09-01", "periodo_fin": "2024-09-07", "id": 9},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2024-10-01", "ultimo_dia": "2024-10-10", "dias_cal": 10, "dias_vac": 5, "pago": "0", "periodo_ini": "2024-10-01", "periodo_fin": "2024-10-10", "id": 10},
            {"novedad": "Ausencia", "fecha_inicial": "2024-11-01", "ultimo_dia": "2024-11-03", "dias_cal": 3, "dias_vac": 1, "pago": "110", "periodo_ini": "2024-11-01", "periodo_fin": "2024-11-03", "id": 11},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2024-12-01", "ultimo_dia": "2024-12-15", "dias_cal": 15, "dias_vac": 7, "pago": "0", "periodo_ini": "2024-12-01", "periodo_fin": "2024-12-15", "id": 12},
            {"novedad": "Ausencia", "fecha_inicial": "2025-01-01", "ultimo_dia": "2025-01-04", "dias_cal": 4, "dias_vac": 2, "pago": "130", "periodo_ini": "2025-01-01", "periodo_fin": "2025-01-04", "id": 13},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2025-02-01", "ultimo_dia": "2025-02-10", "dias_cal": 10, "dias_vac": 5, "pago": "0", "periodo_ini": "2025-02-01", "periodo_fin": "2025-02-10", "id": 14},
            {"novedad": "Ausencia", "fecha_inicial": "2025-03-01", "ultimo_dia": "2025-03-07", "dias_cal": 7, "dias_vac": 3, "pago": "180", "periodo_ini": "2025-03-01", "periodo_fin": "2025-03-07", "id": 15},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2025-04-01", "ultimo_dia": "2025-04-12", "dias_cal": 12, "dias_vac": 6, "pago": "0", "periodo_ini": "2025-04-01", "periodo_fin": "2025-04-12", "id": 16},
            {"novedad": "Ausencia", "fecha_inicial": "2025-05-01", "ultimo_dia": "2025-05-05", "dias_cal": 5, "dias_vac": 2, "pago": "150", "periodo_ini": "2025-05-01", "periodo_fin": "2025-05-05", "id": 17},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2025-06-01", "ultimo_dia": "2025-06-20", "dias_cal": 20, "dias_vac": 10, "pago": "0", "periodo_ini": "2025-06-01", "periodo_fin": "2025-06-20", "id": 18},
            {"novedad": "Ausencia", "fecha_inicial": "2025-07-01", "ultimo_dia": "2025-07-07", "dias_cal": 7, "dias_vac": 3, "pago": "200", "periodo_ini": "2025-07-01", "periodo_fin": "2025-07-07", "id": 19},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2025-08-01", "ultimo_dia": "2025-08-15", "dias_cal": 15, "dias_vac": 7, "pago": "0", "periodo_ini": "2025-08-01", "periodo_fin": "2025-08-15", "id": 20},
            {"novedad": "Ausencia", "fecha_inicial": "2025-09-01", "ultimo_dia": "2025-09-05", "dias_cal": 5, "dias_vac": 2, "pago": "160", "periodo_ini": "2025-09-01", "periodo_fin": "2025-09-05", "id": 21},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2025-10-01", "ultimo_dia": "2025-10-10", "dias_cal": 10, "dias_vac": 5, "pago": "0", "periodo_ini": "2025-10-01", "periodo_fin": "2025-10-10", "id": 22},
            {"novedad": "Ausencia", "fecha_inicial": "2025-11-01", "ultimo_dia": "2025-11-04", "dias_cal": 4, "dias_vac": 2, "pago": "140", "periodo_ini": "2025-11-01", "periodo_fin": "2025-11-04", "id": 23},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2025-12-01", "ultimo_dia": "2025-12-15", "dias_cal": 15, "dias_vac": 7, "pago": "0", "periodo_ini": "2025-12-01", "periodo_fin": "2025-12-15", "id": 24},
            {"novedad": "Ausencia", "fecha_inicial": "2026-01-01", "ultimo_dia": "2026-01-06", "dias_cal": 6, "dias_vac": 3, "pago": "170", "periodo_ini": "2026-01-01", "periodo_fin": "2026-01-06", "id": 25},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2026-02-01", "ultimo_dia": "2026-02-10", "dias_cal": 10, "dias_vac": 5, "pago": "0", "periodo_ini": "2026-02-01", "periodo_fin": "2026-02-10", "id": 26},
            {"novedad": "Ausencia", "fecha_inicial": "2026-03-01", "ultimo_dia": "2026-03-04", "dias_cal": 4, "dias_vac": 2, "pago": "120", "periodo_ini": "2026-03-01", "periodo_fin": "2026-03-04", "id": 27},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2026-04-01", "ultimo_dia": "2026-04-12", "dias_cal": 12, "dias_vac": 6, "pago": "0", "periodo_ini": "2026-04-01", "periodo_fin": "2026-04-12", "id": 28},
            {"novedad": "Ausencia", "fecha_inicial": "2026-05-01", "ultimo_dia": "2026-05-07", "dias_cal": 7, "dias_vac": 3, "pago": "180", "periodo_ini": "2026-05-01", "periodo_fin": "2026-05-07", "id": 29},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2026-06-01", "ultimo_dia": "2026-06-15", "dias_cal": 15, "dias_vac": 7, "pago": "0", "periodo_ini": "2026-06-01", "periodo_fin": "2026-06-15", "id": 30},
            {"novedad": "Ausencia", "fecha_inicial": "2026-07-01", "ultimo_dia": "2026-07-08", "dias_cal": 8, "dias_vac": 4, "pago": "210", "periodo_ini": "2026-07-01", "periodo_fin": "2026-07-08", "id": 31},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2026-08-01", "ultimo_dia": "2026-08-15", "dias_cal": 15, "dias_vac": 7, "pago": "0", "periodo_ini": "2026-08-01", "periodo_fin": "2026-08-15", "id": 32},
            {"novedad": "Ausencia", "fecha_inicial": "2026-09-01", "ultimo_dia": "2026-09-05", "dias_cal": 5, "dias_vac": 2, "pago": "160", "periodo_ini": "2026-09-01", "periodo_fin": "2026-09-05", "id": 33},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2026-10-01", "ultimo_dia": "2026-10-12", "dias_cal": 12, "dias_vac": 6, "pago": "0", "periodo_ini": "2026-10-01", "periodo_fin": "2026-10-12", "id": 34},
            {"novedad": "Ausencia", "fecha_inicial": "2026-11-01", "ultimo_dia": "2026-11-07", "dias_cal": 7, "dias_vac": 3, "pago": "190", "periodo_ini": "2026-11-01", "periodo_fin": "2026-11-07", "id": 35},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2026-12-01", "ultimo_dia": "2026-12-20", "dias_cal": 20, "dias_vac": 10, "pago": "0", "periodo_ini": "2026-12-01", "periodo_fin": "2026-12-20", "id": 36},
            {"novedad": "Ausencia", "fecha_inicial": "2027-01-01", "ultimo_dia": "2027-01-05", "dias_cal": 5, "dias_vac": 2, "pago": "140", "periodo_ini": "2027-01-01", "periodo_fin": "2027-01-05", "id": 37},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2027-02-01", "ultimo_dia": "2027-02-15", "dias_cal": 15, "dias_vac": 7, "pago": "0", "periodo_ini": "2027-02-01", "periodo_fin": "2027-02-15", "id": 38},
            {"novedad": "Ausencia", "fecha_inicial": "2027-03-01", "ultimo_dia": "2027-03-04", "dias_cal": 4, "dias_vac": 2, "pago": "130", "periodo_ini": "2027-03-01", "periodo_fin": "2027-03-04", "id": 39},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2027-04-01", "ultimo_dia": "2027-04-10", "dias_cal": 10, "dias_vac": 5, "pago": "0", "periodo_ini": "2027-04-01", "periodo_fin": "2027-04-10", "id": 40},
            {"novedad": "Ausencia", "fecha_inicial": "2027-05-01", "ultimo_dia": "2027-05-06", "dias_cal": 6, "dias_vac": 3, "pago": "160", "periodo_ini": "2027-05-01", "periodo_fin": "2027-05-06", "id": 41},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2027-06-01", "ultimo_dia": "2027-06-15", "dias_cal": 15, "dias_vac": 7, "pago": "0", "periodo_ini": "2027-06-01", "periodo_fin": "2027-06-15", "id": 42},
            {"novedad": "Ausencia", "fecha_inicial": "2027-07-01", "ultimo_dia": "2027-07-08", "dias_cal": 8, "dias_vac": 4, "pago": "200", "periodo_ini": "2027-07-01", "periodo_fin": "2027-07-08", "id": 43},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2027-08-01", "ultimo_dia": "2027-08-20", "dias_cal": 20, "dias_vac": 10, "pago": "0", "periodo_ini": "2027-08-01", "periodo_fin": "2027-08-20", "id": 44},
            {"novedad": "Ausencia", "fecha_inicial": "2027-09-01", "ultimo_dia": "2027-09-07", "dias_cal": 7, "dias_vac": 3, "pago": "190", "periodo_ini": "2027-09-01", "periodo_fin": "2027-09-07", "id": 45},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2027-10-01", "ultimo_dia": "2027-10-15", "dias_cal": 15, "dias_vac": 7, "pago": "0", "periodo_ini": "2027-10-01", "periodo_fin": "2027-10-15", "id": 46},
            {"novedad": "Ausencia", "fecha_inicial": "2027-11-01", "ultimo_dia": "2027-11-05", "dias_cal": 5, "dias_vac": 2, "pago": "150", "periodo_ini": "2027-11-01", "periodo_fin": "2027-11-05", "id": 47},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2027-12-01", "ultimo_dia": "2027-12-20", "dias_cal": 20, "dias_vac": 10, "pago": "0", "periodo_ini": "2027-12-01", "periodo_fin": "2027-12-20", "id": 48},
            {"novedad": "Ausencia", "fecha_inicial": "2028-01-01", "ultimo_dia": "2028-01-04", "dias_cal": 4, "dias_vac": 2, "pago": "130", "periodo_ini": "2028-01-01", "periodo_fin": "2028-01-04", "id": 49},
            {"novedad": "Licencia No Remunerada", "fecha_inicial": "2028-02-01", "ultimo_dia": "2028-02-15", "dias_cal": 15, "dias_vac": 7, "pago": "0", "periodo_ini": "2028-02-01", "periodo_fin": "2028-02-15", "id": 50}
        ]


    return JsonResponse(data, safe=False)

