from django.db.models import Sum, Q, Case, When, Value, IntegerField , Count
from apps.common.models import  Contratos, Nomina ,Crearnomina , Nomina , NominaComprobantes
from django.db.models import Sum
from .datacompanies import datos_cliente
from apps.components.humani import format_value ,format_value_float , format_value_void

def limitar_cadena(cadena, max_length=25):
    if len(cadena) > max_length:
        return cadena[:max_length-3] + '...'
    return cadena


def genera_comprobante(idnomina, idcontrato):
    
    contrato = Contratos.objects.filter(idcontrato=idcontrato).first()
    crear = Crearnomina.objects.filter(idnomina=idnomina).first()
    datac = datos_cliente(contrato.id_empresa.idempresa)
    
    if contrato:
        nombre_completo = f"{contrato.idempleado.papellido} {contrato.idempleado.sapellido} {contrato.idempleado.pnombre} {contrato.idempleado.snombre}"

        # Obtener datos de devengados y descuentos
        dataDevengado = Nomina.objects.filter(idcontrato=idcontrato, idnomina=idnomina, valor__gt=0).order_by('idconcepto')
        dataDescuento = Nomina.objects.filter(idcontrato=idcontrato, idnomina=idnomina, valor__lt=0).order_by('idconcepto')

        # Formatear valores con puntos para los miles en dataDevengado
        for item in dataDevengado:
            item.valor = format_value(item.valor) # Aplica formato de separador de mil
            item.cantidad = format_value_float(item.cantidad)
            item.nombreconcepto = limitar_cadena(item.idconcepto.nombreconcepto)
            
        for item in dataDescuento:
            item.valor = format_value(item.valor) # Aplica formato de separador de miles
            item.cantidad = format_value_float(item.cantidad)
            item.nombreconcepto = limitar_cadena(item.idconcepto.nombreconcepto)

        # Calcular la suma de todos los valores en dataDevengado
        sumadataDevengado = dataDevengado.aggregate(total=Sum('valor'))['total'] or 0
        
        sumadataDescuento = dataDescuento.aggregate(total=Sum('valor'))['total'] or 0
        
        total = sumadataDevengado + sumadataDescuento
        
        
        
        periodo = f" {crear.fechainicial} hasta: {crear.fechafinal}"
        name = crear.nombrenomina
        centro = f"{contrato.idcosto.idcosto} - {contrato.idcosto.nomcosto}"
    
        
        context = {
            #empresa
            'empresa':datac['nombreempresa'],
            'nit': datac['nit'],
            'web':datac['website'],
            'logo':datac['logo'],        
            # nomina y empleado 
            'nombre_completo': nombre_completo,
            'cc': contrato.idempleado.docidentidad,
            'idcon': idcontrato,
            'idnomi': idnomina,
            'fecha1': str(contrato.fechainiciocontrato),
            'cargo': contrato.cargo, #!
            'salario': format_value(contrato.salario),
            'cuenta': contrato.cuentanomina,
            'ccostos': centro,
            'periodos': periodo,
            'eps': contrato.codeps,#!
            'pension': contrato.codafp,#!
            'dataDevengado': dataDevengado,
            'dataDescuento': dataDescuento,
            'sumadataDevengado': format_value(sumadataDevengado), # Formatear la suma con separador de miles
            'sumadataDescuento': format_value(sumadataDescuento), 
            'total':format_value(total),
            'mail':str(contrato.idempleado.email),
            'name':name,
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


def generate_summary(idnomina,idempresa):
    # Obtener datos del cliente
    datac = datos_cliente(idempresa)
    
    # Obtener la nómina y la información de creación de la nómina
    try:
        nominas = Nomina.objects.filter(idnomina=idnomina)
        nominas2 = Crearnomina.objects.get(idnomina=idnomina)
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
    ).order_by('idconcepto__codigo')
    
    # Separar ingresos y descuentos, y ordenar por idconcepto
    ingresos = [compect for compect in grouped_nominas if compect['ingresos'] > 0]
    descuentos = [compect for compect in grouped_nominas if compect['descuentos'] < 0]
    
    ingresos.sort(key=lambda x: x['idconcepto__nombreconcepto'])
    descuentos.sort(key=lambda x: x['idconcepto__nombreconcepto'])
    
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