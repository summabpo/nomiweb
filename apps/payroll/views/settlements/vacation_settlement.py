
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models  import Contratosemp , Vacaciones ,Contratos , Tipoavacaus , EmpVacaciones,Nomina, Festivos
from apps.payroll.forms.VacationSettlementForm import VacationSettlementForm , BenefitFormSet
from datetime import datetime, timedelta, date
from django.http import JsonResponse
from django.utils import timezone
from django.db import models
import holidays
from apps.components.humani import format_value_float


vacaciones_list = []
vacaemp = {}


def _festivos_colombia_fecha_range(d0: date, d1: date) -> set:
    """Festivos ley Colombia (holidays.CO) unidos a la tabla Festivos."""
    if d0 > d1:
        return set()
    years = list(range(d0.year, d1.year + 1))
    co = holidays.CO(years=years)
    db_dates = Festivos.objects.values_list('dia', flat=True)
    return set(co) | {d for d in db_dates if d is not None}


def _parse_date_yyyy_mm_dd(value):
    if not value or not str(value).strip():
        return None
    try:
        return datetime.strptime(str(value).strip(), '%Y-%m-%d').date()
    except ValueError:
        return None


def calcular_dias_habiles_vacaciones(fechainicialvac, fechafinalvac, cuentasabados, dias_festivos):
    """
    Días hábiles entre dos fechas: sin domingos, sin festivos, sábados solo si cuentasabados=1.
    Alineado con solicitudes de vacaciones (empleados).
    """
    if isinstance(fechainicialvac, datetime):
        fechainicialvac = fechainicialvac.date()
    if isinstance(fechafinalvac, datetime):
        fechafinalvac = fechafinalvac.date()
    fest = dias_festivos if isinstance(dias_festivos, set) else set(dias_festivos)
    total_dias = 0
    dia_actual = fechainicialvac
    while dia_actual <= fechafinalvac:
        if (
            dia_actual.weekday() != 6
            and dia_actual not in fest
            and (dia_actual.weekday() != 5 or cuentasabados == 1)
        ):
            total_dias += 1
        dia_actual += timedelta(days=1)
    return total_dias

