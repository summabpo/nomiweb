from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Contratos 
from apps.components.decorators import custom_login_required ,custom_permission
from openpyxl import Workbook
from django.http import HttpResponse
from io import BytesIO

@custom_login_required
@custom_permission('entrepreneur')
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
    contratos_empleados = Contratos.objects\
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede') \
        .filter(estadocontrato=1) \
        .values_list(
            'idempleado__docidentidad', 'idempleado__papellido', 'idempleado__pnombre',
            'idempleado__snombre', 'fechainiciocontrato', 'cargo', 'salario', 'idcosto__nomcosto',
            'tipocontrato__tipocontrato', 'centrotrabajo__tarifaarl','idempleado__idempleado','idcontrato'
        )

    workbook = Workbook()
    hoja = workbook.active
    hoja.title = "Contratos Activos"

    # Escribir los encabezados
    hoja.append([
        'Documento', 'Nombre', 'Fecha Inicio Contrato', 'Cargo', 'Salario',
        'Centro de Costos', 'Tipo de Contrato', 'Tarifa ARL', 'ID Empleado', 'ID Contrato'
    ])

    # Escribir los datos
    for contrato in contratos_empleados:
        nombre_empleado = f"{contrato[1]} {contrato[2]} {contrato[3]}"
        salario = "{:,.0f}".format(contrato[6]).replace(',', '.')
        hoja.append([
            contrato[0], nombre_empleado, contrato[4],
            contrato[5], salario, contrato[7], contrato[8],
            contrato[9], contrato[10], contrato[11]
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
    contratos_empleados = Contratos.objects\
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede') \
        .filter(estadocontrato=1) \
        .values_list(
            'idempleado__docidentidad', 'idempleado__papellido', 'idempleado__pnombre',
            'idempleado__snombre', 'fechainiciocontrato', 'cargo', 'salario', 'idcosto__nomcosto',
            'tipocontrato__tipocontrato', 'centrotrabajo__tarifaarl','idempleado__idempleado','idcontrato'
        )

    workbook = Workbook()
    hoja = workbook.active
    hoja.title = "Contratos Activos"

    # Escribir los encabezados
    hoja.append([
        'Documento', 'Nombre', 'Fecha Inicio Contrato', 'Cargo', 'Salario',
        'Centro de Costos', 'Tipo de Contrato', 'Tarifa ARL', 'ID Empleado', 'ID Contrato'
    ])

    # Escribir los datos
    for contrato in contratos_empleados:
        nombre_empleado = f"{contrato[1]} {contrato[2]} {contrato[3]}"
        salario = "{:,.0f}".format(contrato[6]).replace(',', '.')
        hoja.append([
            contrato[0], nombre_empleado, contrato[4],
            contrato[5], salario, contrato[7], contrato[8],
            contrato[9], contrato[10], contrato[11]
        ])

    # Guardar el libro de trabajo en memoria
    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    # Crear la respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=informe hojas de vida.xlsx'
    response.write(output.getvalue())
    return response