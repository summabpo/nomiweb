from django.shortcuts import render, redirect
from django.db.models import Sum
from apps.employees.forms.vacation_request_form import EmpVacacionesForm
from apps.employees.models import EmpVacaciones, Vacaciones, Contratos, Festivos
from datetime import timedelta, datetime, date
from apps.components.utils import calcular_dias_360

def calcular_dias_habiles(fechainicialvac, fechafinalvac, cuentasabados, dias_festivos):
    """
    Calcula los días hábiles entre dos fechas.
    Si cuentasabados es 1, incluye los sábados. Los domingos nunca se cuentan.
    Los días festivos también se excluyen.
    """
    total_dias = 0
    dia_actual = fechainicialvac

    while dia_actual <= fechafinalvac:
        if (dia_actual.weekday() != 6 and dia_actual not in dias_festivos) and (dia_actual.weekday() != 5 or cuentasabados == 1):
            total_dias += 1
        dia_actual += timedelta(days=1)
    return total_dias

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def vacation_request_function(request):
    ide = request.session.get('idempleado')
    contrato = Contratos.objects.filter(idempleado=ide, estadocontrato=1).first()
    idc = contrato.idcontrato if contrato else None

    contrato = Contratos.objects.get(idcontrato=idc)
    inicio_contrato = contrato.fechainiciocontrato.strftime('%Y-%m-%d')

    form = EmpVacacionesForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        tipovac_obj = form.cleaned_data.get('tipovac')
        tipovac = str(tipovac_obj.tipovac)

        if tipovac == '2':
            diascalendario = form.cleaned_data.get('diascalendario')
            diasvac = diascalendario
        else:
            fechainicialvac = form.cleaned_data.get('fechainicialvac')
            fechafinalvac = form.cleaned_data.get('fechafinalvac')
            cuentasabados = form.cleaned_data.get('cuentasabados')

            if fechainicialvac and fechafinalvac:
                diascalendario = (fechafinalvac - fechainicialvac).days + 1
                dias_festivos = Festivos.objects.values_list('dia', flat=True)
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

    dias_vacaciones = Vacaciones.objects.filter(idcontrato=idc).aggregate(Sum('diasvac'))['diasvac__sum'] or 0

    fecha_hoy = date.today().strftime('%Y-%m-%d')
    dias_trabajados = calcular_dias_360(inicio_contrato, fecha_hoy)
    vacaciones_fecha = round(dias_trabajados * 15/360,2)

    vacation_list = EmpVacaciones.objects.filter(idcontrato=idc).order_by('-id_sol_vac')

    context = {
        'form': form,
        'dias_vacaciones': dias_vacaciones,
        'vacation_list': vacation_list,
        'idc': idc,
        'vacaciones_fecha': vacaciones_fecha,
    }

    return render(request, 'employees/vacations_request.html', context)
