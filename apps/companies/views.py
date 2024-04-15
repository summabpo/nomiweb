from django.shortcuts import render, redirect, get_object_or_404
from .models import Contratos , Contratosemp ,Costos , Tipocontrato , Centrotrabajo
import locale



def startCompanies(request): 
    combined_data = {}
    
    contracts = Contratos.objects.using("lectaen").filter(estadocontrato=1).values_list('cargo', 'fechainiciocontrato', 'salario', 'idcosto', 'tipocontrato', 'centrotrabajo', 'idempleado')
    
    employee_ids = set(contract[-1] for contract in contracts)
    employees = Contratosemp.objects.using("lectaen").filter(idempleado__in=employee_ids).values_list('idempleado', 'docidentidad', 'pnombre', 'papellido', 'sapellido')
    
    costs = Costos.objects.using("lectaen").all().values_list('idcosto', 'nomcosto')
    tipo_contrato = Tipocontrato.objects.using("lectaen").all().values_list('idtipocontrato', 'tipocontrato')
    centrotrabajo = Centrotrabajo.objects.using("lectaen").all().values_list('tarifaarl', 'centrotrabajo')
    
    for employee_id in employee_ids:
        combined_data[employee_id] = {'docidentidad': None, 'pnombre': None, 'papellido': None, 'sapellido': None, 'contratos': [], 'costs': {'idcosto': None, 'nomcosto': None}, 'tipo_contrato': None}

    for contract in contracts:
        employee_id = contract[-1]
        combined_data[employee_id]['contratos'].append(contract[:-1])

    for employee_detail in employees:
        employee_id = employee_detail[0]
        combined_data[employee_id]['docidentidad'] = employee_detail[1]
        combined_data[employee_id]['pnombre'] = employee_detail[2]
        combined_data[employee_id]['papellido'] = employee_detail[3]
        combined_data[employee_id]['sapellido'] = employee_detail[4]
    
    
    for employee_id, employee_data in combined_data.items():
        contratos_formateados = []
        for contract in employee_data['contratos']:
            salario_formateado = "{:,.0f}".format(contract[2])
            contrato_formateado = (*contract[:2], salario_formateado, *contract[3:])
            contratos_formateados.append(contrato_formateado)
        combined_data[employee_id]['contratos'] = contratos_formateados



    for employee_id, employee_data in combined_data.items():
        for contract in employee_data['contratos']:
            tipo_contrato_contract = contract[4]  
            for tipo in tipo_contrato:
                if tipo[0] == int(tipo_contrato_contract): 
                    combined_data[employee_id]['tipo_contrato'] = tipo[1]
                    break
            else:
                continue
            break 
    
    for employee_id, employee_data in combined_data.items():
        for contract in employee_data['contratos']:
            centrotrabajo_contract = contract[5]  
            for centro in centrotrabajo:
                if centro[1] == int (centrotrabajo_contract): 
                    combined_data[employee_id]['centrotrabajo'] = centro[0]
                    break
            else:
                continue
            break
    
    return render(request, './companies/index.html', {'combined_data': combined_data})




