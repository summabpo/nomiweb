from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.components.decorators import role_required
from apps.common.models import Nomina, Contratos , Conceptosfijos
from apps.payroll.forms.filter_basic_form import FilterBasicForm
from django.db.models import Sum, Q
import calendar
from datetime import date
from decimal import Decimal

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

            # 1️⃣ Contratos activos
            contratos_empleados = (
                Contratos.objects
                .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede', 'centrotrabajo')
                .filter(estadocontrato=1, id_empresa=idempresa)
                .order_by('idempleado__papellido')
                .values(
                    'idcontrato', 'idempleado__docidentidad', 'idempleado__papellido','fechainiciocontrato' ,'fechafincontrato',
                    'idempleado__sapellido', 'idempleado__pnombre', 'idempleado__snombre',
                    'fechainiciocontrato', 'cargo__nombrecargo', 'salario',
                    'idcosto__nomcosto', 'tipocontrato__tipocontrato',
                    'centrotrabajo__tarifaarl'
                )
            )

            # 2️⃣ Bases por contrato (una sola consulta agregada)
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

            # 3️⃣ Convertir a diccionario para acceso rápido (sin queries adicionales)
            bases_dict = {
                b['idcontrato']: {
                    'base_ss': b['base_ss'] or 0,
                    'base_arl': b['base_arl'] or 0,
                    'base_caja': b['base_caja'] or 0,
                }
                for b in bases_por_contrato
            }
            
            
            

            # 4️⃣ Filtrar contratos activos que estén en nómina
            contratos_filtrados = [
                c for c in contratos_empleados if c['idcontrato'] in bases_dict
            ]
            
            cc = Decimal(Conceptosfijos.objects.get(conceptofijo='CESANTIAS').valorfijo)
            icc = Decimal(Conceptosfijos.objects.get(conceptofijo='Intereses de Cesantias').valorfijo)
            vac = Decimal(Conceptosfijos.objects.get(conceptofijo='Vacaciones').valorfijo)

            
            
            # Tarifas empleador (ajústalas si usas otras)
            t_salud_empleador = Decimal(Conceptosfijos.objects.get(conceptofijo='EPS - EMPRESA').valorfijo)
            t_pension_empleador = Decimal(Conceptosfijos.objects.get(conceptofijo='PENSION - EMPRESA').valorfijo)
            t_sena = Decimal(Conceptosfijos.objects.get(conceptofijo='APORTE SENA').valorfijo)
            t_icbf = Decimal(Conceptosfijos.objects.get(conceptofijo='APORTE ICBF').valorfijo)
            t_caja = Decimal(Conceptosfijos.objects.get(conceptofijo='APORTE CAJA DE COMPENSACION').valorfijo)  
            t_fsp = 1  

            for contrato in contratos_filtrados:

                bases = bases_dict.get(contrato['idcontrato'], {})
                salario = contrato.get('salario', 0) or 0

                cesantias = salario * (cc / Decimal(100))
                intereses = salario * (icc / Decimal(100))
                prima = salario * (cc / Decimal(100))
                vacaciones = salario * (vac / Decimal(100))
                provision = cesantias + intereses + prima + vacaciones

                dias = dias_contrato(contrato, mst_init, year_init)
                salud_trab, pension_trab = salud_pension(contrato, bases.get('base_ss', 0))

                base_ss = bases.get('base_ss', 0)
                base_arl = bases.get('base_arl', 0)
                base_caja = bases.get('base_caja', 0)

                # Aportes empleador
                eps = base_ss * (t_salud_empleador / 100)
                afp = base_ss * (t_pension_empleador / 100)
                arl = base_arl * (contrato.get('centrotrabajo__tarifaarl', 0) / 100)
                sena = base_ss * (t_sena / 100)
                icbf = base_ss * (t_icbf / 100)
                caja = base_caja * (t_caja / 100)

                salario = Decimal(str(contrato.get('salario', 0) or 0))
                base_ss = Decimal(str(bases.get('base_ss', 0)))
                base_arl = Decimal(str(bases.get('base_arl', 0)))
                base_caja = Decimal(str(bases.get('base_caja', 0)))
                variable = Decimal(str(bases.get('variable', 0)))
                # FSP
                fsp = base_ss * (t_fsp / 100) if salario > 4 * 1300000 else 0  # Ajusta SMMLV

                # Ajuste (opcional)
                ajuste = base_ss - salario

                total_aportes = 0

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
                    'cesantias': cesantias,
                    'intereses': intereses,
                    'dias': dias,
                    'salud': salud_trab,
                    'pension': pension_trab,
                    'prima': prima,
                    'vacaciones': vacaciones,
                    'total': provision,
                    
                    'suspension_contrato': 0,
                    'ajuste': ajuste,
                    'arl': arl,
                    'sena': sena,
                    'icbf': icbf,
                    'salud_trabajador': salud_trab,
                    'pension_trabajador': pension_trab,
                    'fsp': fsp,
                    'total_aportes': total_aportes,
                    'provision': provision,
                    'afp': afp,
                    'eps': eps,
                    'caja': caja,
                    'centro_costo': clean_value(contrato.get('idcosto__nomcosto')),
                    'idcontrato': contrato['idcontrato'],
                }

                empleados.append(empleado_data)

    return render(
        request,
        './payroll/social_security_provision.html',
        {'empleados': empleados, 'form': form}
    )


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

def salud_pension(contrato , base ):
    salud  = pension  = 0
    
    ps = Decimal(Conceptosfijos.objects.get(conceptofijo='EPS - Empleado').valorfijo)
    pp = Decimal(Conceptosfijos.objects.get(conceptofijo='PENSION - EMPLEADO').valorfijo)

    
    salud = -(base * (ps / Decimal(100)))
    pension = -(base * (pp / Decimal(100)))
    
    return salud , pension 