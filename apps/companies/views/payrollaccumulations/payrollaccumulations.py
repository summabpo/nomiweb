from django.shortcuts import render, redirect
from apps.common.models import Nomina
from apps.companies.forms.ReportFilterForm import ReportFilterForm
from django.contrib import messages
from django.http import HttpResponse
from apps.components.generate_employee_excel import generate_employee_excel
from apps.components.humani import format_value
from django.http import JsonResponse
from .parse_dates import parse_dates

from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

@login_required
@role_required('company')
def payrollaccumulations(request):
    acumulados = {}
    compects = []
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = ReportFilterForm(idempresa=idempresa)
    if request.method == 'POST':
        form = ReportFilterForm(request.POST , idempresa=idempresa)
        if form.is_valid():
            #try:
                # Obtener los parámetros de búsqueda del formulario
            employee = form.cleaned_data['employee']
            cost_center = form.cleaned_data['cost_center']
            city = form.cleaned_data['city']
            
            year_init = form.cleaned_data.get('year_init')
            mst_init = form.cleaned_data.get('mst_init')
            year_end = form.cleaned_data.get('year_end')
            mst_end = form.cleaned_data.get('mst_end')
            
    
            # Aplicar filtros a la consulta de Nomina
            nominas = Nomina.objects.all().order_by('idconcepto__idconcepto')
            if employee:
                nominas = nominas.filter(idcontrato__idempleado__idempleado=employee)
            if cost_center:
                nominas = nominas.filter(idcontrato__idcosto=cost_center)
            if city:
                nominas = nominas.filter(idcontrato__idsede=city)
            
            if year_init and mst_init and year_end and mst_end:
                # Filtrar por mes y año iniciales
                nominas = nominas.filter(
                    #idnomina__anoacumular__gte=year_init, 
                    idnomina__mesacumular__gte=mst_init
                )

                # Filtrar por mes y año finales
                nominas = nominas.filter(
                    #idnomina__anoacumular__ano__lte=year_end, 
                    idnomina__mesacumular__lte=mst_end
                )    
            
                    
            # Acumular los datos
            for data in nominas:
                docidentidad = data.idcontrato.idempleado.docidentidad
                if docidentidad not in acumulados:
                    acumulados[docidentidad] = {
                        'documento': docidentidad,
                        'empleado': f"{data.idcontrato.idempleado.papellido} {data.idcontrato.idempleado.sapellido} {data.idcontrato.idempleado.pnombre} {data.idcontrato.idempleado.snombre}",
                        'contrato': data.idcontrato.idcontrato,
                        'data': [
                            {"idconcepto": data.idconcepto.idconcepto,
                                "nombreconcepto": data.idconcepto.nombreconcepto,
                                "cantidad": data.cantidad,
                                "valor": data.valor,},
                        ]
                    }
                else:
                    concepto_existente = next((concepto for concepto in acumulados[docidentidad]["data"] if concepto["idconcepto"] == data.idconcepto.idconcepto), None)
                    
                    if concepto_existente:
                        # Si existe, sumar la cantidad y el valor
                        concepto_existente["cantidad"] += data.cantidad
                        concepto_existente["valor"] += data.valor
                    else:
                        # Si no existe, añadir el nuevo concepto
                        nuevo_concepto = {
                            "idconcepto": data.idconcepto.idconcepto,
                            "nombreconcepto": data.idconcepto.nombreconcepto,
                            "cantidad": data.cantidad,
                            "valor": data.valor,
                        }
                        acumulados[docidentidad]["data"].append(nuevo_concepto)
            
            for docidentidad, datos in acumulados.items():
                for concepto in datos['data']:
                    concepto['valor'] = format_value(concepto['valor'])
            
            # Procesar los datos acumulados
            compects = list(acumulados.values())
            
            form = ReportFilterForm(request.POST,idempresa=idempresa)
            # except Exception as e:
            #     print(f"Tipo de excepción: {type(e).__name__}") 
            #     messages.error(request, "Algo salió mal. Por favor, intenta nuevamente.")
            #     return  redirect('companies:payrollaccumulations')
        else:
            # Si el formulario no es válido, mostrar los errores
            for error in form.errors.values():
                for e in error:
                    messages.error(request, e)


    return render(request, 'companies/payrollaccumulations.html', {
        'compects': compects,
        'form': form,
    })
    
    
    
    
@login_required
@role_required('company')    
def descargar_excel_empleados(request):
    if request.method == 'POST':
        acumulados = {}
        # Obtener parámetros del POST
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        employee = request.POST.get('employee')
        cost_center = request.POST.get('cost_center')
        city = request.POST.get('city')
        
        # Aplicar filtros a la consulta de Nomina
        filtros = {}
        
        if employee:
            filtros['idempleado__idempleado'] = employee
        if cost_center:
            filtros['idcontrato__idcosto'] = cost_center
        if city:
            filtros['idcontrato__idsede'] = city
        if start_date:
            filtros['idnomina__fechainicial__gte'] = start_date
        if end_date:
            filtros['idnomina__fechafinal__lte'] = end_date
        
        nominas = Nomina.objects.filter(**filtros).order_by('idconcepto__idconcepto')
        
        for data in nominas:
            docidentidad = data.idempleado.docidentidad
            if docidentidad not in acumulados:
                acumulados[docidentidad] = {
                    'documento': docidentidad,
                    'Empleado': f"{data.idempleado.papellido} {data.idempleado.sapellido} {data.idempleado.pnombre} {data.idempleado.snombre} - {data.idempleado.docidentidad} - {data.idcontrato.idcontrato}",
                    'data': [
                        {
                            "idconcepto": data.idconcepto.idconcepto,
                            "nombreconcepto": data.nombreconcepto, 
                            "cantidad": data.cantidad, 
                            "valor": data.valor,
                        }
                    ],
                    'total': data.valor,  
                    'id': data.idcontrato.idcontrato ,
                }
            else:
                concepto_existente = next((concepto for concepto in acumulados[docidentidad]["data"] if concepto["idconcepto"] == data.idconcepto.idconcepto), None)
                
                if concepto_existente:
                    # Si el concepto existe, sumamos la cantidad y el valor
                    concepto_existente["cantidad"] += data.cantidad
                    concepto_existente["valor"] += data.valor
                else:
                    # Si no existe, añadimos el nuevo concepto
                    nuevo_concepto = {
                        "idconcepto": data.idconcepto.idconcepto,
                        "nombreconcepto": data.nombreconcepto,
                        "cantidad": data.cantidad, 
                        "valor": data.valor,
                    }
                    acumulados[docidentidad]["data"].append(nuevo_concepto)
                
                # Actualizar el total con el nuevo valor
                acumulados[docidentidad]['total'] += data.valor
                    

        
        # Convertir las fechas y extraer el año y el mes
        start_year, start_month, end_year, end_month = parse_dates(start_date, end_date)
        # Generar el archivo Excel
        output = generate_employee_excel(acumulados,start_month,start_year,end_month,end_year)
        
        # Crear una respuesta HTTP con el archivo Excel
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="empleado_info.xlsx"'
        return response
    
    return JsonResponse({'error': 'Falla en la creacion de Documento'}, status=405)
