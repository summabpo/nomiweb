from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.filterform import FilterForm 
from apps.components.decorators import  role_required
from apps.companies.models import Contratosemp , Vacaciones ,Contratos 
from apps.employees.models import EmpVacaciones, Vacaciones, Contratos, Festivos, Contratosemp , Tipoavacaus
from django.db.models.functions import Coalesce
from django.db.models import Value
from django.db.models import CharField, DateField
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Q
from datetime import timedelta, datetime, date
from django.db.models.functions import Coalesce



def calcular_dias_habiles(fechainicialvac, fechafinalvac, cuentasabados, dias_festivos):
    """
    Calcula los días hábiles entre dos fechas.
    Si cuentasabados es 1, incluye los sábados. Los domingos nunca se cuentan.
    Los días festivos también se excluyen.
    """
    total_dias = 0
    dia_actual = fechainicialvac

    while dia_actual <= fechafinalvac:
        if (dia_actual.weekday() != 6) and (dia_actual not in dias_festivos) and (dia_actual.weekday() != 5 or cuentasabados == 1):
            total_dias += 1
        dia_actual += timedelta(days=1)
    return total_dias


def calcular_dias_360(fechainicial, fechafinal):
    #Calcula la diferencia entre dos fechas considerando todos los meses con 30 dias.

    fechainicial = datetime.strptime(fechainicial, "%Y-%m-%d")
    fechafinal = datetime.strptime(fechafinal, "%Y-%m-%d")

    anios_diferencia = fechafinal.year - fechainicial.year
    meses_diferencia = fechafinal.month - fechainicial.month
    dias_diferencia = fechafinal.day - fechainicial.day

    dias_totales_360 = (anios_diferencia * 360) + (meses_diferencia * 30) + dias_diferencia

    return dias_totales_360

def vacation_request(request):
    # Obtener la lista de empleados
    vacaciones = EmpVacaciones.objects.all().order_by('-id_sol_vac').values('idcontrato__idempleado__docidentidad', 'idcontrato__idempleado__sapellido', 'idcontrato__idempleado__papellido', 
                'idcontrato__idempleado__pnombre', 'idcontrato__idempleado__snombre', 'idcontrato__idempleado__idempleado', 
                'tipovac__nombrevacaus','fechainicialvac', 'fechafinalvac','estado','idcontrato__idcontrato','id_sol_vac')

    context ={ 
            'vacaciones' : vacaciones,
        }
    
    return render(request, './companies/vacation_request.html', context)


@csrf_exempt
def get_vacation_details(request):
    if request.method == 'GET':
        dato = request.GET.get('dato')
        
        data = EmpVacaciones.objects.get(id_sol_vac = dato )
        
        
        vacaciones_data = Vacaciones.objects.filter(idcontrato=data.idcontrato.idcontrato).filter(
            Q(tipovac='1') | Q(tipovac='2') | Q(tipovac='3') | Q(tipovac='4')
        ).aggregate(
            dias_vacaciones=Coalesce(Sum('diasvac', filter=Q(tipovac__in=['1', '2'])), 0),
            dias_licencia=Coalesce(Sum('diasvac', filter=Q(tipovac__in=['3', '4'])), 0)
        )

        # Asigna los valores a variables con solo dos decimales
        dias_vacaciones = round(vacaciones_data['dias_vacaciones'], 2)
        dias_licencia = round(vacaciones_data['dias_licencia'], 2)

        # Calcula los días trabajados y periodos completos
        fecha_hoy = date.today().strftime('%Y-%m-%d')
        dias_trabajados = calcular_dias_360(str(data.idcontrato.fechainiciocontrato), fecha_hoy)
        periodos_completos = round(dias_trabajados / 360)

        # Calcula las vacaciones restantes
        vacaciones_fecha = round(dias_trabajados * 15 / 360, 2) - dias_vacaciones

        vacaciones_fecha = round(vacaciones_fecha, 2)
        
        if data.cuentasabados == 1:
            nom_cuentasabados = 'Si'
        else:
            nom_cuentasabados = 'No'
        
        
        response ={
            'status':'success',
            'data': {
                'id_cont': data.idcontrato.idcontrato,
                'id_vac' : dato,
                'vac_taken' : dias_vacaciones,
                'vac_periods':periodos_completos,
                'vac_sum':vacaciones_fecha,
                'vac_licenses':dias_licencia,
                'status':data.estado,
                
                ## data vacation 
                'tipovac': str(data.tipovac.tipovac),
                'nombre_tipovac': data.tipovac.nombrevacaus,
                'fecha': data.fecha_hora.strftime('%d-%m-%Y'),
                'cuentasabados': nom_cuentasabados,
                'dias_habiles': data.diasvac,
                'dias_calendario': data.diascalendario,
                'fecha_inicial': data.fechainicialvac.strftime('%d-%m-%Y') if data.fechainicialvac else '',
                'fecha_final': data.fechafinalvac.strftime('%d-%m-%Y') if data.fechafinalvac else '',
                'estado': data.estado,
                'comentarios2': data.comentarios2,
                'comentarios':data.comentarios,
                
                
            }
        }
        return JsonResponse(response, safe=False) 
    
    return JsonResponse({'message': 'Metodo no permitido', 'status': 'error'}, status=405)




