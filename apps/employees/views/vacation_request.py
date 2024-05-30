from django.shortcuts import render, redirect
from django.db.models import Sum
from apps.employees.forms.vacation_request_form import EmpVacacionesForm
from apps.employees.models import EmpVacaciones, Vacaciones, Contratos, Festivos
from datetime import timedelta, datetime


def calcular_dias_habiles(fechainicialvac, fechafinalvac, cuentasabados):
    """
    Calcula los días hábiles entre dos fechas.
    Si cuentasabados es 1, incluye los sábados. Los domingos nunca se cuentan.
    Los días festivos también se excluyen.
    """
    total_dias = 0
    dia_actual = fechainicialvac

    # Obtener todos los días festivos
    dias_festivos = Festivos.objects.values_list('dia', flat=True)

    while dia_actual <= fechafinalvac:
        # Si el día actual no es domingo (6) y no es festivo
        # O es sábado (5) y cuentasabados es 1 y no es festivo
        if (dia_actual.weekday() != 6 and dia_actual not in dias_festivos) and (dia_actual.weekday() != 5 or cuentasabados == 1):
            total_dias += 1
        dia_actual += timedelta(days=1)
    return total_dias

def vacation_request_function(request):
    ide = request.session.get('idempleado')

    contrato = Contratos.objects.filter(idempleado=ide, estadocontrato=1).first()
    if contrato:
        idc = contrato.idcontrato
    else:
        idc = None

    form = EmpVacacionesForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        tipovac_obj = form.cleaned_data.get('tipovac')
        tipovac = str(tipovac_obj.tipovac)

        if tipovac == '2':
            diascalendario = form.cleaned_data.get('diascalendario')  # Usa el valor manual ingresado
            diasvac = diascalendario
        else:
            fechainicialvac = form.cleaned_data.get('fechainicialvac')
            fechafinalvac = form.cleaned_data.get('fechafinalvac')
            cuentasabados = form.cleaned_data.get('cuentasabados')

            if fechainicialvac and fechafinalvac:
                diascalendario = (fechafinalvac - fechainicialvac).days + 1
                diasvac = calcular_dias_habiles(fechainicialvac, fechafinalvac, cuentasabados)
            else:
                form.add_error(None, 'Fechas de inicio y fin son requeridas.')
                return render(request, 'employees/vacations_request.html', {'form': form})

        vacation_request = form.save(commit=False)
        vacation_request.estado = 1
        vacation_request.fecha_hora = datetime.now()
        vacation_request.diascalendario = diascalendario
        vacation_request.diasvac = diasvac
        vacation_request.save()
        return redirect('employees:form_vac')

    dias_vacaciones = Vacaciones.objects.filter(idcontrato=idc).aggregate(Sum('diasvac'))['diasvac__sum'] or 0

    vacation_list = EmpVacaciones.objects.filter(idcontrato=idc).order_by('-id_sol_vac')

    context = {
        'form': form,
        'dias_vacaciones': dias_vacaciones,
        'vacation_list': vacation_list,
        'idc': idc,
    }

    return render(request, 'employees/vacations_request.html', context)
