import openpyxl
from openpyxl.styles import NamedStyle
from io import BytesIO
from django.http import HttpResponse
from apps.common.models import Nomina
from django.db.models import Sum

def generate_nomina_excel(year, month,idempresa):
    """
    Función para generar un informe de nómina en formato Excel.

    Esta función genera un archivo Excel en memoria que contiene los datos de la nómina para un 
    año y mes específicos, asociados a una empresa en particular. Los datos se extraen de la base de 
    datos y se estructuran en una hoja de cálculo con las columnas correspondientes, incluyendo el 
    contrato, cuenta contable, documento de identidad, concepto, nombre del concepto, valor y costo.

    Parámetros
    ----------
    year : int
        El año del período de nómina que se desea generar en el informe (formato YYYY).
    
    month : int
        El mes del período de nómina que se desea generar en el informe (formato MM).
    
    idempresa : int
        El identificador de la empresa cuyos datos de nómina se deben consultar.

    Retorna
    -------
    bytes
        Un archivo en formato Excel generado en memoria que contiene los datos de la nómina correspondiente
        al período de año y mes especificados. El archivo es devuelto en formato de bytes para ser descargado
        o procesado por el cliente.
    
    Notas
    -----
    El archivo generado contiene las siguientes columnas:
        - Contrato: Identificador del contrato del empleado.
        - Cuenta Contable: Cuenta contable asociada al concepto.
        - Documento de Identidad: Número de documento de identidad del empleado.
        - Concepto: Identificador del concepto de la nómina.
        - Nombre del Concepto: Descripción del concepto de la nómina.
        - Valor: El valor asignado al concepto de nómina.
        - Costo: Identificador del costo asociado al concepto.

    Se aplica formato decimal a la columna 'Valor' para asegurar que los números se muestren con dos decimales.
    También se ajusta automáticamente el ancho de las columnas para que el contenido se ajuste correctamente.

    Ejemplo de uso
    ---------------
    excel_data = generate_nomina_excel(2025, 4, 1)  # Genera un reporte para abril de 2025, empresa con ID 1
    """


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
