from django.shortcuts import render, redirect, get_object_or_404
from apps.common.models  import Contratos , Contratosemp , Ciudades
from apps.components.decorators import custom_login_required ,custom_permission
from openpyxl import Workbook
from django.http import HttpResponse
from io import BytesIO
from datetime import datetime

from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from .generate_docu import generate_contract_excel,generate_contract_start_excel



@login_required
@role_required('company')
def startCompanies(request): 
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    contratos_empleados = Contratos.objects\
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede') \
        .order_by('idempleado__papellido') \
        .filter(estadocontrato=1, id_empresa=idempresa) \
        .values(
            'idempleado__docidentidad', 'idempleado__papellido', 'idempleado__pnombre',
            'idempleado__snombre', 'fechainiciocontrato', 'cargo__nombrecargo', 'salario', 
            'idcosto__nomcosto', 'tipocontrato__tipocontrato', 'centrotrabajo__tarifaarl',
            'idempleado__idempleado', 'idcontrato'
        )
    
    empleados = [
        {
            'documento': contrato['idempleado__docidentidad'],
            'nombre': f"{contrato['idempleado__papellido']} {contrato['idempleado__pnombre']} {contrato['idempleado__snombre']}",
            'fechainiciocontrato': contrato['fechainiciocontrato'],
            'cargo': contrato['cargo__nombrecargo'],
            'salario': f"{contrato['salario'] if contrato['salario'] is not None else 0:,.0f}".replace(',', '.'),  # Formato de salario
            'centrocostos': contrato['idcosto__nomcosto'],
            'tipocontrato': contrato['tipocontrato__tipocontrato'],
            'tarifaARL': contrato['centrotrabajo__tarifaarl'],
            'idempleado': contrato['idempleado__idempleado'],
            'idcontrato': contrato['idcontrato'],
        }
        for contrato in contratos_empleados
    ]
    
    return render(request, './companies/ActiveList.html', {'empleados': empleados})



@login_required
@role_required('company')
def exportar_excel0(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    excel_data = generate_contract_start_excel(idempresa)
    file_name = f"contratos_activos.xlsx"
    
    # Crear la respuesta con el archivo Excel
    response = HttpResponse(excel_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    return response

@login_required
@role_required('company')
def exportar_excel1(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    excel_data = generate_contract_excel(idempresa)
    file_name = f"contratos_activos.xlsx"
    
    # Crear la respuesta con el archivo Excel
    response = HttpResponse(excel_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    return response





@login_required
@role_required('company')
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

















































































