from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.components.decorators import role_required
from apps.common.models import Nomina, Contratos , Conceptosfijos , Salariominimoanual
from apps.payroll.forms.filter_basic_form import FilterBasicForm
from django.db.models import Sum, Q
import calendar
from datetime import date ,datetime
from decimal import Decimal
from decimal import Decimal, ROUND_HALF_UP
from apps.components.salary import salario_mes


MESES_MAP = {
    'ENERO': 1, 'FEBRERO': 2, 'MARZO': 3, 'ABRIL': 4, 'MAYO': 5, 'JUNIO': 6,
    'JULIO': 7, 'AGOSTO': 8, 'SEPTIEMBRE': 9, 'OCTUBRE': 10, 'NOVIEMBRE': 11, 'DICIEMBRE': 12,
}

@login_required
@role_required('accountant')
def social_security_provision(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario.get('idempresa')
    form = FilterBasicForm()
    empleados = []

    def clean_value(value):
        """Limpia valores tipo texto que indiquen falta de datos."""
        if isinstance(value, str) and value.strip().lower() in ["no data", "sin dato", "n/a", "none", "ninguno"]:
            return ""
        return value

    if request.method == 'POST':
        form = FilterBasicForm(request.POST)
        if form.is_valid():
            mst_init = request.POST.get('mst_init')
            year_init = request.POST.get('year_init')

            # Contratos activos ,idcontrato = 8137
            contratos_empleados = (
                Contratos.objects
                .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede', 'centrotrabajo')
                .filter(estadocontrato=1, id_empresa=idempresa )
                .order_by('idempleado__papellido')
                .values(
                    'idcontrato', 'idempleado__docidentidad', 'idempleado__papellido','fechainiciocontrato' ,'fechafincontrato',
                    'idempleado__sapellido', 'idempleado__pnombre', 'idempleado__snombre',
                    'fechainiciocontrato', 'cargo__nombrecargo', 'salario',
                    'idcosto__nomcosto', 'tipocontrato__tipocontrato','tiposalario__idtiposalario',
                    'centrotrabajo__tarifaarl','codafp__entidad' , 'codeps__entidad' , 'codccf__entidad'
                )
            )

            #  Bases por contrato (una sola consulta agregada)
            bases_por_contrato = (
                Nomina.objects.filter(
                    estadonomina=2,
                    idnomina__mesacumular=mst_init,
                    idnomina__anoacumular__ano=year_init,
                    idconcepto__id_empresa=idempresa
                )
                .values('idcontrato')
                .annotate(
                    base_ss=Sum('valor', filter=Q(idconcepto__indicador__nombre='basesegsocial')),
                    base_arl=Sum('valor', filter=Q(idconcepto__indicador__nombre='basearl')),
                    base_caja=Sum('valor', filter=Q(idconcepto__indicador__nombre='basecaja')),
                    variable=Sum(
                        'valor',
                        filter=Q(idconcepto__indicador__nombre='extras') | Q(idconcepto__indicador__nombre='comisiones')
                    ),
                )
            )

            SMMLV = Salariominimoanual.objects.get( ano = year_init ).salariominimo
            # Convertir a diccionario para acceso rápido (sin queries adicionales)
            
            TOPE_PARAFISCALES = SMMLV * 10
            TOPE_FSP = SMMLV * 4


            bases_dict = {
                b['idcontrato']: {
                    'base_ss': Decimal(str(b['base_ss'] or 0)),
                    'base_arl': Decimal(str(b['base_arl'] or 0)),
                    'base_caja': Decimal(str(b['base_caja'] or 0)),
                }
                for b in bases_por_contrato
            }


            contratos_filtrados = [
                c for c in contratos_empleados if c['idcontrato'] in bases_dict
            ]


            cc = Decimal(Conceptosfijos.objects.get(conceptofijo='CESANTIAS').valorfijo)
            icc = Decimal(Conceptosfijos.objects.get(conceptofijo='Intereses de Cesantias').valorfijo)
            cp = Decimal(Conceptosfijos.objects.get(conceptofijo='Prima de Servicios').valorfijo)
            vac = Decimal(Conceptosfijos.objects.get(conceptofijo='Vacaciones').valorfijo)


            t_salud_empleador = Decimal(Conceptosfijos.objects.get(conceptofijo='EPS - EMPRESA').valorfijo)
            t_pension_empleador = Decimal(Conceptosfijos.objects.get(conceptofijo='PENSION - EMPRESA').valorfijo)
            t_sena = Decimal(Conceptosfijos.objects.get(conceptofijo='APORTE SENA').valorfijo)
            t_icbf = Decimal(Conceptosfijos.objects.get(conceptofijo='APORTE ICBF').valorfijo)
            t_ccf = Decimal(Conceptosfijos.objects.get(conceptofijo='APORTE CAJA DE COMPENSACION').valorfijo)
            t_caja = Decimal(Conceptosfijos.objects.get(conceptofijo='APORTE CAJA DE COMPENSACION').valorfijo)


            for contrato in contratos_filtrados:
                contract = Contratos.objects.get(idcontrato = contrato['idcontrato'])
                mes = int(MESES_MAP[mst_init])
                salario = salario_mes(contract, mes, int(year_init))

                # 🔹 Base mensual según nómina

                base_ss = max(base_ssf(contrato, year_init, mst_init, 'basesegsocial'), salario)
                base_arl = max(base_ssf(contrato, year_init, mst_init, 'basearl'), salario)
                base_caja = max(base_ssf(contrato, year_init, mst_init, 'basecaja'), salario)
                base_c = max(base_ssf(contrato, year_init, mst_init, 'baseprima'), salario)
                base_p = max(base_ssf(contrato, year_init, mst_init, 'basevacaciones'), salario)


                if contrato['tiposalario__idtiposalario'] == 2 : 
                    factor = Decimal('0.7')
                    base_ss *= factor
                    base_arl *= factor
                    base_caja *= factor
                

                bases = bases_dict.get(contrato['idcontrato'], {})
                dias = dias_contrato(contrato, mst_init, year_init)

                salud_trab, pension_trab , salud_empresa , pension_empresa = salud_pension(contrato, base_ss , TOPE_PARAFISCALES)

                # =========================
                # PROVISIONES
                # =========================

                cesantias = (base_c * (cc/Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) # 1 mes / 12 meses
                intereses = (base_c * (icc / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)  # 12% anual proporcional mensual
                prima = (base_p * (cp / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) # 1 mes / 12 meses
                vacaciones = (salario * (vac / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                provision = cesantias + intereses + prima + vacaciones

                # =========================
                # APORTES EMPLEADOR
                # =========================

                afp = base_ss * (t_pension_empleador / 100)
                arl = base_arl * (Decimal(str(contrato.get('centrotrabajo__tarifaarl', 0))) / 100)
                caja = base_caja * (t_caja / 100)
                ## 'codafp__entidad' , 'codeps__entidad' , 'codccf__entidad'
                n_eps = contrato['codeps__entidad']
                n_afp = contrato['codafp__entidad']
                n_caja = contrato['codccf__entidad']

                # =========================
                # VALIDACION PARAFISCALES
                # =========================

                if salario >= TOPE_PARAFISCALES:

                    eps = base_ss * (t_salud_empleador / 100)
                    sena = base_ss * (t_sena / 100)
                    icbf = base_ss * (t_icbf / 100)
                    ccf = base_ss * (t_ccf / 100)

                else:
                    ccf = Decimal(0)
                    eps = Decimal(0)
                    sena = Decimal(0)
                    icbf = Decimal(0)

                # =========================
                # FONDO SOLIDARIDAD
                # =========================

                if salario >= TOPE_FSP:
                    fsp = base_ss * Decimal("0.01")
                else:
                    fsp = Decimal(0)

                # =========================
                # AJUSTE BASE
                # =========================

                ajuste = 0

                total_aportes = eps + afp + arl + sena + icbf + ccf + salud_trab + pension_trab + fsp + ajuste

                provision = total_aportes - salud_trab - pension_trab 

                empleado_data = {

                    'documento': clean_value(contrato.get('idempleado__docidentidad')),

                    'nombre': ' '.join(filter(None, map(clean_value, [
                        contrato.get('idempleado__papellido', ''),
                        contrato.get('idempleado__sapellido', ''),
                        contrato.get('idempleado__pnombre', ''),
                        contrato.get('idempleado__snombre', '')
                    ]))),

                    'fechainiciocontrato': clean_value(contrato.get('fechainiciocontrato')),
                    'cargo': clean_value(contrato.get('cargo__nombrecargo')),

                    'salario': salario,

                    'base_ss': base_ss,
                    'base_arl': base_arl,
                    'base_caja': base_caja,

                    'variable': bases.get('variable', 0),

                    'dias': dias,

                    'salud_empresa': salud_empresa,
                    'pension_empresa': pension_empresa,

                    'suspension_contrato': 0,

                    'ajuste': ajuste,

                    'arl': arl,
                    'ccf':ccf,
                    'sena': sena,
                    'icbf': icbf,

                    'salud_trabajador': -(salud_trab),
                    'pension_trabajador': -(pension_trab),

                    'fsp': -(fsp),

                    'total_aportes': total_aportes,

                    'provision': provision,

                    'afp': n_afp,
                    'eps': n_eps,
                    'caja': n_caja,

                    'centro_costo': clean_value(contrato.get('idcosto__nomcosto')),

                    'idcontrato': contrato['idcontrato'],
                }

                empleados.append(empleado_data)
                
    return render(request,'./payroll/social_security_provision.html',{'empleados': empleados, 'form': form})


MESES = {
    "ENERO": 1,
    "FEBRERO": 2,
    "MARZO": 3,
    "ABRIL": 4,
    "MAYO": 5,
    "JUNIO": 6,
    "JULIO": 7,
    "AGOSTO": 8,
    "SEPTIEMBRE": 9,
    "OCTUBRE": 10,
    "NOVIEMBRE": 11,
    "DICIEMBRE": 12,
}

def dias_contrato(contrato, month, year):
    # Convertir valores
    month_num = MESES[month.upper()]         
    year_num = int(year)                    

    # Primer y último día
    first_day = date(year_num, month_num, 1)
    last_day = date(year_num, month_num, calendar.monthrange(year_num, month_num)[1])

    dias = 0
    diasnomina = 30
    
    def _to_date(d):
        if d is None:
            return None
        if isinstance(d, datetime):
            return d.date()
        return d
        
        
    # Obtener fecha inicio según tipo
    if isinstance(contrato, dict):
        fecha_inicio = contrato["fechainiciocontrato"]
        fin_contrato =  _to_date(contrato["fechafincontrato"]) or last_day
    else:
        fecha_inicio = contrato.fechainiciocontrato
        fin_contrato = _to_date(contrato.fechafincontrato) or last_day

    
    inicio_periodo = max(first_day, fecha_inicio)
    fin_periodo = min(last_day, fin_contrato)
    
    if fin_periodo < inicio_periodo:
        diasnomina = 0
    else:
        diasnomina = (fin_periodo - inicio_periodo).days  
    
    # Lógica de días
    if fecha_inicio < first_day:
        dias = 30
    else : 
        dias = diasnomina

    return dias

def salud_pension(contrato , base , salario ):
    salud  = pension  = 0
    ps = Decimal(Conceptosfijos.objects.get(conceptofijo='EPS - Empleado').valorfijo)
    pp = Decimal(Conceptosfijos.objects.get(conceptofijo='PENSION - EMPLEADO').valorfijo)
    pse = Decimal(Conceptosfijos.objects.get(conceptofijo='EPS - EMPRESA').valorfijo)
    ppe = Decimal(Conceptosfijos.objects.get(conceptofijo='PENSION - EMPRESA').valorfijo)
    pse2 = Decimal(Conceptosfijos.objects.get(conceptofijo='EPS - Empresa para SMLV > 10').valorfijo)
    
    if int(contrato["salario"]) > salario : 
        aux = (base * (pse2 / Decimal(100)))
    else : 
        aux = (base * (pse / Decimal(100)))
    
    salud = (base * (ps / Decimal(100)))
    pension = (base * (pp / Decimal(100)))
    salud_e = aux 
    pension_e = (base * (ppe / Decimal(100)))
    
    return salud , pension , salud_e , pension_e 



def base_ssf(contrato, year, mes,familia):
    return Nomina.objects.filter(
        idcontrato=contrato['idcontrato'],
        estadonomina=2,
        idnomina__mesacumular=mes,
        idnomina__anoacumular__ano=year,
        idconcepto__indicador__nombre=familia
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0')



def base_cesantias_debug(contrato, year, mes,familia):
    queryset = Nomina.objects.filter(
        idcontrato=contrato['idcontrato'],
        estadonomina=2,
        idnomina__mesacumular=mes,
        idnomina__anoacumular__ano=year,
        idconcepto__indicador__nombre=familia
    )

    # 🔍 Ver cada registro individual
    detalles = queryset.values(
        'idconcepto__nombreconcepto'
    ).annotate(
        total=Sum('valor')
    )

    print(f"=== DETALLE BASE {familia} ===")
    for item in detalles:
        print(f"Concepto: {item['idconcepto__nombreconcepto']} | Valor: {item['total']}")

    # 🔢 Total general
    total = queryset.aggregate(total=Sum('valor'))['total'] or Decimal('0')

    print(f"TOTAL BASE CESANTÍAS: {total}")

    return total
