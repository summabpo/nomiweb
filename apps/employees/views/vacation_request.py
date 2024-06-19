from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q
from apps.employees.forms.vacation_request_form import EmpVacacionesForm
from apps.employees.models import EmpVacaciones, Vacaciones, Contratos, Festivos
from datetime import timedelta, datetime, date
from apps.components.utils import calcular_dias_360
from apps.components.decorators import custom_permission
from django.contrib.auth.decorators import login_required



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


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


@login_required
@custom_permission('employees')
def vacation_request_function(request):
    ide = request.session.get('idempleado')
    contrato = Contratos.objects.filter(idempleado=ide, estadocontrato=1).first()
    idc = contrato.idcontrato if contrato else None

    contratof = Contratos.objects.get(idcontrato=idc)
    inicio_contrato = contratof.fechainiciocontrato.strftime('%Y-%m-%d')

    form = EmpVacacionesForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        tipovac_obj = form.cleaned_data.get('tipovac')
        tipovac = str(tipovac_obj.tipovac)
        cuentasabados = form.cleaned_data.get('cuentasabados')

        if tipovac == '2':
            diasvac = form.cleaned_data.get('diasvac')
            diascalendario = diasvac
        else:
            fechainicialvac = form.cleaned_data.get('fechainicialvac')
            fechafinalvac = form.cleaned_data.get('fechafinalvac')
            cuentasabados = form.cleaned_data.get('cuentasabados')

            if fechainicialvac and fechafinalvac:
                diascalendario = (fechafinalvac - fechainicialvac).days + 1
                dias_festivos = Festivos.objects.values_list('dia', flat=True)
                cuentasabados = int(cuentasabados)
                diasvac = calcular_dias_habiles(fechainicialvac, fechafinalvac, cuentasabados, dias_festivos)
            else:
                form.add_error(None, 'Fechas de inicio y fin son requeridas.')
                return render(request, 'employees/vacations_request.html', {'form': form})

        vacation_request = form.save(commit=False)
        vacation_request.estado = 1
        vacation_request.ip_usuario = get_client_ip(request)
        vacation_request.fecha_hora = datetime.now()
        vacation_request.diascalendario = diascalendario
        vacation_request.diasvac = diasvac
        vacation_request.save()

        return redirect('employees:form_vac')

    dias_vacaciones = Vacaciones.objects.filter(idcontrato=idc).filter(Q(tipovac='1') | Q(tipovac='2')).aggregate(Sum('diasvac'))['diasvac__sum'] or 0
    dias_licencia = Vacaciones.objects.filter(idcontrato=idc).filter(Q(tipovac='3') | Q(tipovac='4')).aggregate(Sum('diasvac'))['diasvac__sum'] or 0
    fecha_hoy = date.today().strftime('%Y-%m-%d')
    dias_trabajados = calcular_dias_360(inicio_contrato, fecha_hoy)
    periodos_completos = round(dias_trabajados/360)
    vacaciones_fecha = round(dias_trabajados * 15/360,2) - dias_vacaciones

    vacation_list = EmpVacaciones.objects.filter(idcontrato=idc).order_by('-id_sol_vac')


    context = {
        'form': form,
        'dias_vacaciones': dias_vacaciones,
        'dias_licencia': dias_licencia,
        'vacation_list': vacation_list,
        'periodos_completos': periodos_completos,
        'idc': idc,
        'vacaciones_fecha': vacaciones_fecha,
    }

    return render(request, 'employees/vacations_request.html', context)

@login_required
@custom_permission('employees')
def vacation_detail_modal(request, pk):
    vacation = get_object_or_404(EmpVacaciones, pk=pk)

    nom_cuentasabados = 'No'

    if vacation.cuentasabados == 1:
        nom_cuentasabados = 'Si'
    else:
        nom_cuentasabados = 'No'

    context = {
        'tipovac': str(vacation.tipovac.tipovac),
        'nombre_tipovac': vacation.tipovac.nombrevacaus,
        'fecha': vacation.fecha_hora.strftime('%d-%m-%Y'),
        'cuentasabados': nom_cuentasabados,
        'dias_habiles': vacation.diasvac,
        'dias_calendario': vacation.diascalendario,
        'fecha_inicial': vacation.fechainicialvac.strftime('%d-%m-%Y') if vacation.fechainicialvac else '',
        'fecha_final': vacation.fechafinalvac.strftime('%d-%m-%Y') if vacation.fechafinalvac else '',
        'estado': vacation.estado,
        'comentarios': vacation.comentarios,
        'comentarios2': vacation.comentarios2,
    }
    return render(request, 'employees/vacation_detail_modal.html', context)