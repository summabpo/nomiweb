from django.db.models import Sum, Q, Case, When, Value, IntegerField , Count
from apps.common.models import  Contratos, Nomina ,Crearnomina , Nomina , NominaComprobantes
from django.db.models import Sum
from .datacompanies import datos_cliente
from apps.components.humani import format_value ,format_value_float , format_value_void


"""
Funciones para la Gestión de Nómina y Comprobantes

Estas funciones están diseñadas para generar comprobantes de nómina y resúmenes de nómina, realizando cálculos de devengados, descuentos, y el total neto.

1. `limitar_cadena(cadena, max_length=25)`
    Limita el tamaño de una cadena a un máximo de `max_length` caracteres. Si la cadena es más larga, se trunca y se le agrega "..." al final.

    Parámetros
    ----------
    cadena : str
        La cadena de texto a limitar.
    max_length : int, opcional
        La longitud máxima permitida para la cadena. El valor predeterminado es 25.

    Retorna
    -------
    str
        La cadena truncada o la misma cadena si no supera el límite de longitud.

    Ejemplo
    -------
    limitar_cadena('Empleado Ejemplo de Nombre', 10) -> 'Empleado...'


2. `genera_comprobante(idnomina, idcontrato)`
    Genera un comprobante de nómina con los datos de devengados y descuentos para un empleado específico.

    Parámetros
    ----------
    idnomina : int
        ID de la nómina.
    idcontrato : int
        ID del contrato del empleado.

    Retorna
    -------
    dict
        Un diccionario con los datos del comprobante, incluyendo la empresa, el empleado, los devengados, descuentos, y el total neto.
        Si no se encuentran los datos, devuelve un diccionario con valores nulos.

    Descripción
    -----------
    Esta función genera un comprobante de nómina para un empleado con los datos de los devengados y descuentos asociados al contrato. Además, formatea los valores de la nómina con separadores de miles. Calcula también los totales de devengados, descuentos y el total neto.

    Ejemplo
    -------
    genera_comprobante(1, 123) -> {'empresa': 'XYZ S.A.', 'nit': '123456789', ...}


3. `generate_summary(idnomina, idempresa)`
    Genera un resumen de la nómina para una empresa específica, agrupando los conceptos de ingresos y descuentos, y calculando el total de ingresos, descuentos y el neto.

    Parámetros
    ----------
    idnomina : int
        ID de la nómina.
    idempresa : int
        ID de la empresa.

    Retorna
    -------
    dict
        Un diccionario con el resumen de la nómina, que incluye los ingresos, descuentos, neto, y otros datos relevantes de la empresa.
        Si no se encuentran los datos, retorna `None`.

    Descripción
    -----------
    Esta función genera un resumen de la nómina, agrupando los ingresos y descuentos por concepto. También calcula la cantidad de empleados distintos, los totales de ingresos, descuentos y el total neto. Los valores se formatean con separadores de miles.

    Ejemplo
    -------
    generate_summary(1, 456) -> {'empresa': 'XYZ S.A.', 'grouped_nominas': [...], 'total_ingresos': '1,000,000', ...}
"""


def limitar_cadena(cadena, max_length=25):
    if len(cadena) > max_length:
        return cadena[:max_length-3] + '...'
    return cadena



