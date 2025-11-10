from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.components.decorators import role_required
from apps.common.models import Nomina, Contratos
from apps.payroll.forms.filter_basic_form import FilterBasicForm
from django.db.models import Sum, Q


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
                    'idcontrato', 'idempleado__docidentidad', 'idempleado__papellido',
                    'idempleado__sapellido', 'idempleado__pnombre', 'idempleado__snombre',
                    'fechainiciocontrato', 'cargo__nombrecargo', 'salario',
                    'idcosto__idcosto', 'tipocontrato__tipocontrato',
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

            # 5️⃣ Calcular valores finales
            for contrato in contratos_filtrados:
                salario = contrato.get('salario', 0) or 0

                cesantias = salario * 0.0833
                intereses = salario * 0.01
                prima = salario * 0.0833
                vacaciones = salario * 0.0417
                total = cesantias + intereses + prima + vacaciones

                bases = bases_dict.get(contrato['idcontrato'], {})
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
                    'base_ss': bases.get('base_ss', 0),
                    'base_arl': bases.get('base_arl', 0),
                    'base_caja': bases.get('base_caja', 0),
                    'variable': bases.get('variable', 0),
                    'cesantias': cesantias,
                    'intereses': intereses,
                    'prima': prima,
                    'vacaciones': vacaciones,
                    'total': total,
                    'centrocostos': clean_value(contrato.get('idcosto__idcosto')),
                    'idcontrato': contrato['idcontrato'],
                }
                empleados.append(empleado_data)

    return render(
        request,
        './payroll/social_security_provision.html',
        {'empleados': empleados, 'form': form}
    )