@csrf_exempt
def get_vacation_acction(request):
    try:
        if request.method == 'POST':
            option = request.POST.get('loanSelect')
            comments = request.POST.get('comments')
            vacation = request.POST.get('vacationDetails') 
            
            data = EmpVacaciones.objects.get(id_sol_vac = vacation )
            
            if option == '1':
                status = '2'
                response_message = "Solicitud aprobada."
            elif option == '2':
                status = '3'
                response_message = "Solicitud rechazada."
            elif option == '3':
                status = '1'
                response_message = "Solicitud en estado pendiente."
            else:
                response_message = "Acción no válida."
                
            data.estado = status
            data.comentarios2 = comments
            data.save()
            
            return JsonResponse({'success': True, 'message': 'Solicitud procesada correctamente.'})
    
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Ocurrio Un error inesperado '})
    
    return JsonResponse({'message': 'Metodo no permitido', 'status': 'error'}, status=405)


""" 
<!--begin::Toggle-->
<button type="button" class="btn btn-light-info rotate" data-kt-menu-trigger="click" data-kt-menu-placement="bottom-start" data-kt-menu-offset="0, 0">
    <i class="fa-solid fa-list-check fs-3 "></i>
    Gestionar
</button>
<!--end::Toggle-->

<!--begin::Menu-->
<div class="menu menu-sub menu-sub-dropdown menu-column menu-rounded menu-gray-800 menu-state-bg-light-primary fw-semibold w-auto min-w-200 mw-300px" data-kt-menu="true">
    <!--begin::Menu item-->
    <div class="menu-item px-3">
        <a href="#" class="menu-link px-3 menu-state-bg-info" data-vacation="{{ vacacion.id_sol_vac }}" data-action="approve" onclick="sendAction(this)">
            Aprobar
        </a>
    </div>
    <!--end::Menu item-->

    <!--begin::Menu item-->
    <div class="menu-item px-3">
        <a href="#" class="menu-link px-3" data-vacation="{{ vacacion.id_sol_vac }}" data-action="reject" onclick="sendAction(this)">
            Rechazar
        </a>
    </div>
    <!--end::Menu item-->

    <!--begin::Menu item-->
    <div class="menu-item px-3">
        <a href="#" class="menu-link px-3" data-vacation="{{ vacacion.id_sol_vac }}" data-action="pending" onclick="sendAction(this)">
            Pendiente
        </a>
    </div>
    <!--end::Menu item-->
    <!--begin::Menu separator-->
    <div class="separator mt-3 opacity-75"></div>
    <!--end::Menu separator-->
</div>
<!--end::Menu-->


"""

