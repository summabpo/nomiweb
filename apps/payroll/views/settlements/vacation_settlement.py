
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models  import Contratosemp , Vacaciones ,Contratos , Tipoavacaus , EmpVacaciones,Nomina, Festivos
from apps.payroll.forms.VacationSettlementForm import VacationSettlementForm , BenefitFormSet
from datetime import datetime, timedelta, date
from django.http import JsonResponse
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
@role_required('accountant')
def vacation_settlement_add(request):
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = VacationSettlementForm(id_empresa=idempresa)
    vacaciones_list = {}
    
    
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
        
        contrato = request.POST.get("contract") #*
        fecha_pago = request.POST.get("pay_date")
        novedad = request.POST.get("novedad")
        fecha_inicio = request.POST.get("fecha_inicio-1")
        fecha_fin = request.POST.get("fecha_fin-1")
        sabados = request.POST.get("sabados-1")
        periodo1 = request.POST.get("fecha_periodo-1")
        periodo2 = request.POST.get("fecha_periodo-2")


        salario = disabilities_ibc(contrato , fecha_inicio )

        if salario == 0 :
            salario = Contratos.objects.get(idcontrato = contrato).salario
        #salario = Contratos.objects.get(idcontrato = contrato).salario

        if sabados == 'on':
            csabado = 1
        else :
            csabado = 0
    
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
                
        if not vacaciones_list: 
            vacaemp = EmpVacaciones.objects.create(
                idcontrato = Contratos.objects.get(idcontrato = contrato) ,
                tipovac = Tipoavacaus.objects.get(idvac = novedad ) , 
                fechainicialvac = fecha_inicio , 
                fechafinalvac = fecha_fin , 
                estado =  1,  # Estado de la solicitud (0: pendiente, 1: aprobado, 2: rechazado, etc.)
                diasvac =  int(dias_v) if dias_v else 0,
                cuentasabados = csabado ,
                estadovac = 1,
                diascalendario = int(dias_c) , 
                ip_usuario =   get_client_ip(request) , # Dirección IP del usuario que realiza la solicitud
                fecha_hora= datetime.now()  , # Fecha y hora de la solicitud
                comentarios = 'Generacion desde sistema Contador' , # Comentarios adicionales
                comentarios2 = 'Generacion desde sistema Contador' , # Comentarios adicionales (opcional)
            )
            
            id_master = vacaemp.id_sol_vac
            
        else : 
            primer_registro = vacaciones_list[0]
            id_master = primer_registro.idvacmaster
            

        vacacion = Vacaciones.objects.create( 
            idcontrato= Contratos.objects.get(idcontrato = contrato) ,
            fechainicialvac = fecha_inicio , 
            ultimodiavac = fecha_fin ,
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
            perinicio = periodo1,
            perfinal = periodo2, 
            fechapago = fecha_pago , 
            idvacmaster = id_master
            
            )


        vacaciones_list = Vacaciones.objects.filter(fechapago = fecha_pago , idcontrato_id = contrato )

        #vacaciones_list.append(vacacion)



    return render(request, './payroll/partials/vacation_settlement_add.html', {
        'form': form,
        'data': data ,
        'vacaciones_list':vacaciones_list ,
        
    })
    



def disabilities_ibc(contract, date):
    ibc = 0

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

    ibc = suma
    return ibc

@login_required
@role_required('accountant')
def vacation_settlement_add_list(request):
    
    pay_date = request.POST.get('pay_date')
    type_novedad = request.POST.get('type_novedad')
    
    contrato = request.POST.get('idc')

    vacaciones_list = Vacaciones.objects.filter(
        fechapago = pay_date ,
        idcontrato_id = contrato 
    ).values(
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

    
    return JsonResponse({
            'vacaciones_list':list(vacaciones_list),
        })


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




def vacation_days_calc(request):
    fecha_inicio = request.POST.get('fecha_inicio')
    fecha_fin = request.POST.get('fecha_fin')
    incluir_sabados = request.POST.get('incluir_sabados')
    contrato = request.POST.get('idc')
    
    dias_c = ''
    dias_v = ''


    salario = disabilities_ibc(contrato , fecha_inicio )

    if salario == 0 :
        salario = Contratos.objects.get(idcontrato = contrato).salario
    
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
            'salario':format_value_float(salario),
            'valor':valor,
        })
