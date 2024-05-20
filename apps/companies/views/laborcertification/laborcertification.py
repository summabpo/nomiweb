from django.shortcuts import render
from apps.companies.models import Contratos 


def laborcertification(request):
    
    contratos_empleados = Contratos.objects\
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede') \
        .values('idempleado__docidentidad', 'idempleado__papellido', 'idempleado__pnombre',
                'idempleado__snombre', 'fechainiciocontrato', 'cargo', 'salario', 'idcosto__nomcosto',
                'tipocontrato__tipocontrato', 'centrotrabajo__tarifaarl')

    empleados = []
    for contrato in contratos_empleados:
        nombre_empleado = f"{contrato['idempleado__papellido']} {contrato['idempleado__pnombre']} {contrato['idempleado__snombre']}"
        

        contrato_data = {
            'documento': contrato['idempleado__docidentidad'],
            'nombre': nombre_empleado,
            'fechainiciocontrato': contrato['fechainiciocontrato'],
            'cargo': contrato['cargo'],
            'centrocostos': contrato['idcosto__nomcosto'],
            'tipocontrato': contrato['tipocontrato__tipocontrato'],
            'tarifaARL': contrato['centrotrabajo__tarifaarl'],
        }

        empleados.append(contrato_data)
        
    
    return render(request, 'companies/laborcertification.html', {'empleados': empleados})



