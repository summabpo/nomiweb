from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Tiempos , Crearnomina , Contratos ,Nomina,Conceptosdenomina, Empresa ,Conceptosfijos ,TiemposTotales ,Sedes, Costos, Subcostos, Empresa
from apps.payroll.forms.filter_basic_form import FilterBasicForm


@login_required
@role_required('accountant')
def employee_benefits_provision(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = FilterBasicForm()
    
    def clean_value(value):
        """
        Limpia valores tipo texto que indiquen falta de datos.
        Ejemplo: 'no data', 'sin dato', 'n/a', 'none', 'ninguno'
        """
        if isinstance(value, str):
            if value.strip().lower() in ["no data", "sin dato", "n/a", "none", "ninguno"]:
                return ""
        return value
    
    if request.method == 'POST':
        form = FilterBasicForm(request.POST)
        if form.is_valid():
            empleados = []
            
            contratos_empleados = (
                Contratos.objects
                    .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede', 'centrotrabajo')
                    .order_by('idempleado__papellido')
                    .filter(estadocontrato=1, id_empresa=idempresa)
                    .values(
                        'idempleado__docidentidad', 'idempleado__papellido', 'idempleado__pnombre',
                        'idempleado__snombre', 'fechainiciocontrato', 'cargo__nombrecargo', 'salario',
                        'idcosto__idcosto', 'tipocontrato__tipocontrato', 'centrotrabajo__tarifaarl',
                        'idempleado__idempleado', 'idempleado__sapellido', 'idcontrato'
                    )
                )

            
            for contrato in contratos_empleados:
                salario = contrato['salario']
                
                cc = Conceptosfijos.objects.get(conceptofijo = 'CESANTIAS').valorfijo
                icc = Conceptosfijos.objects.get(conceptofijo = 'Intereses de Cesantias').valorfijo
                vac = Conceptosfijos.objects.get(conceptofijo = 'Vacaciones').valorfijo

                cesantias = salario * (cc/100)
                intereses = salario * (icc/100)  
                prima = salario * (cc/100)
                vacaciones = salario *(vac/100)  

                total = cesantias + intereses + prima + vacaciones

                empleado_data = {
                    'documento': clean_value(contrato.get('idempleado__docidentidad', '')),
                    'nombre': ' '.join(filter(None, map(clean_value, [
                        contrato.get('idempleado__papellido', ''),
                        contrato.get('idempleado__sapellido', ''),
                        contrato.get('idempleado__pnombre', ''),
                        contrato.get('idempleado__snombre', '')
                    ]))),
                    'fechainiciocontrato': clean_value(contrato.get('fechainiciocontrato', '')),
                    'cargo': clean_value(contrato.get('cargo__nombrecargo', '')),
                    'salario': salario,
                    'cesantias': cesantias,
                    'intereses': intereses,
                    'prima': prima,
                    'vacaciones': vacaciones,
                    'total': total, 
                    'centrocostos': clean_value(contrato.get('idcosto__idcosto', '')),
                    'idcontrato': contrato.get('idcontrato', ''),
                }

                empleados.append(empleado_data)
            
            #empleados = Contratos.objects.filter(id_empresa_id = idempresa)
    else:
        empleados = {}
    
    return render(request,'./payroll/employee_benefits_provision.html', {'empleados': empleados,
        'form': form, } )
