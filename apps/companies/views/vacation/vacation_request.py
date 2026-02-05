from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.filterform import FilterForm 
from apps.components.decorators import  role_required
from apps.common.models  import EmpVacaciones, Vacaciones, Contratos, Festivos, Contratosemp , Tipoavacaus , Crearnomina
from django.db.models.functions import Coalesce
from django.db.models import Value
from django.db.models import CharField, DateField
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Q
from datetime import timedelta, datetime, date
from django.db.models.functions import Coalesce
from apps.components.mail import send_template_email
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
import pandas as pd

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

@login_required
@role_required('company','accountant')
def vacation_request(request):
    """
    Vista para listar las solicitudes de vacaciones realizadas por los empleados de la empresa.

    Esta vista permite a usuarios con el rol 'company' o 'accountant' consultar todas las solicitudes de vacaciones 
    registradas por empleados asociados a la empresa actual. Se muestran los datos básicos del empleado, tipo de 
    vacación, fechas y estado de la solicitud.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP con la sesión del usuario autenticado.

    Returns
    -------
    HttpResponse
        Renderiza el template 'companies/vacation_request.html' con el listado de solicitudes de vacaciones.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol 'company' o 'accountant'.
    Las solicitudes se ordenan por el ID de solicitud de vacaciones en orden descendente.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    # Obtener la lista de solicitudes de vacaciones
    vacaciones = (
        EmpVacaciones.objects
        .filter(idcontrato__id_empresa__idempresa=idempresa)
        .order_by('-id_sol_vac')
        .values(
            'idcontrato__idempleado__docidentidad',
            'idcontrato__idempleado__sapellido',
            'idcontrato__idempleado__papellido',
            'idcontrato__idempleado__pnombre',
            'idcontrato__idempleado__snombre',
            'idcontrato__idempleado__idempleado',
            'tipovac__nombrevacaus',
            'fechainicialvac',
            'fechafinalvac',
            'estado',
            'idcontrato__idcontrato',
            'id_sol_vac'
        )
    )

    # Limpiar los campos de texto (evita mostrar "no data" o None)
    for vac in vacaciones:
        for campo in [
            'idcontrato__idempleado__pnombre',
            'idcontrato__idempleado__snombre',
            'idcontrato__idempleado__papellido',
            'idcontrato__idempleado__sapellido'
        ]:
            valor = vac.get(campo)
            if valor is None or str(valor).strip().lower() == 'no data':
                vac[campo] = ''

    context = {
        'vacaciones': vacaciones,
    }
    
    return render(request, './companies/vacation_request.html', context)


def intentar_fecha(valor):
    if isinstance(valor, str) and '/' in valor:
        try:
            return datetime.strptime(valor, '%d/%m/%Y').date()
        except:
            return valor
    return valor

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


@login_required
@role_required('company', 'accountant')
def vacation_request_file_upload(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    #nomina = Crearnomina.objects.get( idnomina = id)
    
    
    if request.method == 'POST' and request.FILES.get('file'):
        errors = []
        file = request.FILES['file']

        try:
            df = pd.read_csv(file, sep=';', encoding='utf-8')

            registros_validados = []  # aquí guardaremos las filas validadas para luego insertarlas
            df = df.dropna(how='all')
            
            # FASE 1: Validación
            for idx, fila in df.iterrows():
                fila_errors = []

                try:
                    ID_CONTRATO     = fila['ID_CONTRATO']
                    COD_CONCEPTO    = fila['COD_CONCEPTO']
                    F_INICIO        = intentar_fecha(fila['F_INICIO'])
                    F_FIN           = intentar_fecha(fila['F_FIN'])
                    TRABAJA_SABADO  = fila['TRABAJA_SABADO']
                    PER_INICIO      = intentar_fecha(fila['PER_INICIO'])
                    PER_FINAL       = intentar_fecha(fila['PER_FINAL'])
                    TIPO_VAC        = fila['TIPO_VAC']
                    FECHA_PAGO      = intentar_fecha(fila['FECHA_PAGO'])
                    ID_NOMINA       = fila['ID_NOMINA']
                except Exception as e:
                    fila_errors.append(f"Error al leer datos → {str(e)}")

                if not ID_CONTRATO:
                    fila_errors.append("ID_CONTRATO vacío")
                if COD_CONCEPTO not in [24, 32, 81, 80, 82, 83, 31, 30]:
                    fila_errors.append("Código de concepto inválido")
                if not F_INICIO or not F_FIN:
                    fila_errors.append("Fecha de inicio o fin inválida")
                if TRABAJA_SABADO not in [0, 1]:
                    fila_errors.append("Valor de trabaja_sabado inválido (solo 0 o 1)")
                if not PER_INICIO or not PER_FINAL:
                    fila_errors.append("Periodo inicio o final inválido")
                if TIPO_VAC not in [1, 2, 3, 4, 5]:
                    fila_errors.append("Tipo de vacaciones inválido")

                try:
                    contrato = Contratos.objects.get(idcontrato=ID_CONTRATO, id_empresa=idempresa)
                except Contratos.DoesNotExist:
                    fila_errors.append(f"Contrato {ID_CONTRATO} no encontrado")

                try:
                    nomina = Crearnomina.objects.get(idnomina=ID_NOMINA)
                except Crearnomina.DoesNotExist:
                    fila_errors.append(f"Nómina {ID_NOMINA} no encontrada")

                try:
                    tipo = Tipoavacaus.objects.get(idvac=TIPO_VAC)
                except Tipoavacaus.DoesNotExist:
                    fila_errors.append(f"Tipo de vacaciones {TIPO_VAC} no encontrado")

                if fila_errors:
                    errors.append(f"Fila {idx+1}: " + "; ".join(fila_errors))
                else:
                    registros_validados.append({
                        'contrato': contrato,
                        'F_INICIO': F_INICIO,
                        'nomina': nomina,
                        'TRABAJA_SABADO': TRABAJA_SABADO,
                        'tipo': tipo,
                        'PER_INICIO': PER_INICIO,
                        'PER_FINAL': PER_FINAL,
                        'FECHA_PAGO': FECHA_PAGO
                    })

            # Si hubo errores, mostrar y no guardar nada
            if errors:
                return render(request, './companies/partials/disability_upload_errors.html', {
                    'errors': errors
                })

            # FASE 2: Guardado (solo si no hubo errores)
            for reg in registros_validados:
                Vacaciones.objects.create(
                    idcontrato=reg['contrato'],
                    fechainicialvac=reg['F_INICIO'],
                    #idnomina=reg['nomina'],
                    cuentasabados=reg['TRABAJA_SABADO'],
                    tipovac=reg['tipo'],
                    perinicio=reg['PER_INICIO'],
                    perfinal=reg['PER_FINAL'],
                    fechapago=reg['FECHA_PAGO'],
                )

        except Exception as e:
            print(e)
            errors.append(f"Error general al procesar el archivo")

        if errors:
            return render(request, './companies/partials/disability_upload_errors.html', {
                'errors': errors
            })

        return render(request, 'companies/partials/success_vacation.html')


    return render(request, './companies/partials/vacation_request_file_upload.html')





@login_required
@role_required('company','accountant')
@csrf_exempt
def get_vacation_details(request):
    """
    Vista que retorna los detalles de una solicitud de vacaciones en formato JSON, utilizada para mostrar información detallada en el frontend.

    Esta vista se accede mediante petición GET y retorna información detallada de una solicitud de vacaciones, incluyendo:
    - Datos del contrato y del empleado
    - Días de vacaciones y licencias disfrutadas
    - Cálculo de periodos completos según la fecha de ingreso
    - Días restantes de vacaciones
    - Datos específicos de la solicitud seleccionada

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP con el parámetro GET 'dato', que contiene el ID de la solicitud de vacaciones.

    Returns
    -------
    JsonResponse
        Devuelve un JSON con todos los detalles relacionados con la solicitud de vacaciones si es GET; 
        en caso contrario, devuelve un error 405.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol 'company' o 'accountant'.
    Usa la función personalizada `calcular_dias_360` para determinar la cantidad de días trabajados desde la fecha de inicio del contrato.
    La respuesta contiene datos numéricos redondeados a dos decimales y datos de fecha en formato DD-MM-YYYY.
    """

    if request.method == 'GET':
        dato = request.GET.get('dato')
        
        data = EmpVacaciones.objects.get(id_sol_vac = dato )
        
        
        vacaciones_data = Vacaciones.objects.filter(idcontrato=data.idcontrato.idcontrato).filter(
            Q(tipovac='1') | Q(tipovac='2') | Q(tipovac='3') | Q(tipovac='4')
        ).aggregate(
            dias_vacaciones=Coalesce(Sum('diasvac', filter=Q(tipovac__in=['1', '2'])), 0),
            dias_licencia=Coalesce(Sum('diasvac', filter=Q(tipovac__in=['3', '4'])), 0)
        )

        empleado = f"{vacaciones_data.get('idcontrato__idempleado__papellido', '')} {vacaciones_data.get('idcontrato__idempleado__sapellido', '')} {vacaciones_data.get('idcontrato__idempleado__pnombre', '')} {vacaciones_data.get('idcontrato__idempleado__snombre', '')}"

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
                'empleado': empleado,
                
                ## data vacation 
                'tipovac': str(data.tipovac.idvac),
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



@login_required
@role_required('company','accountant')
@csrf_exempt
def get_vacation_acction(request):
    """
    Vista que permite cambiar el estado de una solicitud de vacaciones y notificar al empleado por correo electrónico.

    Esta vista se accede mediante POST y permite a un usuario con rol 'company' o 'accountant':
    - Aprobar una solicitud de vacaciones (estado 2)
    - Rechazar una solicitud de vacaciones (estado 3)
    - Marcarla como pendiente (estado 1)
    Además, se guarda un comentario de respuesta y se envía un correo de notificación al empleado implicado.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP con los siguientes campos POST:
        - 'loanSelect': Opción elegida (1=Aprobar, 2=Rechazar, 3=Pendiente)
        - 'comments': Comentarios o razones para la acción
        - 'vacationDetails': ID de la solicitud de vacaciones a actualizar

    Returns
    -------
    JsonResponse
        Devuelve una respuesta JSON con el resultado de la operación:
        - `success=True` si se guardó el estado y se envió el correo correctamente
        - `success=False` si hubo errores (por ejemplo, al enviar el correo)
        - Status HTTP 405 si el método HTTP no es POST

    Notes
    -----
    - El campo `estado` en el modelo `EmpVacaciones` se actualiza según la opción seleccionada.
    - Se envía un correo al empleado usando la función `send_template_email`, con un mensaje adaptado al estado.
    - La lista de destinatarios incluye un correo de prueba ('mikepruebas@yopmail.com') y el correo del empleado.
    - En caso de excepción, se responde con un mensaje genérico de error.
    """

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
        email_subject = 'Notificación del Estado de su Solicitud de Vacaciones'
        recipient_list = ['mikepruebas@yopmail.com'] 
        #recipient_list = ['mikepruebas@yopmail.com',data.idcontrato.idempleado.email] 
        




        Vacaciones.objects.create(
            idcontrato = data.idcontrato,
            fechainicialvac = data.fechainicialvac , 
            ultimodiavac = data.fechafinalvac , 
            diascalendario = data.diascalendario , 
            diasvac = data.diasvac,
            pagovac = data.idcontrato.salario,
            basepago = data.idcontrato.salario,
            tipovac = data.tipovac,
            idvacmaster = data.id_sol_vac , 
        )



        
        
        if status == '2':
            
            if data.tipovac.idvac == 1:
                mensaje1 = f'Su solicitud ha sido '
                mensaje2 = 'Aprobada. '
                mensaje3 = f'Disfrute de sus vacaciones desde el {data.fechainicialvac} hasta el {data.fechafinalvac}.'
            else:
                mensaje1 = f'Su solicitud ha sido aprobada. '
                mensaje2 = 'Aprobada. '
                mensaje3 = f'Se le informará más detalles con el tiempo.'
                
        elif status == '3':
            mensaje1 = f'Lamentamos informarle que su solicitud ha sido '
            mensaje2 = 'Rechazada. '
            mensaje3 = f'El motivo del rechazo estará en la plataforma en sus solicitudes.'
        else:
            mensaje1 = f'Su solicitud está actualmente en '
            mensaje2 = 'Revisión. '
            mensaje3 = f'Se le notificará cuando se tome una decisión. Si necesita más información, puede verificar el estado en el portal de empleados.'

        context =  {
            'type':status,
            'ms':response_message,
            'empleado':f" {data.idcontrato.idempleado.papellido} {data.idcontrato.idempleado.sapellido} {data.idcontrato.idempleado.pnombre} {data.idcontrato.idempleado.snombre}",
            'hola': f"{data.idcontrato.idempleado.pnombre} {data.idcontrato.idempleado.papellido}",
            'fecha1': str(data.fechainicialvac) ,
            'fecha2': str(data.fechafinalvac ),
            'tipo': data.tipovac.nombrevacaus, 
            'mensaje1': mensaje1,
            'mensaje2': mensaje2,
            'mensaje3': mensaje3,
        }
        
        success = send_template_email(
                    email_type='vacation_request',  # Ajusta el tipo de correo según corresponda
                    context=context,
                    subject=email_subject,
                    recipient_list=recipient_list,
                )
        if success : 
            return JsonResponse({'success': True, 'message': 'Solicitud procesada correctamente.'})
        else :
            return JsonResponse({'success': False, 'message': 'Ocurrio Un error inesperado y el correo de notificacion no pudo ser enviados  '})

    
    
    # try:
    #     except Exception as e:
    #     return JsonResponse({'success': False, 'message': 'Ocurrio Un error inesperado '})
    
    return JsonResponse({'message': 'Metodo no permitido', 'status': 'error'}, status=405)



