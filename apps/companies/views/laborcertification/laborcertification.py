
from django.shortcuts import render
from apps.companies.models import Contratos 

from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

@login_required
@role_required('entrepreneur')
def laborcertification(request):
    """
    Vista para generar la certificación laboral de los empleados.

    Esta vista permite a los usuarios con el rol 'entrepreneur' acceder a los datos laborales de los empleados 
    y generar la certificación laboral correspondiente. Se obtiene una lista de los empleados y sus contratos, 
    mostrando información como el documento de identidad, nombre completo, fecha de inicio del contrato, cargo, 
    centro de costos, tipo de contrato y tarifa ARL. La información es luego pasada al template 'laborcertification.html'.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que permite acceder a los datos de los empleados para la certificación laboral.

    Returns
    -------
    HttpResponse
        Devuelve la respuesta HTTP renderizada con los datos de los empleados en el template 'laborcertification.html'.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol 'entrepreneur' para acceder a esta vista.
    Se hace una consulta optimizada utilizando `select_related` para obtener los datos relacionados de los empleados, 
    cargos, centros de costo, tipo de contrato, y tarifas ARL en una sola consulta a la base de datos.
    """
    contratos_empleados = Contratos.objects\
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede') \
        .values('idempleado__docidentidad', 'idempleado__papellido', 'idempleado__pnombre',
                'idempleado__snombre', 'fechainiciocontrato', 'cargo', 'salario', 'idcosto__nomcosto',
                'tipocontrato__tipocontrato', 'centrotrabajo__tarifaarl')

    empleados = []
    for contrato in contratos_empleados:
        nombre_empleado = ' '.join(filter(None, [
            contrato['idempleado__papellido'],
            contrato['idempleado__sapellido'],
            contrato['idempleado__pnombre'],
            contrato['idempleado__snombre']
        ])),

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





