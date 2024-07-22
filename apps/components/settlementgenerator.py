
from .datacompanies import datos_cliente
from apps.companies.models import Liquidacion
from .humani import format_value


def settlementgenerator(idliqui):
    datac = datos_cliente()
    liquidacion = Liquidacion.objects.filter(idliquidacion = idliqui ).first()
    nombre_completo = f"{liquidacion.idempleado.papellido} {liquidacion.idempleado.sapellido} {liquidacion.idempleado.pnombre} {liquidacion.idempleado.snombre}"
    
    print(type(liquidacion.salario))
    context  = {
        #empresa
        'empresa':datac['nombreempresa'],
        'nit': datac['nit'],
        'web':datac['website'],
        'logo':datac['logo'],   
        
        # empleado
        
        'nombre_completo': nombre_completo, 
        'cc':liquidacion.docidentidad,
        'cargo':liquidacion.idcontrato.cargo,
        'ingreso':liquidacion.idcontrato.fechainiciocontrato,
        'terminación':liquidacion.idcontrato.fechafincontrato,
        'tipoc':liquidacion.idcontrato.tipocontrato.tipocontrato,
        'causa':liquidacion.motivoretiro,
        'salario':format_value(liquidacion.salario),
        'sus':liquidacion.diassuspv,
    }
    
    
    return context 
