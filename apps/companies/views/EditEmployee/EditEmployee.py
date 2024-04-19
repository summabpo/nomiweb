from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Tipodocumento , Paises , Ciudades , Contratosemp , Contratos




def EditEmployeeVisual(request,idempleado):
    empleado = Contratosemp.objects.using("lectaen").get(idempleado=idempleado) 
    tipo_documento = Tipodocumento.objects.using("lectaen").get(codigo=empleado.tipodocident) 
    
    ciudadex = Ciudades.objects.using("lectaen").get(idciudad=empleado.ciudadexpedicion) 
    ciudadna = Ciudades.objects.using("lectaen").get(idciudad=empleado.ciudadnacimiento) 
    DatoCruz = {
        'tipodocident': tipo_documento.documento,
        'ciudadexpedicion':ciudadex.ciudad + ' - ' + ciudadex.departamento,
        'ciudadnaci': ciudadna.ciudad + ' - ' + ciudadna.departamento,
        
    }
    
    #empleado_dict = list(empleado)
    return render(request, './companies/EditEmployeevisual.html',{'empleado':empleado , 'datocruz':DatoCruz})




def EditEmployeeSearch(request):
    contratos_empleados = Contratos.objects.using("lectaen") \
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede') \
        .filter(estadocontrato=1) \
        .values('idempleado__docidentidad', 'idempleado__papellido', 'idempleado__sapellido','idempleado__pnombre',
                'idempleado__snombre', 'fechainiciocontrato', 'cargo', 'idempleado__direccionempleado',
                'ciudadcontratacion__ciudad','idempleado__celular','idempleado__email','idempleado__idempleado')

    empleados = []
    for contrato in contratos_empleados:
        nombre_empleado = f"{contrato['idempleado__papellido']} {contrato['idempleado__sapellido']}  {contrato['idempleado__pnombre']} {contrato['idempleado__snombre']}"
        contrato_data = {
            'documento': contrato['idempleado__docidentidad'],
            'nombre': nombre_empleado,
            'fechainiciocontrato': contrato['fechainiciocontrato'],
            'cargo': contrato['cargo'],
            'dirección': contrato['idempleado__direccionempleado'],
            'ciudad': contrato['ciudadcontratacion__ciudad'],
            'celular': contrato['idempleado__celular'],
            'mail': contrato['idempleado__email'],
            'id':contrato['idempleado__idempleado'],
        }

        empleados.append(contrato_data)
        
    return render(request, './companies/EditEmployeesearch.html', {'empleados': empleados})



"""   
def EditEmployeeSearch(request):
    contratos_empleados = Contratos.objects.using("lectaen").select_related('idempleado').filter(estadocontrato=1)

    empleados = []
    for contrato in contratos_empleados:
        empleado = contrato.idempleado
        costo = contrato.idcosto
        tipo = contrato.tipocontrato
        sede = contrato.idsede
        contrato_data = {
            'documento': empleado.docidentidad,
            'nombre': str(empleado.papellido )+' ' + str(empleado.pnombre) + ' ' + str(empleado.snombre),
            'fechainiciocontrato': contrato.fechainiciocontrato,
            'cargo': contrato.cargo ,
            'salario': "{:,.0f}".format(contrato.salario).replace(',', '.') ,
            'centrocostos':costo.nomcosto,
            'tipocontrato':tipo.tipocontrato, 
            'tarifaARL':sede.nombresede,
        }
        
        empleados.append(contrato_data)
    return render(request, './companies/EditEmployeesearch.html',{'empleados':empleados})

"""