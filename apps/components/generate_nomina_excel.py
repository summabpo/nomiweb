import openpyxl
from openpyxl.styles import NamedStyle
from io import BytesIO
from apps.common.models import Nomina, Contratos, Conceptosfijos
from django.db.models import Q, Sum


"""
Genera un archivo Excel con los datos de nómina de los empleados para un mes y año específicos.

Este script crea un archivo Excel en memoria que contiene los datos de la nómina de los empleados, incluyendo información sobre costos, prestaciones sociales y total de cada empleado.

Parámetros
----------
year : int
    El año para el cual se genera el reporte de la nómina.

mth : str
    El mes para el cual se genera el reporte de la nómina.

idempresa : int
    El ID de la empresa para la cual se genera el reporte de nómina.

Retorna
-------
bytes
    Un archivo Excel en formato binario (bytes) con los datos de nómina de los empleados.

Descripción
-----------
- El archivo generado contiene una hoja llamada "Provisionalidades" con los siguientes encabezados:
    'Contrato', 'Identificación', 'Nombre', 'Costo', 'Base PS', 'Cesantías', 'Int. cesa', 'Prima', 'Vacaciones', 'Total PS'.
- Los datos de cada empleado incluyen su contrato, identificación, nombre, los valores correspondientes a conceptos fijos y prestaciones sociales (como cesantías, prima, vacaciones).
- Las prestaciones sociales se calculan utilizando las fórmulas correspondientes para cada tipo de salario.
- El archivo también contiene un estilo decimal para los valores numéricos de las prestaciones sociales y costos.
- Las columnas tienen un ancho ajustado automáticamente para mejorar la legibilidad de los datos.
- El archivo es guardado en memoria y retornado como un valor en bytes para ser descargado o utilizado en otros contextos.

Notas
-----
- La información de conceptos fijos (como cesantías, prima, vacaciones) se obtiene de la tabla `Conceptosfijos`.
- El costo de cada empleado se obtiene de la relación con el contrato.
- El cálculo de las prestaciones sociales se realiza en función de los valores de la base y el tipo de salario.
- El formato de celdas aplica un estilo decimal a las columnas de valores monetarios.
- El archivo se guarda con el nombre `excel_nomina.xlsx` en la memoria.
"""


def generate_nomina_excel(year, mth,idempresa):
    # Crear un archivo en memoria
    output = BytesIO()

    # Crear un nuevo libro de trabajo y seleccionar la hoja activa
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Provisionalidades"

    # Encabezados del reporte
    headers = ['Contrato', 'Identificación', 'Nombre', 'Costo', 'Base PS', 'Cesantías', 'Int. cesa', 'Prima', 'Vacaciones', 'Total PS']
    ws.append(headers)

    # Estilo para formato decimal
    decimal_style = NamedStyle(name='decimal_style', number_format='0.00')

    # Obtener datos
    nominas = Nomina.objects.filter(idnomina__mesacumular=mth, idnomina__anoacumular__ano=year,idnomina__id_empresa__idempresa = idempresa).select_related( 'idcontrato', 'idcosto').order_by('idcontrato__idempleado__papellido')
    conceptos_fijos = Conceptosfijos.objects.values('idfijo', 'valorfijo')
    conceptos_dict = {cf['idfijo']: cf['valorfijo'] for cf in conceptos_fijos}
    contratos = Contratos.objects.filter(idcontrato__in=nominas.values_list('idcontrato', flat=True)).select_related('tiposalario')
    contratos_dict = {c.idcontrato: c for c in contratos}

    empleados_datos = {}

    # Agrupar datos por empleado
    for data_nomina in nominas:
        docidentidad = data_nomina.idcontrato.idcontrato
        contrato = contratos_dict.get(docidentidad)
        tiposal = contrato.tiposalario if contrato else None
        basico = contrato.salario if contrato else 0

        # Obtener los valores de conceptos fijos
        pces = conceptos_dict.get(7, 0)
        ppri = conceptos_dict.get(6, 0)
        pint = conceptos_dict.get(8, 0)
        pvac = conceptos_dict.get(9, 0)

        base_prestacion_social = Q(idconcepto__baseprestacionsocial=1)
        sueldo_basico = Q(idconcepto__sueldobasico=1)

        base = Nomina.objects.filter(
            (base_prestacion_social | sueldo_basico),
            idnomina__mesacumular = mth,
            idnomina__anoacumular__ano = year,
            idcontrato=docidentidad
        ).aggregate(total=Sum('valor'))['total'] or 0

        # Calcular prestaciones sociales
        vacaciones = basico * pvac / 100
        if tiposal != 2:
            cesantias = base * pces / 100
            intcesa = base * pint / 100
            prima = base * ppri / 100
        else:
            cesantias = intcesa = prima = 0

        total_ps = cesantias + intcesa + prima + vacaciones

        empleado_id = data_nomina.idcontrato.idempleado.docidentidad

        if empleado_id not in empleados_datos:
            empleados_datos[empleado_id] = {
                'contrato': data_nomina.idcontrato.idcontrato,
                'nombre': f"{data_nomina.idcontrato.idempleado.papellido} {data_nomina.idcontrato.idempleado.sapellido} {data_nomina.idcontrato.idempleado.pnombre} {data_nomina.idcontrato.idempleado.snombre}",
                'costo': data_nomina.idcosto.idcosto,
                'base_ps': float(base),
                'cesantias': float(cesantias),
                'intcesa': float(intcesa),
                'prima': float(prima),
                'vacaciones': float(vacaciones),
                'total_ps': float(total_ps),
            }

    # Agregar los datos de empleados a la hoja de trabajo
    for empleado_id, datos in empleados_datos.items():
        ws.append([
            datos['contrato'],
            empleado_id,
            datos['nombre'],
            datos['costo'],
            datos['base_ps'],
            datos['cesantias'],
            datos['intcesa'],
            datos['prima'],
            datos['vacaciones'],
            datos['total_ps']
        ])

    # Aplicar formato decimal a las columnas relevantes
    for col in ['E', 'F', 'G', 'H', 'I', 'J']:
        for cell in ws[col]:
            cell.style = decimal_style

    # Ajustar el ancho de las columnas
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # Get the column name
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    # Guardar el archivo en memoria
    wb.save(output)
    output.seek(0)

    return output.getvalue()
