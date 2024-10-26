from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q
from apps.employees.forms.vacation_request_form import EmpVacacionesForm
from apps.common.models import EmpVacaciones, Vacaciones, Contratos, Festivos, Contratosemp , Tipoavacaus
from datetime import timedelta, datetime, date
from apps.components.utils import calcular_dias_360
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.components.mail import send_template_email
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from apps.components.decorators import  role_required
from apps.components.humani import format_decimal


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
@role_required('employee')
def vacation_request_function(request):
    usuario = request.session.get('usuario', {})
    ide = usuario['idempleado']
    nombre_empleado = Contratosemp.objects.get(idempleado=ide).pnombre
    contrato = Contratos.objects.filter(idempleado=ide, estadocontrato=1).first()
    idc = contrato.idcontrato if contrato else None

    contratof = Contratos.objects.get(idcontrato=idc)
    inicio_contrato = contratof.fechainiciocontrato.strftime('%Y-%m-%d')

    form = EmpVacacionesForm(idempleado=ide)

    if request.method == 'POST' :
        form = EmpVacacionesForm(request.POST)
        if form.is_valid() :
            tipovac_obj = form.cleaned_data.get('tipovac')
            tipovac = str(tipovac_obj.tipovac)
            cuentasabados = form.cleaned_data.get('cuentasabados')
            comentarios = form.cleaned_data.get('comentarios')
            fechainicialvac = form.cleaned_data.get('fechainicialvac')
            fechafinalvac = form.cleaned_data.get('fechafinalvac')

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
            vacation_request.comentarios = comentarios
            vacation_request.save()

        email_type = 'vacations'
        context = {
            'nombre_empleado': nombre_empleado,
            'tipovac_obj': tipovac_obj,
            'diasvac': diasvac,
            'comentarios': comentarios,
            'tipovac': tipovac,
        }
        if fechainicialvac:
            context['fechainicialvac'] = fechainicialvac
        if fechafinalvac:
            context['fechafinalvac'] = fechafinalvac

        subject = 'Solicitud de Vacaciones / Licencias'
        recipient_list = ['catalina@matchlink.co'] ## cambiar este correo por una variable que contenga el email del empleado y con copia a gghh

        if send_template_email(email_type, context, subject, recipient_list):
            pass
        else:
            messages.error(request, 'Error en el procesamiento de la solicitud')

        messages.success(request, 'La solicitud de Vacaciones/Licencias ha sido enviada correctamente.')

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
        'vacaciones_fecha': format_decimal(vacaciones_fecha),
    }

    return render(request, 'employees/vacations_request.html', context)


global_dato = None 

@csrf_exempt
def my_get_view(request):
    global global_dato
    
    if request.method == 'GET':
        dato = request.GET.get('dato')
        solicitud =  get_object_or_404(EmpVacaciones, pk=dato)
        global_dato = dato
        
        if solicitud.cuentasabados == 1:
            nom_cuentasabados = 'Si'
        else:
            nom_cuentasabados = 'No'
        
        response_data = {
            'data': {
                'idcontrato':solicitud.idcontrato.idcontrato,
                'tipovac':solicitud.tipovac.idvac,
                'nombre_tipovac': solicitud.tipovac.nombrevacaus,
                'fechainicialvac':solicitud.fechainicialvac,
                'fechafinalvac':solicitud.fechafinalvac,
                'diasvac':solicitud.diasvac,
                'comentarios':solicitud.comentarios,
                'si': 1 if solicitud.cuentasabados else 0,
                
                'tipovac2': str(solicitud.tipovac.idvac),
                'fecha': solicitud.fecha_hora.strftime('%d-%m-%Y'),
                'cuentasabados': 'Si'if nom_cuentasabados else 'No',
                'dias_habiles': solicitud.diasvac,
                'dias_calendario': solicitud.diascalendario,
                'fecha_inicial': solicitud.fechainicialvac.strftime('%d-%m-%Y') if solicitud.fechainicialvac else '',
                'fecha_final': solicitud.fechafinalvac.strftime('%d-%m-%Y') if solicitud.fechafinalvac else '',
                'estado': solicitud.estado,
                'comentarios2': solicitud.comentarios2,
                
            }
        }

        return JsonResponse(response_data)
    
    if request.method == 'POST' :
        
        tipovac_obj = request.POST.get('tipovac')
        tipovac = str(tipovac_obj) if tipovac_obj else None
        cuentasabados = request.POST.get('cuentasabados')
        comentarios = request.POST.get('comentarios')
        fechainicialvac = request.POST.get('fechainicialvac')
        fechafinalvac = request.POST.get('fechafinalvac')
        diasvac = request.POST.get('diasvac')
        ghost = global_dato
        
        fechainicialvac = datetime.strptime(fechainicialvac, '%Y-%m-%d')  # Convert string to datetime
        fechafinalvac = datetime.strptime(fechafinalvac, '%Y-%m-%d') 
        
        solicitud =  get_object_or_404(EmpVacaciones, pk=ghost)
        tipo = get_object_or_404(Tipoavacaus, tipovac=tipovac)

        if tipovac == '2':
            diascalendario = diasvac
        else:
            if fechainicialvac and fechafinalvac:
                diascalendario = (fechafinalvac - fechainicialvac).days + 1
                dias_festivos = Festivos.objects.values_list('dia', flat=True)
                cuentasabados = int(cuentasabados)
                diasvac = calcular_dias_habiles(fechainicialvac, fechafinalvac, cuentasabados, dias_festivos)
        
        solicitud.ip_usuario = get_client_ip(request)
        solicitud.tipovac  =  tipo
        solicitud.fechainicialvac  = fechainicialvac
        solicitud.fechafinalvac  = fechafinalvac
        solicitud.diascalendario = diascalendario
        solicitud.diasvac = diasvac
        solicitud.cuentasabados  = cuentasabados
        solicitud.comentarios  = comentarios
        solicitud.save()
        
        messages.success(request, 'La solicitud de Vacaciones/Licencias ha sido actualizada correctamente.')
        return redirect('employees:form_vac')
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)







