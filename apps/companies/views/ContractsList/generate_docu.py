import openpyxl
from openpyxl.styles import NamedStyle
from io import BytesIO
from django.http import HttpResponse
from apps.common.models import Contratos
from django.db.models import Sum


FormaPago = (
    ('', '----------'),
    ('1', 'Abono a cuenta'),
    ('2', 'Cheque'),
    ('3', 'Efectivo'),
    ('4', 'Transferencia electrónica'),
)



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
        'Forma Pago', 'Tipo Salario', 'Modelo', 'Departamento'
        ,'ID Contrato']
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
            'idmodelo__nombremodelo',
            'idcontrato'
        )

    # Añadir datos a la hoja de cálculo
    for data in contratos_empleados:
        forma_pago_dict = dict(FormaPago)
        row = [
            data.idempleado.docidentidad, #* 
            f'{data.idempleado.papellido or ""} {data.idempleado.pnombre or ""} {data.idempleado.snombre or ""}',#* 
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
            forma_pago_dict.get(data.formapago, 'Valor no encontrado') , #* 
            data.tiposalario.tiposalario  , # *
            data.jornada  , # 
            data.idmodelo.nombremodelo  , #* 
            data.idcontrato 
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
        'Centro de Costos', 'Tipo de Contrato', 'Tarifa ARL','ID Contrato']
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
        'centrotrabajo__tarifaarl',
        'idcontrato'
    )
    # Añadir datos a la hoja de cálculo
    for data in contratos_empleados:
        
        row = [
            data.idempleado.docidentidad, 
            f'{data.idempleado.papellido or ""} {data.idempleado.pnombre or ""} {data.idempleado.snombre or ""}', 
            data.fechainiciocontrato, 
            data.cargo.nombrecargo,  
            data.salario, 
            data.idcosto.nomcosto, 
            data.tipocontrato.tipocontrato,  
            data.centrotrabajo.tarifaarl  , 
            data.idcontrato 
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

