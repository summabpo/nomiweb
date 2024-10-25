import openpyxl
from openpyxl.styles import NamedStyle
from io import BytesIO
from apps.common.models import Nomina, Contratos, Conceptosfijos
from django.db.models import Q, Sum

def generate_nomina_excel(year, mth):
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
    nominas = Nomina.objects.filter(mesacumular=mth, anoacumular=year).select_related('idempleado', 'idcontrato', 'idcosto').order_by('idempleado__papellido')
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
            mesacumular=mth,
            anoacumular=year,
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

        empleado_id = data_nomina.idempleado.docidentidad

        if empleado_id not in empleados_datos:
            empleados_datos[empleado_id] = {
                'contrato': data_nomina.idcontrato.idcontrato,
                'nombre': f"{data_nomina.idempleado.papellido} {data_nomina.idempleado.sapellido} {data_nomina.idempleado.pnombre} {data_nomina.idempleado.snombre}",
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
