from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Contratos , Contratosemp , Ciudades
from apps.components.decorators import custom_login_required ,custom_permission
from openpyxl import Workbook
from django.http import HttpResponse
from io import BytesIO
from datetime import datetime



# @custom_login_required
# @custom_permission('entrepreneur')
def startCompanies(request): 
    contratos_empleados = Contratos.objects\
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede') \
        .filter(estadocontrato=1) \
        .values('idempleado__docidentidad', 'idempleado__papellido', 'idempleado__pnombre',
                'idempleado__snombre', 'fechainiciocontrato', 'cargo', 'salario', 'idcosto__nomcosto',
                'tipocontrato__tipocontrato', 'centrotrabajo__tarifaarl','idempleado__idempleado','idcontrato')

    empleados = []
    for contrato in contratos_empleados:
        nombre_empleado = f"{contrato['idempleado__papellido']} {contrato['idempleado__pnombre']} {contrato['idempleado__snombre']}"
        salario = "{:,.0f}".format(contrato['salario']).replace(',', '.')

        contrato_data = {
            'documento': contrato['idempleado__docidentidad'],
            'nombre': nombre_empleado,
            'fechainiciocontrato': contrato['fechainiciocontrato'],
            'cargo': contrato['cargo'],
            'salario': salario,
            'centrocostos': contrato['idcosto__nomcosto'],
            'tipocontrato': contrato['tipocontrato__tipocontrato'],
            'tarifaARL': contrato['centrotrabajo__tarifaarl'],
            'idempleado' : contrato['idempleado__idempleado'],
            'idcontrato' : contrato['idcontrato'],
        }

        empleados.append(contrato_data)
    
    return render(request, './companies/ActiveList.html', {'empleados': empleados})


def exportar_excel1(request):
    
    citys = Ciudades.objects.all()
    
    contratos_empleados = Contratos.objects\
        .select_related(
            'idempleado', 
            'idcosto', 
            'tipocontrato', 
            'idsede', 
            'centrotrabajo', 
            'ciudadcontratacion', 
            'tiposalario',
            
            
        )\
        .filter(estadocontrato=1)\
        .values_list(
            'idempleado__docidentidad', 
            'idempleado__papellido', 
            'idempleado__pnombre',
            'idempleado__snombre', 
            'fechainiciocontrato', 
            'cargo', 
            'salario', 
            'idcosto__nomcosto',
            'tipocontrato__tipocontrato', 
            'centrotrabajo__tarifaarl', 
            'fechafincontrato', 
            'tiponomina', 
            'bancocuenta', 
            'cuentanomina', 
            'tipocuentanomina', 
            'eps',
            'pension', 
            'cajacompensacion', 
            'ciudadcontratacion__ciudad',
            'fondocesantias', 
            'formapago', 
            'tiposalario__tiposalario', 
            'jornada', 
            'idmodelo__tipocontrato',
            'coddepartamento', 
            'codciudad'
        )

    workbook = Workbook()
    hoja = workbook.active
    hoja.title = "Contratos Activos"

    # Escribir los encabezados
    hoja.append([
        'Documento', 'Nombre', 'Fecha Inicio Contrato', 'Cargo', 'Salario',
        'Centro de Costos', 'Tipo de Contrato', 'Tarifa ARL', 'Fecha Fin Contrato',
        'Tipo Nomina', 'Banco Cuenta', 'Cuenta Nomina', 'Tipo Cuenta Nomina', 'EPS', 'Pension',
        'Caja Compensacion', 'Ciudad Contratacion ', 'Fondo Cesantias',
        'Forma Pago', 'Tipo Salario', 'Modelo', 'Departamento',
        'Ciudad'
    ])

    # Escribir los datos
    for contrato in contratos_empleados:
        try:
            if contrato[24] and contrato[25]:  # Verifica si ambos campos no están vacíos
                ciudad = next((ciudad for ciudad in citys if ciudad.codciudad == contrato[24] and ciudad.idciudad == contrato[25]), None)
                if ciudad:
                    departamento = ciudad.departamento
                    ciudad = ciudad.ciudad
        except ValueError as e:
            departamento = ""
            ciudad = ""
        except IndexError:
            departamento = ""
            ciudad = ""


        
        
        nombre_empleado = f"{contrato[1]} {contrato[2]} {contrato[3]}"
        salario = "{:,.0f}".format(contrato[6]).replace(',', '.')
        hoja.append([
            contrato[0], nombre_empleado, contrato[4],
            contrato[5], salario, contrato[7], contrato[8],
            contrato[9], contrato[10], contrato[11],
            contrato[12], contrato[13], contrato[14], contrato[15], contrato[16], contrato[17],
            contrato[18], contrato[19], contrato[21], contrato[22], contrato[23],
            departamento , ciudad 
        ])

    # Guardar el libro de trabajo en memoria
    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    # Crear la respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=contratos_activos.xlsx'
    response.write(output.getvalue())
    return response





