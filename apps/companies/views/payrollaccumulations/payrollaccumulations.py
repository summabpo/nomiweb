from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Liquidacion , Nomina
from apps.companies.forms.ReportFilterForm import ReportFilterForm
from django.contrib import messages
from django.http import HttpResponse
from apps.components.generate_employee_excel import generate_employee_excel
from apps.components.humani import format_value


def payrollaccumulations(request):
    acumulados = {}
    compects = []

    if request.method == 'POST':
        form = ReportFilterForm(request.POST)
        if form.is_valid():
            # Obtener los parámetros de búsqueda del formulario
            employee = form.cleaned_data['employee']
            cost_center = form.cleaned_data['cost_center']
            city = form.cleaned_data['city']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            
            # Aplicar filtros a la consulta de Nomina
            nominas = Nomina.objects.all()
            if employee:
                nominas = nominas.filter(idempleado__idempleado=employee)
            if cost_center:
                nominas = nominas.filter(idcontrato__idcosto=cost_center)
            if city:
                nominas = nominas.filter(idcontrato__idsede=city)
            if start_date:
                nominas = nominas.filter(idnomina__fechainicial__gte=start_date)
            if end_date:
                nominas = nominas.filter(idnomina__fechafinal__lte=end_date)
            
            # Acumular los datos
            for data in nominas:
                docidentidad = data.idempleado.docidentidad
                if docidentidad not in acumulados:
                    acumulados[docidentidad] = {
                        'documento': docidentidad,
                        'empleado': f"{data.idempleado.papellido} {data.idempleado.sapellido} {data.idempleado.pnombre} {data.idempleado.snombre}",
                        'contrato': data.idcontrato.idcontrato,
                        'basico': 0,
                        'aportess': 0,
                        'prestamos': 0,
                        'total': 0,
                    }
                acumulados[docidentidad]['basico'] += data.valor if data.idconcepto.sueldobasico == 1 else 0
                acumulados[docidentidad]['aportess'] += data.valor if data.idconcepto.aportess == 1 else 0
                acumulados[docidentidad]['prestamos'] += data.valor if data.idconcepto.idconcepto == 50 else 0
            
            # Procesar los datos acumulados
            compects = list(acumulados.values())
            for compect in compects:
                compect['total'] = compect['basico'] - compect['aportess'] - compect['prestamos']
                for key in ['basico', 'aportess', 'prestamos', 'total']:
                    compect[key] = format_value(compect[key])
            
            return render(request, 'companies/payrollaccumulations.html', {
                'compects': compects,
                'form': form,
            })
        else:
            for error in form.errors.values():
                for e in error:
                    messages.error(request, e)
            return redirect('companies:payrollaccumulations')
    
    # Inicializar el formulario vacío
    form = ReportFilterForm()
    
    return render(request, 'companies/payrollaccumulations.html', {
        'compects': compects,
        'form': form,
    })
    
    
def descargar_excel_empleados(request):
    acumulados = {}
    # Diccionario de ejemplo con 6 empleados y datos asociados
    nominas = Nomina.objects.all()[:70] ## .order_by('idconcepto__idconcepto')
    
    for data in nominas:
            docidentidad = data.idempleado.docidentidad
            if docidentidad not in acumulados:
                acumulados[docidentidad] = {
                    'documento': docidentidad,
                    'Empleado': f"{data.idempleado.papellido} {data.idempleado.sapellido} {data.idempleado.pnombre} {data.idempleado.snombre} - {data.idempleado.docidentidad} - {data.idcontrato.idcontrato} ",
                    'total':0,
                    'data':[
                        {"idconcepto": data.idconcepto.idconcepto,
                        "nombreconcepto": data.nombreconcepto, 
                        "cantidad": data.cantidad, 
                        "valor": data.valor},
                    ]
                }
            else:
                nuevo_concepto = {"idconcepto": data.idconcepto.idconcepto, 
                                "nombreconcepto": data.nombreconcepto,
                                "cantidad": data.cantidad,  
                                "valor": data.valor }
                
                acumulados[docidentidad]["data"].append(nuevo_concepto)
            acumulados[docidentidad]['total'] += data.valor
            
    # Generar el archivo Excel
    output = generate_employee_excel(acumulados)
    
    # Crear una respuesta HTTP con el archivo Excel
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="empleado_info.xlsx"'
    
    return response
