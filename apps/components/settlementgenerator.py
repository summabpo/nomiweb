
from .datacompanies import datos_cliente
from apps.common.models  import Liquidacion
from .humani import format_value , format_value_float


def settlementgenerator(idliqui, idempresa):
    datac = datos_cliente(idempresa)
    liquidacion = Liquidacion.objects.filter(idliquidacion = idliqui ).first()
    nombre_completo = f"{liquidacion.idcontrato.idempleado.papellido} {liquidacion.idcontrato.idempleado.sapellido} {liquidacion.idcontrato.idempleado.pnombre} {liquidacion.idcontrato.idempleado.snombre}"
    
    context = {
            # empresa
            'empresa': str(datac['nombreempresa']),
            'nit': str(datac['nit']),
            'web': str(datac['website']),
            'logo': str(datac['logo']),   
            'rrhh': str(datac['contactorrhh']),   

            # empleado
            'nombre_completo': str(nombre_completo), 
            'cc': str(liquidacion.idcontrato.idempleado.docidentidad),
            'cargo': str(liquidacion.idcontrato.cargo),
            'ingreso': liquidacion.idcontrato.fechainiciocontrato,
            'terminación': liquidacion.idcontrato.fechafincontrato,
            'tipoc': str(liquidacion.idcontrato.tipocontrato.tipocontrato),
            'causa': str(liquidacion.motivoretiro),
            'salario': str(format_value(liquidacion.salario)),
            'sus': str(liquidacion.diassuspv),

            # data: se debe asegurar que 'data' sea una lista de diccionarios reales
            'data': [
                {
                    "concepto": 'Cesantias', 
                    "base": format_value_float(liquidacion.basecesantias),
                    "dias": str(liquidacion.diascesantias),  
                    "valor": format_value_float(liquidacion.cesantias),
                },
                {
                    "concepto": 'Intereses sobre Cesantias', 
                    "base": format_value_float(liquidacion.cesantias),
                    "dias": str(liquidacion.diascesantias),  
                    "valor": format_value_float(liquidacion.intereses),
                },
                {
                    "concepto": 'Prima de Servicios', 
                    "base": format_value_float(liquidacion.baseprima),
                    "dias": str(liquidacion.diasprimas),  
                    "valor": format_value_float(liquidacion.prima),
                },
                {
                    "concepto": 'Vacaciones', 
                    "base": format_value_float(liquidacion.basevacaciones),
                    "dias": str(liquidacion.diasvacaciones),  
                    "valor": str(liquidacion.vacaciones),
                },
            ],
            
            'total': format_value_float(liquidacion.totalliq),
        }
    
    
    
    return context 
