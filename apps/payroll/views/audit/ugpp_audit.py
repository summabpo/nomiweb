from traceback import print_tb
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Crearnomina , Tipodenomina ,NovFijos,Vacaciones, Empresa,Prestamos ,Incapacidades, Conceptosfijos , Salariominimoanual,Conceptosdenomina , Nomina , Contratos
from apps.components.salary import salario_mes
from decimal import Decimal, ROUND_HALF_UP, getcontext
from django.db.models import Sum, Count, Q
from apps.payroll.views.payroll.payroll_automatic_systems import calcular_dias, precargar_acumulados
from apps.payroll.views.payroll.payroll_automatic_systems import return_transporte , calculo_incapacidad , return_tipo_incapacidad , calcular_suspenciones2
from apps.companies.views.disabilities.disabilities import disabilities_ibc 

from datetime import timedelta

def _norm_codigo(codigo):
    return str(codigo).strip()


def _money_equal(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    try:
        da = Decimal(str(a)).quantize(Decimal('0.01'))
        db = Decimal(str(b)).quantize(Decimal('0.01'))
        return da == db
    except Exception:
        return False


def _qty_equal(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    try:
        return Decimal(str(a)).quantize(Decimal('0.0001')) == Decimal(str(b)).quantize(Decimal('0.0001'))
    except Exception:
        return False


def _normalize_concept_row(item):
    return {
        'codigo': _norm_codigo(item.get('codigo')),
        'nombre': item.get('nombre', ''),
        'valor': float(item['valor']) if item.get('valor') is not None else None,
        'cantidad': float(item['cantidad']) if item.get('cantidad') is not None else None,
    }


@login_required
@role_required('accountant')
def UgppPayrollAudit(request,payroll_id):
    data = {}
    payroll = get_object_or_404(Crearnomina, idnomina=payroll_id)
    salaries = get_audit_salaries(payroll_id)
    contributions = get_audit_contributions(payroll_id)
    total_errors , errors_list = get_audit_total_errors(payroll_id)
    total_aportes_ss = (
        abs(float(contributions.get('eps') or 0))
        + abs(float(contributions.get('pension') or 0))
        + abs(float(contributions.get('fsp') or 0))
    )
    

    empleados_raw = Nomina.objects \
        .select_related('idcontrato') \
        .filter(idnomina=payroll_id, estadonomina=1) \
        .values(
            'idcontrato__idempleado__docidentidad',
            'idcontrato__idempleado__papellido',
            'idcontrato__idempleado__sapellido',
            'idcontrato__idempleado__pnombre',
            'idcontrato__idempleado__snombre',
            'idcontrato__salario',
            'idcontrato__idempleado__idempleado',
            'idcontrato'
        ) \
        .order_by('idcontrato__idempleado__papellido') \
        .distinct()

    empleados = []
    for e in empleados_raw:
        doc = e.get('idcontrato__idempleado__docidentidad')
        if not doc or str(doc).strip().lower() == "no data":
            doc = ""

        nombres = [
            e.get('idcontrato__idempleado__pnombre'),
            e.get('idcontrato__idempleado__snombre'),
            e.get('idcontrato__idempleado__papellido'),
            e.get('idcontrato__idempleado__sapellido'),
        ]
        full_name = " ".join([
            n.strip() for n in nombres
            if n and n.strip().lower() != "no data"
        ])
        
        empleados.append({
            'documento': doc,
            'nombre_completo': full_name,
            'salario': e.get('idcontrato__salario'),
            'idempleado': e.get('idcontrato__idempleado__idempleado'),
            'idcontrato': e.get('idcontrato'),
        })

    data = {
        'payroll': payroll,
        'salaries': salaries,
        'contributions': contributions,
        'total_employees': get_audit_employees(payroll_id),
        'total_to_pay': get_audit_total_to_pay(payroll_id),
        'total_errors': total_errors,
        'errors_list': errors_list,
        'empleados': empleados,
        'total_aportes_ss': total_aportes_ss,
    }
    return render(request, './payroll/UgppPayrollAudit.html', data)


@login_required
@role_required('accountant')
def audit_employee_payroll(request, payroll_id, idcontrato):
    errors_list = []
    total_errors = 0
    tabla_aportes = []

    conceptos_payroll = Nomina.objects.filter(
        idnomina=payroll_id,
        idcontrato=idcontrato
    ).values(
        'idconcepto__codigo',
        'idconcepto__nombreconcepto',
        'valor',
        'cantidad'
    ).order_by('idconcepto__codigo')

    conceptos_payroll_list = [
        _normalize_concept_row({
            'codigo': c['idconcepto__codigo'],
            'nombre': c['idconcepto__nombreconcepto'],
            'valor': c['valor'],
            'cantidad': c['cantidad'],
        })
        for c in conceptos_payroll
    ]

    audit_data = get_audit_employee(payroll_id, idcontrato)

    conceptos_audit_list = audit_data['conceptos']
    contrib_nomina = audit_data['contribuciones']['nomina']
    contrib_calculada = audit_data['contribuciones']['calculada']

    audit_codigos_set = {_norm_codigo(i['codigo']) for i in conceptos_audit_list}
    aportes_set = {'60', '70', '90','25','26','27','28','29'}

    conceptos_audit_aportes = [
        item for item in conceptos_payroll_list
        if _norm_codigo(item['codigo']) in aportes_set
    ]

    conceptos_audit_faltantes = [
        item for item in conceptos_payroll_list
        if _norm_codigo(item['codigo']) not in audit_codigos_set
        and _norm_codigo(item['codigo']) not in aportes_set
    ]

    for item in conceptos_audit_faltantes:
        total_errors += 1
        errors_list.append(
            f"Concepto {_norm_codigo(item['codigo'])} — {item.get('nombre', '')}: "
            f"registrado en nómina pero no existe en el resultado auditado (salario/transporte)."
        )

    faltantes_codigos_set = {_norm_codigo(i['codigo']) for i in conceptos_audit_faltantes}

    conceptos_payroll_list = [
        item for item in conceptos_payroll_list
        if _norm_codigo(item['codigo']) not in faltantes_codigos_set
    ]

    codes_payroll_ap = {_norm_codigo(i['codigo']) for i in conceptos_audit_aportes}
    codes_nom = {_norm_codigo(i['codigo']) for i in contrib_nomina}
    codes_calc = {_norm_codigo(i['codigo']) for i in contrib_calculada}
    codigos_filtrados = sorted(
        (codes_payroll_ap | codes_nom | codes_calc) & aportes_set,
        key=lambda x: int(x),
    )


    if codigos_filtrados:
        nomina_payroll = {_norm_codigo(i['codigo']): i for i in conceptos_audit_aportes}
        nomina_audit = {_norm_codigo(i['codigo']): i for i in contrib_nomina}
        calc_dict = {_norm_codigo(i['codigo']): i for i in contrib_calculada}

        for codigo in codigos_filtrados:
            nom = nomina_payroll.get(codigo)
            aud = nomina_audit.get(codigo)
            calc = calc_dict.get(codigo)

            base = nom or aud or calc

            fila = {
                'codigo': codigo,
                'nombre': (base or {}).get('nombre', ''),

                'nomina_valor': nom.get('valor') if nom else None,
                'nomina_cantidad': nom.get('cantidad') if nom else None,

                'calc_valor': calc.get('valor') if calc else None,
                'calc_cantidad': calc.get('cantidad') if calc else None,

                'audit_valor': aud.get('valor') if aud else None,
                'audit_cantidad': aud.get('cantidad') if aud else None,
            }

            if not nom:
                fila['estado'] = 'faltante_nomina'
                total_errors += 1
                errors_list.append(
                    f"Concepto {codigo} — {fila['nombre']}: no está en la nómina del empleado "
                    f"pero sí en auditoría/cálculo."
                )
            elif not aud:
                fila['estado'] = 'faltante_audit'
                total_errors += 1
                errors_list.append(
                    f"Concepto {codigo} — {fila['nombre']}: está en nómina pero la auditoría "
                    f"no generó el valor esperado."
                )
            elif not (
                _money_equal(nom.get('valor'), aud.get('valor'))
                and _qty_equal(nom.get('cantidad'), aud.get('cantidad'))
            ):
                fila['estado'] = 'diferente'
                total_errors += 1
                errors_list.append(
                    f"Concepto {codigo} — {fila['nombre']}: nómina vs auditoría "
                    f"(Nómina: valor={nom.get('valor')}, cantidad={nom.get('cantidad')} | "
                    f"Auditoría: valor={aud.get('valor')}, cantidad={aud.get('cantidad')})."
                )
            elif calc and not (
                _money_equal(nom.get('valor'), calc.get('valor'))
                and _qty_equal(nom.get('cantidad'), calc.get('cantidad'))
            ):
                fila['estado'] = 'diferente'
                total_errors += 1
                errors_list.append(
                    f"Concepto {codigo} — {fila['nombre']}: nómina vs cálculo auditado "
                    f"(Nómina: valor={nom.get('valor')}, cantidad={nom.get('cantidad')} | "
                    f"Calculado: valor={calc.get('valor')}, cantidad={calc.get('cantidad')})."
                )
            else:
                fila['estado'] = 'ok'

            tabla_aportes.append(fila)

        aportes_en_tabla = set(codigos_filtrados)
        conceptos_payroll_list = [
            item for item in conceptos_payroll_list
            if _norm_codigo(item['codigo']) not in aportes_en_tabla
        ]

    audit_map = {_norm_codigo(a['codigo']): a for a in conceptos_audit_list}
    conceptos_comparacion = []
    for c in conceptos_payroll_list:
        ac = audit_map.get(_norm_codigo(c['codigo']))
        match_ok = bool(
            ac
            and _money_equal(c.get('valor'), ac.get('valor'))
            and _qty_equal(c.get('cantidad'), ac.get('cantidad'))
        )
        conceptos_comparacion.append({
            'codigo': c['codigo'],
            'nombre': c.get('nombre', ''),
            'nom_valor': c.get('valor'),
            'nom_cantidad': c.get('cantidad'),
            'audit_valor': ac.get('valor') if ac else None,
            'audit_cantidad': ac.get('cantidad') if ac else None,
            'match_ok': match_ok,
        })

    data = {
        'conceptos_payroll': conceptos_payroll_list,
        'conceptos_comparacion': conceptos_comparacion,
        'conceptos_audit': conceptos_audit_list,
        'contrib_nomina': contrib_nomina,
        'contrib_calculada': contrib_calculada,
        'conceptos_audit_faltantes': conceptos_audit_faltantes,
        'tabla_aportes': tabla_aportes,
        'total_errors': total_errors,
        'errors_list': errors_list,
    }

    return render(request,'./payroll/partials/audit_employee_payroll.html',{'data': data, 'conceptos_audit_faltantes': conceptos_audit_faltantes},)


def get_audit_total_errors(payroll_id):

    errors_count = 0
    errors_list = []

    errors_count1 , errors_list1 = error_salary_audit(payroll_id)
    errors_count2 , errors_list2 = error_contributions_audit(payroll_id)
    errors_count3 , errors_list3 = error_transport_audit(payroll_id)
    
    errors_count = errors_count1 + errors_count2 + errors_count3
    errors_list = errors_list1 + errors_list2 + errors_list3

    
    return errors_count , errors_list


def get_audit_employee(payroll_id, idcontrato):

    data = []

    #  1. Salario
    data1 = salary_audit_employee(payroll_id, idcontrato)

    #  2. Transporte
    data2 = transport_audit_employee(payroll_id, idcontrato)

    

    if isinstance(data1, list):
        data.extend(data1)

    if isinstance(data2, list):
        data.extend(data2)

    #  3. Contribuciones (base normal)
    data3 = contributions_audit_employee(payroll_id, idcontrato, data)


    if not isinstance(data3, dict):
        data3 = {'nomina': [], 'calculada': []}

    #  4. Incapacidades → se agregan a data3
    contrato = Contratos.objects.get(idcontrato=idcontrato)
    disable_data = disable_audit_employee(payroll_id, contrato)
    data4 = deductions_audit_employee(payroll_id, contrato)

    if isinstance(data4, list):
        data.extend(data4)
        

    if isinstance(disable_data, dict):
        data3['nomina'].extend(disable_data.get('nomina', []))
        data3['calculada'].extend(disable_data.get('calculada', []))

    #  Normalización
    data[:] = [_normalize_concept_row(r) for r in data]
    data3['nomina'] = [_normalize_concept_row(r) for r in data3.get('nomina', [])]
    data3['calculada'] = [_normalize_concept_row(r) for r in data3.get('calculada', [])]

    return {
        'conceptos': data,
        'contribuciones': data3,
    }



def salary_audit_employee(payroll_id, idcontrato):
    data = []
    
    try:
        nomina = Crearnomina.objects.get(idnomina=payroll_id)
    except Crearnomina.DoesNotExist:
        return []

    contrato = Contratos.objects.get(idcontrato=idcontrato)
    if contrato.tiposalario.idtiposalario == 2:
        codigo_aux = '4'
    elif contrato.tipocontrato_id == 6:
        codigo_aux = '34'
    else:
        codigo_aux = '1'
    

    acumulados = precargar_acumulados(nomina, int(codigo_aux))
    concepto = Conceptosdenomina.objects.get(codigo = codigo_aux, id_empresa = contrato.id_empresa)

    diasnomina = calcular_dias(contrato,nomina,int(codigo_aux),acumulados)

    #calculo_prestamo(contrato, payroll_id)
    #Calculo_vacaciones(contrato, payroll_id)
    #calculo_novfija(contrato, payroll_id)

    if diasnomina > 0:

        getcontext().prec = 50

        mes = nomina.fechainicial.month
        anio = nomina.fechainicial.year

        salario = salario_mes(contrato,mes,anio)

        valorsalario = (
            Decimal(str(salario))
            * Decimal(str(diasnomina))
            / Decimal('30')
        ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)


        data.append({
            'codigo': _norm_codigo(concepto.codigo),
            'nombre': concepto.nombreconcepto,
            'valor': float(valorsalario),
            'cantidad': float(diasnomina)
        })

    return data

def transport_audit_employee(payroll_id, idcontrato):
    data = []
    
    try:
        nomina = Crearnomina.objects.get(idnomina=payroll_id)
    except Crearnomina.DoesNotExist:
        return []

    contrato = Contratos.objects.get(idcontrato=idcontrato)
    sal_min = Salariominimoanual.objects.get(ano=nomina.anoacumular.ano).salariominimo
    aux_tra = Salariominimoanual.objects.get(ano=nomina.anoacumular.ano).auxtransporte
    concepto = Conceptosdenomina.objects.get(codigo=2, id_empresa = contrato.id_empresa)
    acumulados = precargar_acumulados(nomina, 2)

    diasnomina = calcular_dias(contrato, nomina, 2,acumulados)

    if contrato.tipocontrato.idtipocontrato in [5, 6]:
        return data

    transporte = return_transporte(contrato, nomina, diasnomina, sal_min, aux_tra)

    if diasnomina > 0 and transporte > 0:
        data.append({
            'codigo': _norm_codigo(concepto.codigo),
            'nombre': concepto.nombreconcepto,
            'valor': float(transporte),
            'cantidad': float(diasnomina)
        })

    return data

def contributions_audit_employee(payroll_id, idcontrato, data_ex):
    data_audit = []
    data_calculada = []

    EPS = Conceptosfijos.objects.get(idfijo=8)
    AFP = Conceptosfijos.objects.get(idfijo=10)
    tope_ibc = Conceptosfijos.objects.get(idfijo=2)
    factor_integral = Conceptosfijos.objects.get(idfijo=1).valorfijo

    fsp416 = Conceptosfijos.objects.get(idfijo=12).valorfijo
    fsp1617 = Conceptosfijos.objects.get(idfijo=13).valorfijo
    fsp1718 = Conceptosfijos.objects.get(idfijo=14).valorfijo
    fsp1819 = Conceptosfijos.objects.get(idfijo=15).valorfijo
    fsp1920 = Conceptosfijos.objects.get(idfijo=16).valorfijo
    fsp21 = Conceptosfijos.objects.get(idfijo=17).valorfijo

    contrato = Contratos.objects.select_related('tiposalario').get(idcontrato=idcontrato)

    conceptos_validos = {
        _norm_codigo(c)
        for c in Conceptosdenomina.objects.filter(
            id_empresa=contrato.id_empresa,
            indicador__nombre='basesegsocial',
        ).values_list('codigo', flat=True)
    }

    total_data = sum(
        item['valor']
        for item in data_ex
        if _norm_codigo(item.get('codigo')) in conceptos_validos
    )

    try:
        nomina = Crearnomina.objects.select_related('anoacumular').get(idnomina=payroll_id)
    except Crearnomina.DoesNotExist:
        return {'nomina': [], 'calculada': []}

    tipo_salario = contrato.tiposalario.idtiposalario
    sal_min = Salariominimoanual.objects.get(ano=nomina.anoacumular.ano).salariominimo
    sal_min_d = Decimal(str(sal_min))

    # ==========================================
    # BASE SEGURIDAD SOCIAL - nomina general
    # ==========================================

    total_base_ss = Nomina.objects.filter(
        idcontrato=contrato,
        idnomina_id=payroll_id,
        idconcepto__indicador__nombre='basesegsocial',
    ).exclude(
        idconcepto__codigo__in=[60, 70, 90],
    ).aggregate(total=Sum('valor'))['total'] or 0

    base_ss_fsp = Nomina.objects.filter(
        idcontrato=contrato,
        idnomina__mesacumular=nomina.mesacumular,
        idnomina__anoacumular=nomina.anoacumular,
        idconcepto__indicador__nombre='basesegsocial',
    ).exclude(
        idconcepto__codigo__in=[60, 70, 90],
    ).aggregate(total=Sum('valor'))['total'] or 0

    if tipo_salario == 2:
        base_ss_fsp2 = Decimal(str(base_ss_fsp)) * Decimal('0.7')
    else:
        base_ss_fsp2 = Decimal(str(base_ss_fsp))

    valor_fsp = Decimal('0')
    if base_ss_fsp2 > 0 or Decimal(str(total_base_ss)) > 0:
        if base_ss_fsp2 <= (sal_min_d * 4):
            FSP = 0
        elif base_ss_fsp2 > (sal_min_d * 20):
            FSP = fsp21
        elif base_ss_fsp2 > (sal_min_d * 19):
            FSP = fsp1920
        elif base_ss_fsp2 > (sal_min_d * 18):
            FSP = fsp1819
        elif base_ss_fsp2 > (sal_min_d * 17):
            FSP = fsp1718
        elif base_ss_fsp2 > (sal_min_d * 16):
            FSP = fsp1617
        elif base_ss_fsp2 > (sal_min_d * 4):
            FSP = fsp416
        else:
            FSP = 0

        if FSP > 0:
            valor_fsp = (
                base_ss_fsp2 * Decimal(str(FSP)) / Decimal('100')
            ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        if contrato.pensionado == '2':
            valor_fsp = Decimal('0')

    if total_base_ss > 0:
        base_max = sal_min * tope_ibc.valorfijo
        tbs = float(total_base_ss)

        if tipo_salario == 2:
            tbs *= float(factor_integral / 100)
            tbs = round(tbs, 2)

        base_ss = min(tbs, base_max)
        base_ss = round(base_ss, 2)

        valoreps = (
            Decimal(str(base_ss)) * Decimal(EPS.valorfijo) / Decimal('100')
        ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

        valorafp = (
            Decimal(str(base_ss)) * Decimal(AFP.valorfijo) / Decimal('100')
        ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

        if contrato.pensionado == '2':
            valorafp = Decimal('0')

        if valoreps > 0:
            data_audit.append({
                'codigo': '60',
                'nombre': 'EPS - Nomina General',
                'valor': float(-valoreps),
                'cantidad': float(0),
            })

        if valorafp > 0:
            data_audit.append({
                'codigo': '70',
                'nombre': 'AFP - Nomina General',
                'valor': float(-valorafp),
                'cantidad': float(0),
            })
    
    if valor_fsp > 0:
        data_audit.append({
            'codigo': '90',
            'nombre': 'FSP - Nomina General',
            'valor': float(-valor_fsp),
            'cantidad': float(0),
        })

    # ==========================================
    # BASE SEGURIDAD SOCIAL - nomina Generada por el sistema
    # ==========================================

    if total_data > 0:
        base_max = sal_min * tope_ibc.valorfijo
        td = float(total_data)

        if tipo_salario == 2:
            td *= float(factor_integral / 100)
            td = round(td, 2)

        base_ss = min(td, base_max)
        base_ss = round(base_ss, 2)

        valoreps = (
            Decimal(str(base_ss)) * Decimal(EPS.valorfijo) / Decimal('100')
        ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

        valorafp = (
            Decimal(str(base_ss)) * Decimal(AFP.valorfijo) / Decimal('100')
        ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

        if contrato.pensionado == '2':
            valorafp = Decimal('0')

        if valoreps > 0:
            data_calculada.append({
                'codigo': '60',
                'nombre': 'EPS - Nomina auditada',
                'valor': float(-valoreps),
                'cantidad': float(0),
            })

        if valorafp > 0:
            data_calculada.append({
                'codigo': '70',
                'nombre': 'AFP - Nomina auditada',
                'valor': float(-valorafp),
                'cantidad': float(0),
            })

        

        if valor_fsp > 0:
            data_calculada.append({
                'codigo': '90',
                'nombre': 'FSP - Nomina auditada',
                'valor': float(-valor_fsp),
                'cantidad': float(0),
            })

    return {
        'nomina': data_audit,
        'calculada': data_calculada,
    }




def disable_audit_employee(payroll_id,idcontrato):
    data = []
    data_audit = []
    data_calculada = []

    nomina = Crearnomina.objects.get(idnomina=payroll_id)
    inicio_nomina, fin_nomina = nomina.fechainicial, nomina.fechafinal
    ano = nomina.anoacumular.ano 

    salario_minimo = Salariominimoanual.objects.get( ano = ano ).salariominimo
    pago_incapacidad = Empresa.objects.get(idempresa = idcontrato.id_empresa.idempresa).ige100 or "NO"

    incapacidades = Incapacidades.objects.filter(idcontrato = idcontrato ).order_by('-fechainicial')

    for incapacidad in incapacidades:

        dias_incapacidad = 0 
        dias_asumidos = 0
        ini = incapacidad.fechainicial
        fin = ini + timedelta(days = incapacidad.dias ) - timedelta(days = 1 )

        ibc = incapacidad.ibc
        tipo = incapacidad.origenincap
        prorroga = incapacidad.prorroga
        dias = incapacidad.dias

        segundo_dia = ini + timedelta(days=1)
        dia_asumido_1 = int(inicio_nomina <= ini <= fin_nomina)
        dia_asumido_2 = int(inicio_nomina <= segundo_dia <= fin_nomina)
        dias_asumidos = dia_asumido_1 + dia_asumido_2 if dias != 1 else dia_asumido_1

        if pago_incapacidad == "NO":
            ibc = round(ibc * 2 / 3, 0)
            
        if ibc < salario_minimo:
            ibc = salario_minimo


        idconceptoi, idconceptoa = return_tipo_incapacidad(tipo, idcontrato.id_empresa)
        inicio_real = max(ini, inicio_nomina)
        fin_real = min(fin, fin_nomina)

        if inicio_real > fin_real:
            dias_incapacidad = 0
            continue
        else:
            dias_incapacidad = (fin_real - inicio_real).days + 1

            dias_incapacidad -= dias_asumidos

        if prorroga:    

            dias_asumidos = 0
            dias_incapacidad = calculo_incapacidad(idcontrato.idcontrato, nomina)
            ibc = disabilities_ibc(idcontrato , str(inicio_nomina) )
            valor_incapacidad = (ibc / 30 ) * dias_incapacidad

            valor_incapacidad = (
                Decimal(ibc) / Decimal('30') * Decimal(dias_incapacidad)
            ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

            if dias_incapacidad > 0:
                print('incapacidad prorroga')
                data_calculada.append({
                    'codigo': idconceptoi.codigo,
                    'nombre': idconceptoi.nombreconcepto,
                    'valor':  float(valor_incapacidad),
                    'cantidad': float(dias_incapacidad),
                })
                
            break

        else : 
            
            
            valor_incapacidad = (
                Decimal(ibc) / Decimal('30') * Decimal(dias_incapacidad)
            ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

            valor_asumido = (
                Decimal(ibc) / Decimal('30') * Decimal(dias_asumidos)
            ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

            if dias_incapacidad > 0:
                data_calculada.append({
                    'codigo': idconceptoi.codigo,
                    'nombre': idconceptoi.nombreconcepto,
                    'valor':  float(valor_incapacidad),
                    'cantidad': float(dias_incapacidad),
                })

            if dias_asumidos > 0:
                data_calculada.append({
                    'codigo': idconceptoa.codigo,
                    'nombre': idconceptoa.nombreconcepto,
                    'valor':  float(valor_asumido),
                    'cantidad': float(dias_asumidos),
                })

    return {
            'nomina': data_calculada,
            'calculada': data_calculada,
        }


def deductions_audit_employee(payroll_id, contrato):
    data = []
    data_audit = []
    data_calculada = []


    # ==========================================
    # Deducciones de préstamos
    # ==========================================

    # Obtener la nómina actual
    nomina_actual = Crearnomina.objects.get(idnomina=payroll_id)


    # Concepto del préstamo
    conceptosdenomina = Conceptosdenomina.objects.get(
        codigo=50,
        id_empresa=contrato.id_empresa_id
    )

    loans = Prestamos.objects.filter(
        idcontrato = contrato,
        estadoprestamo=True
    ).order_by('-idprestamo')


    for load in loans:
        valor = load.valorprestamo
        fecha = load.fechaprestamo

        if fecha is None:
            break

        if fecha > nomina_actual.fechafinal:
            continue
        

        # Deducciones anteriores de este préstamo
        deducciones = Nomina.objects.filter(
            idconcepto=conceptosdenomina,
            control=load.idprestamo,
        )

        suma_deducciones = deducciones.aggregate(
            total=Sum('valor')
        )['total'] or 0

        if deducciones.exists():
            if (load.valorprestamo + suma_deducciones) > load.valorcuota:
                valor = load.valorcuota
            else:
                valor = load.valorprestamo + suma_deducciones

            if valor != 0:

                data.append({
                    'codigo': '50',
                    'nombre': 'Prestamo a Empleados',
                    'valor': -1 * valor,
                    'cantidad': 1,  
                })
        else:
            valor = load.valorcuota
            if valor != 0:

                data.append({
                    'codigo': '50',
                    'nombre': 'Prestamo a Empleados',
                    'valor': -1 * valor,
                    'cantidad': 1,  
                })

    # ==========================================
    # Deducciones de préstamos
    # ==========================================
    
    # ==========================================
    # Deducciones de Novedades Fijas
    # ==========================================
    novs = list(NovFijos.objects.filter(idcontrato=contrato, estado_novfija=True).order_by('-idnovfija'))
    if novs:

        created_count = 0

        for nov in novs:
            valor = getattr(nov, 'valor', 0) or 0
            
            if nomina_actual.diasnomina < 16:
                valor = valor / 2

            cantidad = 1

            if nov.idconcepto.codigo == 91:
                data.append({
                    'codigo': nov.idconcepto.codigo,
                    'nombre': nov.idconcepto.nombreconcepto,
                    'valor': float(valor),
                    'cantidad': float(cantidad),
                })

            else:
                data.append({
                    'codigo': nov.idconcepto.codigo,
                    'nombre': nov.idconcepto.nombreconcepto,
                    'valor':float(valor),
                    'cantidad': float(cantidad),
                })

    # ==========================================
    # Deducciones de Novedades Fijas
    # ==========================================


    # ==========================================
    # Deducciones de suspensiones , vacaciones y licencias
    # ==========================================

    vacaciones = Vacaciones.objects.filter(
        idcontrato=contrato,
        tipovac__idvac__in=[3, 4, 5]
    )

    for vaca in vacaciones:
        if not vaca.fechainicialvac or not vaca.ultimodiavac:
            continue

        concepto1 = None
        concepto2 = None
        if vaca.fechainicialvac <= nomina_actual.fechafinal and vaca.ultimodiavac >= nomina_actual.fechainicial:
            
            # Definir conceptos según tipo
            if vaca.tipovac.idvac == 4:
                concepto1 = Conceptosdenomina.objects.get(
                    codigo=31,
                    id_empresa_id=contrato.id_empresa_id
                )
                concepto2 = Conceptosdenomina.objects.get(
                    codigo=83,
                    id_empresa_id=contrato.id_empresa_id
                )

            elif vaca.tipovac.idvac == 3:
                concepto2 = Conceptosdenomina.objects.get(
                    codigo=82,
                    id_empresa_id=contrato.id_empresa_id
                )

            elif vaca.tipovac.idvac == 5:
                concepto1 = Conceptosdenomina.objects.get(
                    codigo=30,
                    id_empresa_id=contrato.id_empresa_id
                )
                concepto2 = Conceptosdenomina.objects.get(
                    codigo=86,
                    id_empresa_id=contrato.id_empresa_id
                )

            dias_suspensiones = calcular_suspenciones2(
                vaca,
                nomina_actual
            )

            if dias_suspensiones <= 0:
                continue

            mes = vaca.fechainicialvac.month
            anio = vaca.fechainicialvac.year

            salario = salario_mes(contrato,mes,anio)

            dias =  salario / 30
            valor_calculado = dias * dias_suspensiones

            if vaca.tipovac.idvac != 3 and concepto1:
                data.append({
                    'codigo': concepto1.codigo,
                    'nombre': concepto1.nombreconcepto,
                    'valor': float(valor_calculado),
                    'cantidad': float(dias_suspensiones),
                })

                data.append({
                    'codigo': concepto2.codigo,
                    'nombre': concepto2.nombreconcepto,
                    'valor': -1 * float(valor_calculado),
                    'cantidad': float(dias_suspensiones),
                })
            else : 
                data.append({
                    'codigo': concepto2.codigo,
                    'nombre': concepto2.nombreconcepto,
                    'valor': float(-valor_calculado),
                    'cantidad': float(dias_suspensiones),
                })

    # ==========================================
    # Deducciones de suspensiones
    # ==========================================

    print('------------')
    print(data)
    print('------------')
    return data

def error_salary_audit(payroll_id):

    errors_count = 0
    errors_list = []
    contratos_cache = {}

    getcontext().prec = 50

    nomina = Crearnomina.objects.select_related('anoacumular').get(idnomina=payroll_id)

    salario_anual = Salariominimoanual.objects.get(ano=nomina.anoacumular.ano)
    sal_min = salario_anual.salariominimo
    aux_tra = salario_anual.auxtransporte

    mes = nomina.fechainicial.month
    anio = nomina.fechainicial.year

    conceptos = [1, 4, 33, 34]

    registros = Nomina.objects.select_related(
        'idcontrato__idempleado',
        'idconcepto'
    ).filter(
        idnomina_id=payroll_id,
        idconcepto__codigo__in=conceptos,
    )

    for data in registros:

        contrato = data.idcontrato
        empleado = contrato.idempleado
        codigo = data.idconcepto.codigo
        contrato_id = contrato.idcontrato

        # ==========================================
        # CACHE POR CONTRATO
        # ==========================================
        if contrato_id not in contratos_cache:
            salario = salario_mes(contrato, mes, anio)
            acumulados = precargar_acumulados(nomina,codigo)

            contratos_cache[contrato_id] = {
                "salario": Decimal(salario),
                "acumulados": acumulados
            }

        salario = contratos_cache[contrato_id]["salario"]
        acumulados = contratos_cache[contrato_id]["acumulados"]
        
        # ==========================================
        # DIAS
        # ==========================================
        diasnomina = calcular_dias(contrato, nomina, codigo, acumulados)
        # ==========================================
        # VALIDACIONES BASE
        # ==========================================
        valor = Decimal('0')

        valor = (
            salario * Decimal(diasnomina) / Decimal('30')
        ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

        # ==========================================
        # ERROR 1: VALOR INCORRECTO
        # ==========================================
        if not _qty_equal(data.cantidad, diasnomina):
            errors_list.append(
                f"[BASE] {contrato_id} → "
                f"Días incorrectos ({data.cantidad} vs {diasnomina}) "
                f"→ Esto afecta el salario ({data.valor} vs {valor})"
            )
            errors_count += 1

        elif not _money_equal(data.valor, valor):
            errors_list.append(
                f"[SALARIO] {contrato_id} → "
                f"Actual: {data.valor} | Esperado: {valor}"
            )
            errors_count += 1

        # ==========================================
        # VALIDACIONES UGPP
        # ==========================================

        # ERROR 3: SALARIO POR DEBAJO DEL MINIMO
        #if codigo == 1 and salario < sal_min:
        #    errors_list.append(
        #        f"[MINIMO] {contrato_id} "
        #        f"tiene salario menor al mínimo ({salario} < {sal_min})"
        #    )
        #    errors_count += 1

        # ERROR 4: DIAS MAYORES A 30
        if diasnomina > 30:
            errors_list.append(
                f"[DIAS_EXCESO] {contrato_id} "
                f"tiene más de 30 días ({diasnomina})"
            )
            errors_count += 1

        # ERROR 5: APRENDIZ MAL LIQUIDADO
        if codigo in [33, 34] and salario >= sal_min:
            errors_list.append(
                f"[APRENDIZ] {contrato_id} "
                f"tiene salario de aprendiz sospechoso ({salario})"
            )
            errors_count += 1

        # ERROR 6: SALARIO INTEGRAL BAJO (13 SMMLV aprox)
        if codigo == 4 and salario < (sal_min * 13):
            errors_list.append(
                f"[INTEGRAL] {contrato_id} "
                f"tiene salario integral bajo ({salario})"
            )
            errors_count += 1

    return errors_count, errors_list


def error_transport_audit(payroll_id):

    errors_count = 0
    errors_list = []
    contratos_cache = {}

    getcontext().prec = 50

    nomina = Crearnomina.objects.select_related('anoacumular').get(idnomina=payroll_id)

    salario_anual = Salariominimoanual.objects.get(ano=nomina.anoacumular.ano)
    sal_min = salario_anual.salariominimo
    aux_tra = salario_anual.auxtransporte

    mes = nomina.fechainicial.month
    anio = nomina.fechainicial.year

    # SOLO TRANSPORTE
    registros = Nomina.objects.select_related(
        'idcontrato',
        'idconcepto'
    ).filter(
        idnomina_id=payroll_id,
        idconcepto__codigo=2,
    )

    for data in registros:

        contrato = data.idcontrato
        contrato_id = contrato.idcontrato
        codigo = 2

        # ==========================================
        # CACHE POR CONTRATO
        # ==========================================
        if contrato_id not in contratos_cache:

            salario = salario_mes(contrato, mes, anio)
            acumulados = precargar_acumulados(nomina,codigo)

            contratos_cache[contrato_id] = {
                "salario": Decimal(salario),
                "acumulados": acumulados
            }

        salario = contratos_cache[contrato_id]["salario"]
        acumulados = contratos_cache[contrato_id]["acumulados"]

        # ==========================================
        # DIAS
        # ==========================================
        diasnomina = calcular_dias(contrato, nomina, codigo, acumulados)

        # ==========================================
        # VALIDACIONES 
        # ==========================================

        # 1. SI SALARIO >= 2 SMMLV → NO DEBE EXISTIR
        if salario >= (sal_min * 2):
            errors_list.append(
                f"[TRANSPORTE] {contrato_id} → "
                f"No debería tener auxilio (salario {salario} >= 2 SMMLV)"
            )
            errors_count += 1
            continue

        # BASE TRANSPORTE
        total_base_trans = Nomina.objects.filter(
            idcontrato=contrato,
            idnomina_id=payroll_id,
            idconcepto__indicador__nombre='basetransporte'
        ).exclude(
            idconcepto__codigo=2
        ).aggregate(total=Sum('valor'))['total'] or 0

        # 2. BASE <= 0 → NO DEBE EXISTIR
        if total_base_trans <= 0:
            errors_list.append(
                f"[TRANSPORTE] {contrato_id} → "
                f"No debería existir (base transporte = {total_base_trans})"
            )
            errors_count += 1
            continue

        # 3. BASE >= 2 SMMLV → NO DEBE EXISTIR
        if total_base_trans >= (sal_min * 2):
            errors_list.append(
                f"[TRANSPORTE] {contrato_id} → "
                f"No debería existir (base transporte >= 2 SMMLV)"
            )
            errors_count += 1
            continue

        # ==========================================
        # CALCULO ESPERADO
        # ==========================================
        valor_esperado = (
            Decimal(diasnomina) *
            (Decimal(aux_tra) / Decimal('30'))
        ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

        # ==========================================
        # ERRORES
        # ==========================================
        if not _qty_equal(data.cantidad, diasnomina):
            errors_list.append(
                f"[TRANSPORTE_DIAS] {contrato_id} → "
                f"Actual: {data.cantidad} | Esperado: {diasnomina}"
            )
            errors_count += 1

        elif not _money_equal(data.valor, valor_esperado):
            errors_list.append(
                f"[TRANSPORTE_VALOR] {contrato_id} → "
                f"Actual: {data.valor} | Esperado: {valor_esperado}"
            )
            errors_count += 1

    return errors_count, errors_list


def error_contributions_audit(payroll_id):

    errors_count = 0
    errors_list = []
    contratos_cache = {}

    getcontext().prec = 50

    nomina = Crearnomina.objects.select_related('anoacumular').get(idnomina=payroll_id)

    # ==========================================
    # PARAMETROS
    # ==========================================
    EPS = Conceptosfijos.objects.get(idfijo=8)
    AFP = Conceptosfijos.objects.get(idfijo=10)
    tope_ibc = Conceptosfijos.objects.get(idfijo=2)
    factor_integral = Conceptosfijos.objects.get(idfijo=1).valorfijo

    # FSP
    fsp416 = Conceptosfijos.objects.get(idfijo=12).valorfijo
    fsp1617 = Conceptosfijos.objects.get(idfijo=13).valorfijo
    fsp1718 = Conceptosfijos.objects.get(idfijo=14).valorfijo
    fsp1819 = Conceptosfijos.objects.get(idfijo=15).valorfijo
    fsp1920 = Conceptosfijos.objects.get(idfijo=16).valorfijo
    fsp21 = Conceptosfijos.objects.get(idfijo=17).valorfijo

    sal_min = Salariominimoanual.objects.get(
        ano=nomina.anoacumular.ano
    ).salariominimo

    # ==========================================
    # TRAER APORTES
    # ==========================================
    registros = Nomina.objects.select_related(
        'idcontrato',
        'idconcepto'
    ).filter(
        idnomina_id=payroll_id,
        idconcepto__codigo__in=[60, 70, 90]
    )

    for data in registros:

        contrato = data.idcontrato
        contrato_id = contrato.idcontrato
        codigo = data.idconcepto.codigo

        # ==========================================
        # CACHE POR CONTRATO
        # ==========================================
        if contrato_id not in contratos_cache:

            total_base_ss = Nomina.objects.filter(
                idcontrato=contrato,
                idnomina_id=payroll_id,
                
                idconcepto__indicador__nombre='basesegsocial'
            ).exclude(
                idconcepto__codigo__in=[60, 70, 90]
            ).aggregate(total=Sum('valor'))['total'] or 0

            # BASE FSP (ACUMULADA)
            base_ss_fsp = Nomina.objects.filter(
                idcontrato=contrato,
                idnomina__mesacumular=nomina.mesacumular,
                idnomina__anoacumular=nomina.anoacumular,
                idconcepto__indicador__nombre='basesegsocial'
            ).exclude(
                idconcepto__codigo__in=[60, 70, 90]
            ).aggregate(total=Sum('valor'))['total'] or 0

            # INTEGRAL
            if contrato.tiposalario.idtiposalario == 2:
                total_base_ss *= (factor_integral / 100)
                base_ss_fsp2 = base_ss_fsp * Decimal('0.7')
            else:
                base_ss_fsp2 = base_ss_fsp

            base_max = sal_min * tope_ibc.valorfijo
            base_ss = min(total_base_ss, base_max)

            base_ss = Decimal(base_ss).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

            contratos_cache[contrato_id] = {
                "base_ss": base_ss,
                "base_ss_fsp2": Decimal(base_ss_fsp2)
            }

        base_ss = contratos_cache[contrato_id]["base_ss"]
        base_ss_fsp2 = contratos_cache[contrato_id]["base_ss_fsp2"]

        # ==========================================
        # CALCULO ESPERADO
        # ==========================================

        # EPS
        if codigo == 60:
            valor_esperado = (
                base_ss * Decimal(EPS.valorfijo) / Decimal('100')
            ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

            valor_esperado = -1 * valor_esperado

        # PENSION
        elif codigo == 70:
            valor_esperado = (
                base_ss * Decimal(AFP.valorfijo) / Decimal('100')
            ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

            if contrato.pensionado == '2':
                valor_esperado = Decimal('0')

            valor_esperado = -1 * valor_esperado

        # FSP
        elif codigo == 90:

            # Determinar porcentaje
            if base_ss_fsp2 <= (sal_min * 4):
                FSP = 0
            elif base_ss_fsp2 > (sal_min * 20):
                FSP = fsp21
            elif base_ss_fsp2 > (sal_min * 19):
                FSP = fsp1920
            elif base_ss_fsp2 > (sal_min * 18):
                FSP = fsp1819
            elif base_ss_fsp2 > (sal_min * 17):
                FSP = fsp1718
            elif base_ss_fsp2 > (sal_min * 16):
                FSP = fsp1617
            elif base_ss_fsp2 > (sal_min * 4):
                FSP = fsp416
            else:
                FSP = 0

            if FSP > 0:
                valor_esperado = (
                    base_ss_fsp2 * Decimal(FSP) / Decimal('100')
                ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            else:
                valor_esperado = Decimal('0')

            if contrato.pensionado == '2':
                valor_esperado = Decimal('0')

            valor_esperado = -1 * valor_esperado

        else:
            continue

        # ==========================================
        # ERRORES
        # ==========================================
        if not _money_equal(data.valor, valor_esperado):
            errors_list.append(
                f"[APORTE] {contrato_id} → "
                f"Cod:{codigo} | Actual: {data.valor} | Esperado: {valor_esperado}"
            )
            errors_count += 1


    return errors_count, errors_list




def get_audit_salaries(payroll_id):

    queryset = Nomina.objects.filter(
        idnomina_id=payroll_id,
        estadonomina=1
    )

    data = queryset.aggregate(
        normales=Sum('valor', filter=Q(idconcepto__codigo=1)),
        normales_count=Count('idregistronom', filter=Q(idconcepto__codigo=1)),

        integral=Sum('valor', filter=Q(idconcepto__codigo=4)),
        integral_count=Count('idregistronom', filter=Q(idconcepto__codigo=4)),

        aprendices=Sum('valor', filter=Q(idconcepto__codigo__in=[33, 34])),
        aprendices_count=Count('idregistronom', filter=Q(idconcepto__codigo__in=[33, 34])),

        otros=Sum('valor', filter=Q(idconcepto__codigo=41)),
        otros_count=Count('idregistronom', filter=Q(idconcepto__codigo=41)),
    )

    # limpiar None → 0
    return {k: v or 0 for k, v in data.items()}
    

def get_audit_contributions(payroll_id):

    queryset = Nomina.objects.filter(
        idnomina_id=payroll_id,
        estadonomina=1
    )

    data = queryset.aggregate(
        eps=Sum('valor', filter=Q(idconcepto__codigo=60)),
        eps_count=Count('idregistronom', filter=Q(idconcepto__codigo=60)),

        pension=Sum('valor', filter=Q(idconcepto__codigo=70)),
        pension_count=Count('idregistronom', filter=Q(idconcepto__codigo=70)),

        fsp=Sum('valor', filter=Q(idconcepto__codigo=90)),
        fsp_count=Count('idregistronom', filter=Q(idconcepto__codigo=90)),

        incapacidades=Sum('valor', filter=Q(idconcepto__codigo__in=[25, 26, 27, 28])),
        incapacidades_count=Count('idregistronom', filter=Q(idconcepto__codigo__in=[25, 26, 27, 28])),
    )

    return {k: v or 0 for k, v in data.items()}


def get_audit_employees(payroll_id):
    queryset = Nomina.objects \
        .select_related('idcontrato') \
        .filter(idnomina=payroll_id, estadonomina=1) \
        .values(
            'idcontrato'
        ) \
        .distinct()

    return queryset.count()


def get_audit_total_to_pay(payroll_id):
    queryset = Nomina.objects.filter(
        idnomina_id=payroll_id,
        estadonomina=1
    )
    return queryset.aggregate(total=Sum('valor'))['total'] or 0