def genera_comprobante(idnomina, idcontrato, date=1):
    contrato = Contratos.objects.filter(idcontrato=idcontrato).first()
    crear = Crearnomina.objects.filter(idnomina=idnomina).first()
    datac = datos_cliente(contrato.id_empresa.idempresa)
    if contrato:
        def limpiar(valor):
            """Limpia el valor solo si existe y es string."""
            if isinstance(valor, str):
                return valor.replace('no data', '').strip()
            return ''

        nombres = [
            limpiar(getattr(contrato.idempleado, 'papellido', None)),
            limpiar(getattr(contrato.idempleado, 'sapellido', None)),
            limpiar(getattr(contrato.idempleado, 'pnombre', None)),
            limpiar(getattr(contrato.idempleado, 'snombre', None)),
        ]

        nombre_completo = ' '.join(n for n in nombres if n)

        # Obtener datos de devengados y descuentos
        if date == 0:
            dataDevengado = Nomina.objects.filter(
                idcontrato=idcontrato, idnomina=idnomina, estadonomina=1, valor__gt=0
            ).order_by('idconcepto__codigo')
            dataDescuento = Nomina.objects.filter(
                idcontrato=idcontrato, idnomina=idnomina, estadonomina=1, valor__lt=0
            ).order_by('idconcepto__codigo')
        else:
            dataDevengado = Nomina.objects.filter(
                idcontrato=idcontrato, idnomina=idnomina, estadonomina=2, valor__gt=0
            ).order_by('idconcepto__codigo')
            dataDescuento = Nomina.objects.filter(
                idcontrato=idcontrato, idnomina=idnomina, estadonomina=2, valor__lt=0
            ).order_by('idconcepto__codigo')

        # Formatear valores con separadores y limpiar “no data”
        for item in dataDevengado:
            item.valor = format_value(item.valor)
            item.cantidad = format_value_float(item.cantidad)
            item.nombreconcepto = limitar_cadena(
                (item.idconcepto.nombreconcepto or '').replace('no data', '').strip()
            )

        for item in dataDescuento:
            item.valor = format_value(item.valor)
            item.cantidad = format_value_float(item.cantidad)
            item.nombreconcepto = limitar_cadena(
                (item.idconcepto.nombreconcepto or '').replace('no data', '').strip()
            )

        # Totales
        sumadataDevengado = dataDevengado.aggregate(total=Sum('valor'))['total'] or 0
        sumadataDescuento = dataDescuento.aggregate(total=Sum('valor'))['total'] or 0
        total = sumadataDevengado + sumadataDescuento

        # Periodo y otros datos
        periodo = f"{crear.fechainicial} hasta: {crear.fechafinal}"
        name = crear.nombrenomina
        centro = f"{contrato.idcosto.idcosto} - {(contrato.idcosto.nomcosto or '').replace('no data', '').strip()}"

        # Limpiar “no data” también en campos de cargo, EPS y pensión
        cargo = (contrato.cargo.nombrecargo or '').replace('no data', '').strip()
        eps = (contrato.codeps.entidad or '').replace('no data', '').strip()
        pension = (contrato.codafp.entidad or '').replace('no data', '').strip()

        context = {
            'empresa': datac['nombreempresa'],
            'nit': datac['nit'],
            'web': datac['website'],
            'logo': datac['logo'],
            'nombre_completo': (nombre_completo[:32] + '...') if len(nombre_completo) > 32 else nombre_completo,
            'cc': contrato.idempleado.docidentidad if contrato.idempleado.docidentidad else ' ',
            'idcon': idcontrato,
            'idnomi': idnomina,
            'fecha1': str(contrato.fechainiciocontrato),
            'cargo': (cargo[:32] + '...') if len(cargo) > 32 else cargo,
            'salario': format_value(contrato.salario),
            'cuenta': contrato.cuentanomina,
            'ccostos': centro,
            'periodos': periodo,
            'eps': (eps[:12] + '...') if len(eps) > 15 else eps,
            'pension': (pension[:12] + '...') if len(pension) > 15 else pension,
            'dataDevengado': dataDevengado,
            'dataDescuento': dataDescuento,
            'sumadataDevengado': format_value(sumadataDevengado),
            'sumadataDescuento': format_value(sumadataDescuento),
            'total': format_value(total),
            'mail': str((contrato.idempleado.email or '').replace('no data', '').strip()),
            'name': name,
        }

    else:
        context = {
            'nombre_completo': None,
            'cc': None,
            'idcon': None,
            'fecha1': None,
            'cargo': None,
            'dataDevengado': None,
            'dataDescuento': None,
            'sumadataDevengado': None,
        }

    return context


