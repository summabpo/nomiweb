from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Tiempos , Crearnomina , Contratos ,Nomina,Conceptosdenomina, Empresa ,Conceptosfijos ,TiemposTotales ,Sedes, Costos, Subcostos, Empresa
from apps.payroll.forms.filter_basic_form import FilterBasicForm
from django.db.models import Q
from math import ceil
from apps.payroll.views.settlements.liquidacion_utils import *
import calendar

MESES_MAP = {
    'ENERO': 1,
    'FEBRERO': 2,
    'MARZO': 3,
    'ABRIL': 4,
    'MAYO': 5,
    'JUNIO': 6,
    'JULIO': 7,
    'AGOSTO': 8,
    'SEPTIEMBRE': 9,
    'OCTUBRE': 10,
    'NOVIEMBRE': 11,
    'DICIEMBRE': 12,
}



@login_required
@role_required('accountant')
def employee_benefits_provision(request):

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    form = FilterBasicForm()

    def clean_value(value):
        if isinstance(value, str):
            if value.strip().lower() in ["no data", "sin dato", "n/a", "none", "ninguno"]:
                return ""
        return value

    empleados = []

    if request.method == 'POST':

        form = FilterBasicForm(request.POST)

        if form.is_valid():
            
            mst_init = form.cleaned_data['mst_init']
            year_init = int(form.cleaned_data['year_init'])

            print('---------------------')
            print(mst_init)
            print(year_init)
            print('---------------------')


            # 🔹 Traer conceptos fijos UNA SOLA VEZ
            conceptos = Conceptosfijos.objects.filter(
                conceptofijo__in=[
                    'CESANTIAS',
                    'Intereses de Cesantias',
                    'Vacaciones'
                ]
            ).values_list('conceptofijo', 'valorfijo')

            conceptos_dict = {c[0]: c[1] for c in conceptos}

            cc = conceptos_dict.get('CESANTIAS', 0)
            icc = conceptos_dict.get('Intereses de Cesantias', 0)
            vac = conceptos_dict.get('Vacaciones', 0)

            # 🔹 Query de contratos
            contratos_empleados = (
                Contratos.objects
                .filter(estadocontrato=1, id_empresa=idempresa ,  idcontrato__in=[8137, 12070, 8132 ,7961])
                .select_related(
                    'idempleado',
                    'idcosto',
                    'tipocontrato',
                    'idsede',
                    'centrotrabajo',
                    'cargo'
                )
                .order_by('idempleado__papellido')
                .values(
                    'idempleado__docidentidad',
                    'idempleado__papellido',
                    'idempleado__sapellido',
                    'idempleado__pnombre',
                    'idempleado__snombre',
                    'fechainiciocontrato',
                    'cargo__nombrecargo',
                    'salario',
                    'idcosto__idcosto',
                    'centrotrabajo__tarifaarl',
                    'idempleado__idempleado',
                    'idcontrato',
                    'id_empresa',
                    'tiposalario__idtiposalario'
                )
            )

            for contrato in contratos_empleados:

                salario = contrato['salario'] or 0

                base_c = base_cesantias(contrato,year_init,mst_init)


                if contrato['tiposalario__idtiposalario']  == 2:
                    cesantias = intereses = prima = 0
                else:
                    cesantias = base_c * (cc / 100)
                    intereses = salario * (icc / 100)
                    prima = salario * (cc / 100)
                
                vacaciones = salario * (vac / 100)

                total = cesantias + intereses + prima + vacaciones

                nombre = " ".join(filter(None, [
                    clean_value(contrato.get('idempleado__papellido')),
                    clean_value(contrato.get('idempleado__sapellido')),
                    clean_value(contrato.get('idempleado__pnombre')),
                    clean_value(contrato.get('idempleado__snombre')),
                ]))

                empleados.append({
                    'documento': clean_value(contrato.get('idempleado__docidentidad')),
                    'nombre': nombre,
                    'fechainiciocontrato': contrato.get('fechainiciocontrato'),
                    'cargo': clean_value(contrato.get('cargo__nombrecargo')),
                    'salario': base_c,
                    'cesantias': cesantias,
                    'intereses': intereses,
                    'prima': prima,
                    'vacaciones': vacaciones,
                    'total': total,
                    'centrocostos': clean_value(contrato.get('idcosto__idcosto')),
                    'idcontrato': contrato.get('idcontrato'),
                })
    
    return render(request,'./payroll/employee_benefits_provision.html', {'empleados': empleados,'form': form, } )




def base_cesantias(contrato,year_init,mes):
    base = 0 

    base = Nomina.objects.filter(
        idcontrato=contrato['idcontrato'],
        estadonomina = 2 ,
        idnomina__mesacumular = mes , 
        idnomina__anoacumular__ano = year_init , 
        idconcepto__id_empresa = contrato['id_empresa'] ,
        idconcepto__indicador__nombre='baseprovisionA'
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    
    return base



def base_prima(contrato):
    base = 0 


    return base