@login_required
@role_required('accountant')
def vacation_settlement(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    # Obtener la lista de empleados
    contratos_empleados = Contratos.objects \
        .select_related('idempleado') \
        .filter(
            estadocontrato=1,
            tipocontrato__idtipocontrato__in=[1, 2, 3, 4],
            id_empresa_id=idempresa
        ) \
        .values(
            'idempleado__docidentidad',
            'idempleado__sapellido',
            'idempleado__papellido',
            'idempleado__pnombre',
            'idempleado__snombre',
            'idempleado__idempleado',
            'idcontrato'
        )

    # Limpiar None y 'no data' de los campos de nombre
    for emp in contratos_empleados:
        for field in ['idempleado__pnombre', 'idempleado__snombre', 'idempleado__papellido', 'idempleado__sapellido']:
            value = emp.get(field, '')
            if value is None or (isinstance(value, str) and value.strip().lower() == 'no data'):
                emp[field] = ''
            else:
                emp[field] = value

    context = {
        'contratos_empleados': contratos_empleados,
    }

    return render(request, './payroll/vacation_settlement.html', context)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


@login_required
@role_required("accountant", "company")
def vacation_settlement_add(request):
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = VacationSettlementForm(id_empresa=idempresa)
    vacaciones_list = []
    
    # Generar nuevo idvacmaster al abrir el modal (GET)
    # Este ID se mantendrá para todas las líneas agregadas en esta sesión del modal
    nuevo_idvacmaster = None
    if request.method == 'GET':
        max_id = Vacaciones.objects.filter(
            idvacmaster__isnull=False
        ).aggregate(max_id=models.Max('idvacmaster'))['max_id']
        nuevo_idvacmaster = (max_id or 0) + 1
    
    data = {
        "conceptors": [
            (1, "Vacaciones Disfrutadas"),
            (2, "Vacaciones Compensadas"),
            (3, "Licencia Remunerada"),
            (4, "Licencia No Remunerada"),
            (5, "Suspension"),
        ]
    }

    if request.method == 'POST':
        contrato = request.POST.get("contract")
        fecha_pago = request.POST.get("pay_date")
        novedad = request.POST.get("novedad")
        fecha_inicio = request.POST.get("fecha_inicio-1")
        fecha_fin = request.POST.get("fecha_fin-1")
        sabados = request.POST.get("sabados-1")
        periodo1 = request.POST.get("fecha_periodo-1")
        periodo2 = request.POST.get("fecha_periodo-2")

        dias_c = 0
        dias_v = 0
        valor = 0
        csabado = 1 if sabados == 'on' else 0

        # Vacaciones compensadas: solo días V manual; sin fechas de disfrute; base según periodo o fecha de pago
        if novedad == "2":
            try:
                dias_v = int((request.POST.get("dias_v-1") or "0").strip())
            except ValueError:
                dias_v = 0
            dias_c = dias_v
            ref_ibc = periodo1 or fecha_pago or ""
            salario = disabilities_ibc(contrato, ref_ibc) if ref_ibc else 0
            if salario == 0:
                salario = Contratos.objects.get(idcontrato=contrato).salario
            valor = round((salario / 30) * dias_c) if dias_c else 0
            csabado = 0
            fecha_inicio = ""
            fecha_fin = ""

        else:
            ref_ibc_dis = fecha_inicio or fecha_pago or ""
            salario = disabilities_ibc(contrato, ref_ibc_dis) if ref_ibc_dis else 0

            if salario == 0:
                salario = Contratos.objects.get(idcontrato=contrato).salario

            if fecha_inicio and fecha_fin:
                try:
                    fi = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                    ff = datetime.strptime(fecha_fin, '%Y-%m-%d')

                    # Días calendario
                    dias_c = (ff - fi).days + 1 if ff >= fi else 0

                    # Días hábiles: excluye domingos, festivos Colombia (ley) y tabla Festivos; sábados según cuentasabados
                    festivos = _festivos_colombia_fecha_range(fi.date(), ff.date())
                    dias_v = calcular_dias_habiles_vacaciones(fi, ff, csabado, festivos)

                    valor = round((salario / 30) * dias_c)

                except Exception:
                    dias_c = dias_v = 0

        fi_db = _parse_date_yyyy_mm_dd(fecha_inicio)
        ff_db = _parse_date_yyyy_mm_dd(fecha_fin)
        p1_db = _parse_date_yyyy_mm_dd(periodo1)
        p2_db = _parse_date_yyyy_mm_dd(periodo2)

                
        fechapago_db = _parse_date_yyyy_mm_dd(fecha_pago)

        # Obtener idvacmaster del formulario (campo oculto) o generar uno nuevo
        id_master = request.POST.get('idvacmaster')
        
        if not id_master or id_master == '':
            # Generar nuevo idvacmaster: obtener el máximo actual + 1
            max_id = Vacaciones.objects.filter(
                idvacmaster__isnull=False
            ).aggregate(max_id=models.Max('idvacmaster'))['max_id']
            
            id_master = (max_id or 0) + 1
        else:
            id_master = int(id_master)

        vacacion = Vacaciones.objects.create( 
            idcontrato= Contratos.objects.get(idcontrato = contrato) ,
            fechainicialvac = fi_db,
            ultimodiavac = ff_db,
            diascalendario = int(dias_c) ,
            diasvac = int(dias_v) if dias_v else 0,
            #diaspendientes = ,
            pagovac = valor if valor else 0,
            #totaldiastomados = int(dias_c) ,
            basepago = salario ,
            #estadovac = 1,
            #idnomina = nomina,
            cuentasabados= csabado ,
            tipovac= Tipoavacaus.objects.get(idvac = novedad ) ,
            perinicio = p1_db,
            perfinal = p2_db,
            fechapago = fechapago_db,
            idvacmaster = id_master
            
            )


        vacaciones_list = Vacaciones.objects.filter(fechapago = fechapago_db, idcontrato_id = contrato )

        #vacaciones_list.append(vacacion)



    return render(request, './payroll/partials/vacation_settlement_add.html', {
        'form': form,
        'data': data ,
        'vacaciones_list':vacaciones_list ,
        'idvacmaster': nuevo_idvacmaster if request.method == 'GET' else id_master,
    })
    



def calcular_periodos_vacaciones(idcontrato, idempresa, dias_vacaciones_actuales):
    """
    Calcula los períodos de vacaciones automáticamente basado en:
    1. Fecha de inicio del contrato
    2. Historial de vacaciones consumidas
    3. Días de vacaciones que se van a registrar
    
    Lógica:
    - Primer período: desde fechainiciocontrato hasta fechainiciocontrato + 1 año - 1 día
    - Períodos siguientes: consecutivos (día siguiente del perfinal anterior)
    - Si un período no se consume completamente (< 15 días), se reutiliza hasta completar 15 días
    - Se pueden tomar días de diferentes períodos (mixto)
    """
    try:
        # Obtener el contrato y fecha de inicio
        contrato = Contratos.objects.get(idcontrato=idcontrato, id_empresa_id=idempresa)
        fecha_inicio_contrato = contrato.fechainiciocontrato
        
        if not fecha_inicio_contrato:
            return None, None
        
        # Obtener historial de vacaciones del contrato (solo tipos 1 y 2)
        historial_vacaciones = Vacaciones.objects.filter(
            idcontrato_id=idcontrato,
            tipovac__idvac__in=[1, 2]  # Solo vacaciones disfrutadas y compensadas
        ).order_by('perinicio', 'perfinal')
        
        
        # Calcular períodos disponibles
        periodos_disponibles = []
        fecha_inicio_periodo = fecha_inicio_contrato
        fecha_hoy = date.today()
        
        # Generar períodos hasta la fecha actual + 2 años (para cubrir períodos futuros)
        fecha_limite = fecha_hoy + timedelta(days=730)
        
        # Primero, encontrar en qué período estamos actualmente
        periodo_actual_inicio = fecha_inicio_contrato
        while periodo_actual_inicio <= fecha_hoy:
            try:
                periodo_actual_fin = periodo_actual_inicio.replace(year=periodo_actual_inicio.year + 1) - timedelta(days=1)
            except ValueError:
                periodo_actual_fin = periodo_actual_inicio + timedelta(days=365) - timedelta(days=1)
                
            if fecha_hoy <= periodo_actual_fin:
                break
            try:
                periodo_actual_inicio = periodo_actual_inicio.replace(year=periodo_actual_inicio.year + 1)
            except ValueError:
                periodo_actual_inicio = periodo_actual_inicio + timedelta(days=365)
        
        # Ahora generar todos los períodos para análisis
        fecha_inicio_periodo = fecha_inicio_contrato
        
        while fecha_inicio_periodo <= fecha_limite:
            # Calcular la fecha fin: mismo día y mes del año siguiente, menos 1 día
            # Por ejemplo: 2025-02-16 a 2026-02-15
            try:
                fecha_fin_periodo = fecha_inicio_periodo.replace(year=fecha_inicio_periodo.year + 1) - timedelta(days=1)
            except ValueError:
                # En caso de años bisiestos (29 de febrero)
                fecha_fin_periodo = fecha_inicio_periodo + timedelta(days=365) - timedelta(days=1)
            
            # Calcular días consumidos en este período específico
            dias_consumidos = 0
            vacaciones_en_periodo = []
            
            for vacacion in historial_vacaciones:
                # Verificar si la vacación pertenece a este período (puede tener fechas ligeramente diferentes)
                if (vacacion.perinicio and vacacion.perfinal):
                    # Considerar que pertenece al período si las fechas están dentro del rango del año
                    if (abs((vacacion.perinicio - fecha_inicio_periodo).days) <= 5 and 
                        abs((vacacion.perfinal - fecha_fin_periodo).days) <= 5):
                        # Esta vacación corresponde a este período (con tolerancia de 5 días)
                        dias_consumidos += vacacion.diasvac or 0
                        vacaciones_en_periodo.append(f"ID:{vacacion.idvacaciones} ({vacacion.diasvac} días, {vacacion.perinicio}-{vacacion.perfinal})")
            
            # Si el período no está completamente consumido (< 15 días), está disponible
            dias_disponibles = 15 - dias_consumidos
            
            if dias_disponibles > 0:
                periodos_disponibles.append({
                    'inicio': fecha_inicio_periodo,
                    'fin': fecha_fin_periodo,
                    'dias_disponibles': dias_disponibles,
                    'dias_consumidos': dias_consumidos
                })
            
            # Siguiente período comienza exactamente un año después del inicio anterior
            # Esto mantiene la fecha exacta (16 de febrero cada año)
            try:
                fecha_inicio_periodo = fecha_inicio_periodo.replace(year=fecha_inicio_periodo.year + 1)
            except ValueError:
                # En caso de años bisiestos
                fecha_inicio_periodo = fecha_inicio_periodo + timedelta(days=365)
        
        # Encontrar el mejor período para los días solicitados
        
        if not periodos_disponibles:
            return None, None
        
        # Ordenar períodos por fecha de inicio (cronológicamente)
        periodos_disponibles.sort(key=lambda x: x['inicio'])
        
        # Lógica para manejar días mixtos de diferentes períodos
        fecha_hoy = date.today()
        dias_restantes = dias_vacaciones_actuales
        periodos_sugeridos = []
        
        # Buscar períodos disponibles en orden cronológico
        for periodo in periodos_disponibles:
            if dias_restantes <= 0:
                break
                
            if periodo['dias_disponibles'] > 0:
                # Calcular cuántos días se pueden tomar de este período
                dias_de_este_periodo = min(dias_restantes, periodo['dias_disponibles'])
                
                periodos_sugeridos.append({
                    'periodo': periodo,
                    'dias_sugeridos': dias_de_este_periodo
                })
                
                dias_restantes -= dias_de_este_periodo
        
        if periodos_sugeridos:
            # Retornar el primer período (donde van la mayoría o todos los días)
            primer_periodo = periodos_sugeridos[0]['periodo']
            
            return primer_periodo['inicio'], primer_periodo['fin']
        
        return None, None
        
    except Exception as e:
        return None, None


def disabilities_ibc(contract, date):
    ibc = contract.salario

    date_obj = datetime.strptime(date, "%Y-%m-%d")
    mes_num = date_obj.month
    ano = date_obj.year

    meses = [
        "ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO",
        "JULIO","AGOSTO","SEPTIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE"
    ]

    # calcular mes anterior
    if mes_num == 1:
        mes_anterior_num = 12
        ano -= 1
    else:
        mes_anterior_num = mes_num - 1

    mes_texto = meses[mes_anterior_num - 1]

    suma = 0

    conceptos = Nomina.objects.filter(
        idcontrato_id=contract,
        estadonomina = 2 , 
        idnomina__mesacumular=mes_texto,
        idnomina__anoacumular__ano=ano,
        idconcepto__indicador__nombre='basevacaciones'
    )

    for data in conceptos:        
        if data.idconcepto.codigo == 4 : 
            suma += data.valor * 0.7
        else:
            suma += data.valor

    if suma > 0:
        ibc = suma
    return ibc

@login_required
@role_required("accountant", "company")
def vacation_calculate_periods(request):
    """
    Endpoint AJAX para calcular períodos de vacaciones automáticamente
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        usuario = request.session.get('usuario', {})
        idempresa = usuario.get('idempresa')
        
        idcontrato = request.POST.get('idcontrato')
        dias_vacaciones_str = request.POST.get('dias_vacaciones', '0')
        
        if not idcontrato:
            return JsonResponse({'error': 'ID de contrato requerido'}, status=400)
        
        if not idempresa:
            return JsonResponse({'error': 'ID de empresa no encontrado en sesión'}, status=400)
        
        try:
            dias_vacaciones = int(dias_vacaciones_str)
        except ValueError:
            return JsonResponse({'error': f'Días de vacaciones inválido: {dias_vacaciones_str}'}, status=400)
        
        # Calcular períodos
        perinicio, perfinal = calcular_periodos_vacaciones(idcontrato, idempresa, dias_vacaciones)
        
        
        if perinicio and perfinal:
            # Verificar si necesita días mixtos
            mensaje_adicional = ""
            
            # Obtener el contrato nuevamente para el cálculo de días mixtos
            contrato_temp = Contratos.objects.get(idcontrato=idcontrato, id_empresa_id=idempresa)
            historial_temp = Vacaciones.objects.filter(
                idcontrato_id=idcontrato,
                tipovac__idvac__in=[1, 2]
            ).order_by('perinicio', 'perfinal')
            
            # Recalcular para obtener información de días mixtos
            periodos_disponibles_temp = []
            fecha_inicio_temp = contrato_temp.fechainiciocontrato
            fecha_limite_temp = date.today() + timedelta(days=730)
            
            while fecha_inicio_temp <= fecha_limite_temp:
                try:
                    fecha_fin_temp = fecha_inicio_temp.replace(year=fecha_inicio_temp.year + 1) - timedelta(days=1)
                except ValueError:
                    fecha_fin_temp = fecha_inicio_temp + timedelta(days=365) - timedelta(days=1)
                
                dias_consumidos_temp = 0
                for vac in historial_temp:
                    if (vac.perinicio and vac.perfinal and
                        abs((vac.perinicio - fecha_inicio_temp).days) <= 5 and 
                        abs((vac.perfinal - fecha_fin_temp).days) <= 5):
                        dias_consumidos_temp += vac.diasvac or 0
                
                dias_disponibles_temp = 15 - dias_consumidos_temp
                if dias_disponibles_temp > 0:
                    periodos_disponibles_temp.append({
                        'inicio': fecha_inicio_temp,
                        'fin': fecha_fin_temp,
                        'dias_disponibles': dias_disponibles_temp
                    })
                
                try:
                    fecha_inicio_temp = fecha_inicio_temp.replace(year=fecha_inicio_temp.year + 1)
                except ValueError:
                    fecha_inicio_temp = fecha_inicio_temp + timedelta(days=365)
            
            # Verificar si necesita distribución mixta
            dias_restantes_check = dias_vacaciones
            distribucion = []
            
            for periodo in sorted(periodos_disponibles_temp, key=lambda x: x['inicio']):
                if dias_restantes_check <= 0:
                    break
                if periodo['dias_disponibles'] > 0:
                    dias_este_periodo = min(dias_restantes_check, periodo['dias_disponibles'])
                    distribucion.append({
                        'periodo': f"{periodo['inicio'].strftime('%Y-%m-%d')} - {periodo['fin'].strftime('%Y-%m-%d')}",
                        'dias': dias_este_periodo
                    })
                    dias_restantes_check -= dias_este_periodo
            
            if len(distribucion) > 1:
                mensaje_adicional = f"\n\n⚠️ DÍAS MIXTOS REQUERIDOS:\n"
                for i, dist in enumerate(distribucion):
                    mensaje_adicional += f"Línea {i+1}: {dist['dias']} días en período {dist['periodo']}\n"
                mensaje_adicional += "\nDebe crear múltiples líneas de liquidación."
            
            resultado = {
                'success': True,
                'perinicio': perinicio.strftime('%Y-%m-%d'),
                'perfinal': perfinal.strftime('%Y-%m-%d'),
                'mensaje_adicional': mensaje_adicional,
                'distribucion_sugerida': distribucion if len(distribucion) > 1 else None,
                'debug_info': {
                    'idcontrato': idcontrato,
                    'dias_vacaciones': dias_vacaciones,
                    'idempresa': idempresa
                }
            }

            return JsonResponse(resultado)
        else:
            error_response = {
                'success': False,
                'error': 'No se pudieron calcular los períodos. Verifique la fecha de inicio del contrato.',
                'debug_info': {
                    'idcontrato': idcontrato,
                    'dias_vacaciones': dias_vacaciones,
                    'idempresa': idempresa
                }
            }

            return JsonResponse(error_response)
            
    except Exception as e:

        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': f'Error calculando períodos: {str(e)}'
        })


@login_required
@role_required("accountant", "company")
def vacation_settlement_add_list(request):
    
    pay_date = request.POST.get('pay_date')
    type_novedad = request.POST.get('type_novedad')
    
    contrato = request.POST.get('idc')

    qs = Vacaciones.objects.filter(
        fechapago=pay_date,
        idcontrato_id=contrato,
    )
    if type_novedad == "1":
        qs = qs.filter(tipovac__idvac__in=[1, 2])
    elif type_novedad == "2":
        qs = qs.filter(tipovac__idvac__in=[3, 4, 5])

    vacaciones_list = qs.values(
        'tipovac__nombrevacaus',
        'fechainicialvac',
        'ultimodiavac',
        'cuentasabados',
        'diascalendario',
        'diasvac',
        'basepago',
        'pagovac',
        'perinicio',
        'perfinal',
        'idvacaciones',
    )

    
    rows = []
    for row in vacaciones_list:
        r = dict(row)
        for k in ("fechainicialvac", "ultimodiavac", "perinicio", "perfinal"):
            v = r.get(k)
            if v is not None and hasattr(v, "isoformat"):
                r[k] = v.isoformat()
        rows.append(r)

    return JsonResponse({"vacaciones_list": rows})


@login_required
@role_required("accountant", "company")
def vacation_settlement_delete(request):
    """Elimina una fila de liquidación de vacaciones (solo empresa del usuario)."""
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "method"}, status=405)
    idv = request.POST.get("idvacaciones")
    idempresa = request.session.get("usuario", {}).get("idempresa")
    if not idv or not idempresa:
        return JsonResponse({"ok": False}, status=400)
    try:
        v = Vacaciones.objects.select_related("idcontrato").get(
            idvacaciones=idv,
            idcontrato__id_empresa_id=idempresa,
        )
    except Vacaciones.DoesNotExist:
        return JsonResponse({"ok": False}, status=404)
    v.delete()
    return JsonResponse({"ok": True})


@login_required
@role_required('accountant')
def vacation_modal_data(request,id,t):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    novedad = Vacaciones.objects.filter(idcontrato_id = id)

    if t == '1' : 
        titulo = 'Vacaciones'
        p = False
        novedad =  Vacaciones.objects.filter(idcontrato__idcontrato=id, tipovac__idvac__in=[1,2]) 
    else:
        novedad = Vacaciones.objects.filter(idcontrato__idcontrato=id, tipovac__idvac__in=[3,4,5])
        titulo = 'Ausensias'
        p = True

    data = {
        'titulo': titulo , 
        'pass': p ,
        'novedad' : novedad ,

    }
    
    return render(request, './payroll/partials/vacation_modal_data.html', {
        'data': data,
        
    })




@login_required
@role_required("accountant", "company")
def vacation_contract_hire(request):
    """Fecha de ingreso del contrato (ayuda para armar periodo de vacaciones)."""
    if request.method != 'POST':
        return JsonResponse({'error': 'method'}, status=405)
    idc = request.POST.get('idcontrato')
    idempresa = request.session.get('usuario', {}).get('idempresa')
    if not idc or not idempresa:
        return JsonResponse({'fechainiciocontrato': None, 'valid_contract': False})
    c = Contratos.objects.filter(idcontrato=idc, id_empresa_id=idempresa).first()
    if not c:
        return JsonResponse({'fechainiciocontrato': None, 'valid_contract': False})
    f = c.fechainiciocontrato
    return JsonResponse({
        'fechainiciocontrato': f.isoformat() if f else None,
        'valid_contract': True,
    })


@login_required
@role_required("accountant", "company")
def vacation_contract_history(request, idcontrato):
    """Historial de registros en `Vacaciones` para el contrato (ventana auxiliar desde el modal)."""
    idempresa = request.session.get('usuario', {}).get('idempresa')
    if not idempresa:
        return render(request, 'payroll/vacation_contract_history_standalone.html', {
            'error': 'Sesión sin empresa.',
            'rows': [],
            'idcontrato': idcontrato,
        }, status=403)
    get_object_or_404(Contratos, idcontrato=idcontrato, id_empresa_id=idempresa)
    rows = (
        Vacaciones.objects.filter(idcontrato_id=idcontrato)
        .select_related('tipovac')
        .order_by('-idvacaciones')
    )
    return render(request, 'payroll/vacation_contract_history_standalone.html', {
        'error': None,
        'rows': rows,
        'idcontrato': idcontrato,
    })


@login_required
@role_required("accountant", "company")
def vacation_days_calc(request):
    fecha_inicio = request.POST.get('fecha_inicio')
    fecha_fin = request.POST.get('fecha_fin')
    incluir_sabados = request.POST.get('incluir_sabados')
    contrato = request.POST.get('idc')
    modo = request.POST.get('modo')

    dias_c = ''
    dias_v = ''
    valor = ''

    if modo == 'compensada':
        dias_v_raw = request.POST.get('dias_v')
        fecha_ref = request.POST.get('fecha_ref') or request.POST.get('fecha_pago') or ''
        try:
            dias_v_int = int(dias_v_raw)
        except (TypeError, ValueError):
            return JsonResponse({
                'dias_c': '',
                'dias_v': '',
                'salario': '',
                'valor': '',
            })
        salario = disabilities_ibc(contrato, fecha_ref) if fecha_ref else 0
        if salario == 0:
            salario = Contratos.objects.get(idcontrato=contrato).salario
        dias_c = dias_v = dias_v_int
        valor = round((salario / 30) * dias_c)
        valor = format_value_float(valor)
        return JsonResponse({
            'dias_c': dias_c,
            'dias_v': dias_v,
            'salario': format_value_float(salario),
            'valor': valor,
        })

    salario = disabilities_ibc(contrato, fecha_inicio or '') if fecha_inicio else 0

    if salario == 0:
        salario = Contratos.objects.get(idcontrato=contrato).salario

    csabado = 1 if incluir_sabados == 'true' else 0

    if fecha_inicio and fecha_fin:
        try:
            fi = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            ff = datetime.strptime(fecha_fin, '%Y-%m-%d')

            # Días calendario
            dias_c = (ff - fi).days + 1 if ff >= fi else 0

            festivos = _festivos_colombia_fecha_range(fi.date(), ff.date())
            dias_v = calcular_dias_habiles_vacaciones(fi, ff, csabado, festivos)

            valor = round((salario / 30) * dias_c)
            valor = format_value_float(valor)
        except Exception:
            dias_c = dias_v = 'Err'

    return JsonResponse({
            'dias_c': dias_c,
            'dias_v': dias_v,
            'salario': format_value_float(salario),
            'valor': valor,
        })