def generate_summary(idnomina,idempresa , data = 0):
    # Obtener datos del cliente
    datac = datos_cliente(idempresa)
    
    # Obtener la nómina y la información de creación de la nómina
    try:
        if data == 0 :
            nominas = Nomina.objects.filter(idnomina=idnomina , estadonomina = 1  ,idnomina__id_empresa = idempresa )
            nominas2 = Crearnomina.objects.get(idnomina=idnomina , estadonomina = 1 )
            nombre_nomina = nominas2.nombrenomina
        else : 
            nominas = Nomina.objects.filter(idnomina=idnomina ,estadonomina = 2 ,idnomina__id_empresa = idempresa )
            nominas2 = Crearnomina.objects.get(idnomina=idnomina ,estadonomina = 0 )
            nombre_nomina = nominas2.nombrenomina
            
    except Nomina.DoesNotExist or Crearnomina.DoesNotExist:
        # Manejar el caso de que no existan las nóminas
        return None  # O manejar el error de otra manera
    
    
    
    # Agregar un campo calculado para ingresos, descuentos y neto
    grouped_nominas = nominas.values('idconcepto__nombreconcepto','idconcepto__codigo').annotate(
        cantidad_total=Sum('cantidad'),
        ingresos=Sum(Case(
            When(valor__gt=0, then='valor'),
            default=Value(0),
            output_field=IntegerField()
        )),
        descuentos=Sum(Case(
            When(valor__lt=0, then='valor'),
            default=Value(0),
            output_field=IntegerField()
        )),
    ).order_by('-idconcepto__codigo')
    
    incapacidades = nominas.filter(idconcepto__nombreconcepto__icontains='Incapacidad').values(
        'idconcepto__nombreconcepto',
        'idconcepto__codigo'
    ).annotate(
        cantidad_total=Sum('cantidad'),
        valor_total=Sum('valor')
    ).order_by('idconcepto__codigo')

    
    
    # Separar ingresos y descuentos, y ordenar por idconcepto
    ingresos = [compect for compect in grouped_nominas if compect['ingresos'] > 0]
    descuentos = [compect for compect in grouped_nominas if compect['descuentos'] < 0]
    
    ingresos = sorted(ingresos, key=lambda x: x['idconcepto__codigo'])
    descuentos = sorted(descuentos, key=lambda x: x['idconcepto__codigo'])
    
    
    
    
    # ingresos.sort(key=lambda x: x['idconcepto__nombreconcepto'])
    # descuentos.sort(key=lambda x: x['idconcepto__nombreconcepto'])
    
    # Combinar ingresos y descuentos
    grouped_nominas = ingresos + descuentos

    # Obtener la cantidad de empleados distintos
    cantidad_empleados = nominas.values('idcontrato__idempleado').distinct().count()
    
    # Calcular totales de ingresos, descuentos y neto
    total_ingresos = nominas.filter(valor__gt=0).aggregate(total=Sum('valor'))['total'] or 0
    total_descuentos = nominas.filter(valor__lt=0).aggregate(total=Sum('valor'))['total'] or 0
    neto = total_ingresos + total_descuentos
    
    # Formatear los valores
    total_ingresos = format_value(total_ingresos)
    total_descuentos = format_value(total_descuentos)
    neto = format_value(neto)
    
    for compect in grouped_nominas:
        # Formatear los valores en el grupo de nóminas
        compect['ingresos'] = format_value_void(compect['ingresos'])
        compect['descuentos'] = format_value_void(compect['descuentos'])
    
    # Construir el contexto
    context = {
        'empresa': datac.get('nombreempresa', ''),
        'nit': datac.get('nit', ''),
        'web': datac.get('website', ''),
        'logo': datac.get('logo', ''),
        'grouped_nominas': grouped_nominas,
        'total_ingresos': total_ingresos,
        'total_descuentos': total_descuentos,
        'cantidad_empleados': cantidad_empleados,
        'neto': neto,
        'nombre_nomina': nombre_nomina
    }
    
    return context