from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Liquidacion , Nomina
from apps.companies.forms.ReportFilterForm import ReportFilterForm
from django.contrib import messages
from django.http import HttpResponse
from apps.components.generate_employee_excel import generate_employee_excel
from apps.components.humani import format_value
from django.http import JsonResponse
from .parse_dates import parse_dates



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
                        'total':0,
                        'contrato': data.idcontrato.idcontrato,
                        'data':[
                            {"idconcepto": data.idconcepto.idconcepto,
                            "nombreconcepto": data.nombreconcepto, 
                            "cantidad": data.cantidad, 
                            "valor": data.valor,
                            "multiplicador": 1},
                            
                        ]
                    }
                else:
                    concepto_existente = next((concepto for concepto in acumulados[docidentidad]["data"] if concepto["idconcepto"] == data.idconcepto.idconcepto), None)
                    print('////////////////')
                    print(concepto_existente)
                    print('////////////////')
                    
                    if concepto_existente:
                        # Si existe, sumar la cantidad y el valor, y actualizar el nombreconcepto con el multiplicador
                        concepto_existente["cantidad"] += data.cantidad
                        concepto_existente["valor"] += data.valor
                        concepto_existente["multiplicador"] += 1
                        # Actualizar el nombreconcepto con el multiplicador
                        concepto_existente["nombreconcepto"] = f'{data.nombreconcepto} x{concepto_existente["multiplicador"]}'
                    else:
                        # Si no existe, añadir el nuevo concepto
                        nuevo_concepto = {
                            "idconcepto": data.idconcepto.idconcepto,
                            "nombreconcepto": data.nombreconcepto,
                            "cantidad": data.cantidad,
                            "valor": data.valor,
                            "multiplicador": 1
                        }
                    
                    # nuevo_concepto = {"idconcepto": data.idconcepto.idconcepto, 
                    #                 "nombreconcepto": data.nombreconcepto,
                    #                 "cantidad": data.cantidad,  
                    #                 "valor": data.valor }
                    
                    acumulados[docidentidad]["data"].append(nuevo_concepto)
                acumulados[docidentidad]['total'] += data.valor
            
            # Procesar los datos acumulados
            compects = list(acumulados.values())
            # for compect in compects:
            #     compect['total'] = compect['basico'] + compect['aportess'] + compect['prestamos']
            #     for key in ['basico', 'aportess', 'prestamos', 'total']:
            #         compect[key] = format_value(compect[key])
            
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
        
        nominas = Nomina.objects.filter(**filtros)
        
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