def exportar_excel2(request):
    
    citys = Ciudades.objects.all()
    contratosemp_empleados = Contratosemp.objects.filter(estadocontrato=1).values_list(
        'docidentidad', 'tipodocident', 'pnombre', 'snombre', 'papellido', 'sapellido', 'fechanac',
        'ciudadnacimiento', 'telefonoempleado', 'direccionempleado', 'sexo', 'email', 
        'ciudadresidencia', 'estadocivil', 'idempleado', 'paisnacimiento', 'paisresidencia', 
        'celular', 'profesion', 'niveleducativo', 'gruposanguineo', 'estatura', 'peso', 
        'fechaexpedicion', 'ciudadexpedicion', 'dotpantalon', 'dotcamisa', 'dotzapatos', 
        'estrato', 'numlibretamil', 'estadocontrato', 'formatohv'
    )

    workbook = Workbook()
    hoja = workbook.active
    hoja.title = "Informe Hojas de vida"

    # Escribir los encabezados
    hoja.append([
        'Documento', 'Tipo de Documento', 'Nombre Completo', 'Fecha de Nacimiento', 'Ciudad de Nacimiento', 
        'Teléfono', 'Dirección', 'Sexo', 'Email', 'Ciudad de Residencia', 'Estado Civil', 'ID Empleado',
        'País de Nacimiento', 'País de Residencia', 'Celular', 'Profesión', 'Nivel Educativo', 
        'Grupo Sanguíneo', 'Estatura', 'Peso', 'Fecha de Expedición', 'Ciudad de Expedición', 
        'Talla Pantalón', 'Talla Camisa', 'Talla Zapatos', 'Estrato', 'Número de Libreta Militar', 
        'Estado del Contrato'
    ])

    # Escribir los datos
    for contrato in contratosemp_empleados:
        nombre_empleado = f"{contrato[2]} {contrato[3]} {contrato[4]} {contrato[5]}"
        
        # Convertir y formatear las fechas
        fechanac = contrato[6]
        fechaexpedicion = contrato[23]
        
        if isinstance(fechanac, str):
            try:
                fechanac = datetime.strptime(fechanac, '%Y-%m-%d').date()
            except ValueError:
                fechanac = None
                
        if isinstance(fechaexpedicion, str):
            try:
                fechaexpedicion = datetime.strptime(fechaexpedicion, '%Y-%m-%d').date()
            except ValueError:
                fechaexpedicion = None
        
        fechanac = fechanac.strftime('%Y-%m-%d') if fechanac else ''
        fechaexpedicion = fechaexpedicion.strftime('%Y-%m-%d') if fechaexpedicion else ''

        
        # ciudades 
        
        try:
            if contrato[7] :  # Verifica si ambos campos no están vacíos
                ciudad = next((ciudad for ciudad in citys if ciudad.idciudad == contrato[7] ), None)
                if ciudad:
                    ciudad1 = ciudad.ciudad
                else:
                    ciudad1 = ""
        except ValueError as e:
            ciudad1 = ""
        except IndexError:
            ciudad1 = ""
        
        
        try:
            if contrato[12] :  # Verifica si ambos campos no están vacíos
                ciudad = next((ciudad for ciudad in citys if ciudad.idciudad == contrato[12] ), None)
                if ciudad:
                    ciudad2 = ciudad.ciudad
                else:
                    ciudad2 = ""
        except ValueError as e:
            ciudad2 = ""
        except IndexError:
            ciudad2 = ""
        
        
        try:
            if contrato[24] :  # Verifica si ambos campos no están vacíos
                ciudad = next((ciudad for ciudad in citys if ciudad.idciudad == contrato[24] ), None)
                if ciudad:
                    ciudad3 = ciudad.ciudad
                else:
                    ciudad3 = ""
        except ValueError as e:
            ciudad3 = ""
        except IndexError:
            ciudad3 = ""
            
        # Agregar datos a la hoja
        
        
        
        hoja.append([
            contrato[0], contrato[1], nombre_empleado, fechanac, ciudad1, contrato[8], contrato[9], 
            contrato[10], contrato[11], ciudad2, contrato[13], contrato[14], contrato[15], 
            contrato[16], contrato[17], contrato[18], contrato[19], contrato[20], contrato[21], 
            contrato[22], fechaexpedicion, ciudad3, contrato[25], contrato[26], 
            contrato[27], contrato[28], contrato[29],contrato[30]
        ])
        
    # Guardar el libro de trabajo en memoria
    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    # Crear la respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=hojas de vida.xlsx'
    response.write(output.getvalue())
    return response

















































































