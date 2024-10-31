import openpyxl
from openpyxl.styles import NamedStyle
from io import BytesIO
from django.http import HttpResponse
from apps.common.models import Contratos
from django.db.models import Sum

""" 
original :
'Documento', 'Nombre', 'Fecha Inicio Contrato', 'Cargo', 'Salario',
        'Centro de Costos', 'Tipo de Contrato', 'Tarifa ARL', 'Fecha Fin Contrato',
        'Tipo Nomina', 'Banco Cuenta', 'Cuenta Nomina', 'Tipo Cuenta Nomina', 'EPS', 'Pension',
        'Caja Compensacion', 'Ciudad Contratacion ', 'Fondo Cesantias',
        'Forma Pago', 'Tipo Salario', 'Modelo', 'Departamento',
        'Ciudad'
quitados 
'Fondo Cesantias',

"""

def generate_contract_excel(idempresa):
    # Crear un archivo en memoria
    output = BytesIO()
    
    # Crear un nuevo libro de trabajo
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Contract Report"

    # Encabezados del reporte
    headers = ['Documento', 'Nombre', 'Fecha Inicio Contrato', 'Cargo', 'Salario',
        'Centro de Costos', 'Tipo de Contrato', 'Tarifa ARL', 'Fecha Fin Contrato',
        'Tipo Nomina', 'Banco Cuenta', 'Cuenta Nomina', 'Tipo Cuenta Nomina', 'EPS', 'Pension',
        'Caja Compensacion', 'Ciudad Contratacion ', 
        'Forma Pago', 'Tipo Salario', 'Modelo', 'Departamento',
        'Ciudad']
    ws.append(headers)

    # Estilo para formato decimal
    decimal_style = NamedStyle(name='decimal_style', number_format='0.00')

    # Obtener datos optimizando la consulta
    contratos_empleados = Contratos.objects\
        .filter(estadocontrato=1 , id_empresa = idempresa)\
        .only(
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
            'codeps',
            'codafp', 
            'codccf', 
            'ciudadcontratacion__ciudad',
            'formapago', 
            'tiposalario__tiposalario', 
            'jornada', 
            'idmodelo__tipocontrato',
        )

    # Añadir datos a la hoja de cálculo
    for data in contratos_empleados:
        row = [
            data.idempleado.docidentidad, #* 
            f'{data.idempleado.papellido} {data.idempleado.pnombre} {data.idempleado.snombre }', #* 
            data.fechainiciocontrato, # *
            data.cargo.nombrecargo, #* 
            data.salario, #*
            data.idcosto.nomcosto, #* 
            data.tipocontrato.tipocontrato, #* 
            data.centrotrabajo.tarifaarl  , #* 
            data.fechafincontrato  , #* 
            data.tiponomina.tipodenomina  , #* 
            data.bancocuenta.nombanco  , #* 
            data.cuentanomina  , #* 
            data.tipocuentanomina  , #* 
            data.codeps.entidad  , #*
            data.codafp.entidad  , #* 
            data.codccf.entidad  , #* 
            data.ciudadcontratacion.ciudad  , #* 
            data.formapago  , #* 
            data.tiposalario.tiposalario  , # *
            data.jornada  , # 
            data.idmodelo.tipocontrato  , #* 
        ]
        ws.append(row)

    # Aplicar formato decimal a las columnas relevantes
    for cell in ws['E']:
        cell.style = decimal_style

    # Ajustar el ancho de las columnas
    for col in ws.columns:
        max_length = max(len(str(cell.value or '')) for cell in col)
        column = col[0].column_letter
        ws.column_dimensions[column].width = max_length + 2

    # Guardar el archivo en memoria
    wb.save(output)
    output.seek(0)

    return output.getvalue()




def generate_contract_start_excel(idempresa):
    # Crear un archivo en memoria
    output = BytesIO()
    
    # Crear un nuevo libro de trabajo
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Contract Report"

    # Encabezados del reporte
    headers = ['Documento', 'Nombre', 'Fecha Inicio Contrato', 'Cargo', 'Salario',
        'Centro de Costos', 'Tipo de Contrato', 'Tarifa ARL']
    ws.append(headers)

    # Estilo para formato decimal
    decimal_style = NamedStyle(name='decimal_style', number_format='0.00')

    # Obtener datos optimizando la consulta
    contratos_empleados = Contratos.objects.filter(
        estadocontrato=1,
        id_empresa=idempresa
    ).select_related(
        'idempleado', 'idcosto', 'tipocontrato', 'centrotrabajo'
    ).only(
        'idempleado__docidentidad', 
        'idempleado__papellido', 
        'idempleado__pnombre',
        'idempleado__snombre', 
        'fechainiciocontrato', 
        'cargo', 
        'salario', 
        'idcosto__nomcosto',
        'tipocontrato__tipocontrato', 
        'centrotrabajo__tarifaarl'
    )
    # Añadir datos a la hoja de cálculo
    for data in contratos_empleados:
        row = [
            data.idempleado.docidentidad, 
            f'{data.idempleado.papellido} {data.idempleado.pnombre} {data.idempleado.snombre }', 
            data.fechainiciocontrato, 
            data.cargo.nombrecargo,  
            data.salario, 
            data.idcosto.nomcosto, 
            data.tipocontrato.tipocontrato,  
            data.centrotrabajo.tarifaarl  , 
        ]
        ws.append(row)

    # Aplicar formato decimal a las columnas relevantes
    for cell in ws['E']:
        cell.style = decimal_style

    # Ajustar el ancho de las columnas
    for col in ws.columns:
        max_length = max(len(str(cell.value or '')) for cell in col)
        column = col[0].column_letter
        ws.column_dimensions[column].width = max_length + 2

    # Guardar el archivo en memoria
    wb.save(output)
    output.seek(0)

    return output.getvalue()

