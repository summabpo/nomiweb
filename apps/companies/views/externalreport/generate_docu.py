import openpyxl
from openpyxl.styles import NamedStyle
from io import BytesIO
from django.http import HttpResponse
from apps.common.models import Nomina
from django.db.models import Sum

def generate_nomina_excel(year, month,idempresa):
    # Crear un archivo en memoria
    output = BytesIO()
    
    # Crear un nuevo libro de trabajo
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Nominas Report"

    # Encabezados del reporte
    headers = ['Contrato', 'Cuenta Contable', 'Documento de Identidad', 'Concepto', 'Nombre del Concepto', 'Valor', 'Costo']
    ws.append(headers)

    # Estilo para formato decimal
    decimal_style = NamedStyle(name='decimal_style', number_format='0.00')

    # Obtener datos optimizando la consulta
    nominas = Nomina.objects.filter(idnomina__mesacumular=month, idnomina__anoacumular__ano=year,idnomina__id_empresa__idempresa = idempresa)\
        .select_related('idcontrato', 'idcosto', 'idconcepto')\
        .only('idcontrato__idcontrato', 'idconcepto__cuentacontable', 'idcontrato__idempleado__docidentidad', 
              'idconcepto__idconcepto', 'idconcepto__nombreconcepto', 'valor', 'idcosto__idcosto')

    # Añadir datos a la hoja de cálculo
    for data in nominas:
        row = [
            data.idcontrato.idcontrato,
            data.idconcepto.cuentacontable,
            data.idcontrato.idempleado.docidentidad,
            data.idconcepto.idconcepto,
            data.idconcepto.nombreconcepto,
            data.valor, 
            data.idcosto.idcosto
        ]
        ws.append(row)

    # Aplicar formato decimal a las columnas relevantes
    for cell in ws['F']:
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
