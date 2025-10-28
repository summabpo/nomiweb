
from .datacompanies import datos_cliente
from apps.common.models  import Liquidacion
from .humani import format_value , format_value_float

"""
Genera los datos necesarios para la liquidación de un empleado, incluyendo detalles sobre la empresa y el empleado, así como los conceptos de liquidación.

### Función `settlementgenerator(idliqui, idempresa)`

Esta función recibe el ID de una liquidación y el ID de una empresa, recupera los datos correspondientes a la liquidación, y genera un contexto que incluye información sobre la empresa, el empleado y los conceptos relacionados con la liquidación (cesantías, intereses, primas, vacaciones, etc.).

#### Parámetros:
- `idliqui` (int): El ID de la liquidación que se desea obtener.
- `idempresa` (int): El ID de la empresa asociada con la liquidación.

#### Retorna:
- `context` (dict): Un diccionario con los datos relevantes de la liquidación, los cuales incluyen detalles de la empresa, el empleado y los conceptos de liquidación.

#### Estructura de `context`:
1. **Información de la Empresa**:
   - `'empresa'`: Nombre de la empresa.
   - `'nit'`: Número de identificación tributaria (NIT) de la empresa.
   - `'web'`: Página web de la empresa.
   - `'logo'`: Logo de la empresa.
   - `'rrhh'`: Información de contacto del departamento de recursos humanos de la empresa.

2. **Información del Empleado**:
   - `'nombre_completo'`: Nombre completo del empleado (primer apellido, segundo apellido, primer nombre y segundo nombre).
   - `'cc'`: Número de documento de identidad del empleado.
   - `'cargo'`: Cargo del empleado.
   - `'ingreso'`: Fecha de inicio del contrato del empleado.
   - `'terminación'`: Fecha de finalización del contrato del empleado.
   - `'tipoc'`: Tipo de contrato del empleado.
   - `'causa'`: Motivo de retiro del empleado (si aplica).
   - `'salario'`: Salario del empleado, formateado con separadores de miles.
   - `'sus'`: Número de días de suspensión (si aplica).

3. **Datos de Liquidación** (Conceptos):
   - Una lista de diccionarios, cada uno representando un concepto de la liquidación:
     - `'concepto'`: Nombre del concepto de liquidación (por ejemplo, "Cesantías", "Intereses sobre Cesantías", "Prima de Servicios", etc.).
     - `'base'`: La base de cálculo para el concepto, formateada con separadores de miles.
     - `'dias'`: Número de días relacionados con el concepto.
     - `'valor'`: El valor calculado para el concepto, formateado con separadores de miles.

4. **Total de Liquidación**:
   - `'total'`: El valor total de la liquidación del empleado, formateado con separadores de miles.

#### Descripción:
La función consulta la base de datos para obtener los detalles de la liquidación del empleado usando el `idliqui`, y los detalles de la empresa utilizando el `idempresa`. Los valores numéricos como salarios, cesantías, y otros conceptos de la liquidación son formateados utilizando las funciones `format_value` y `format_value_float` para incluir separadores de miles y decimales cuando sea necesario.

#### Ejemplo de Uso:
```python
context = settlementgenerator(1, 101)  # Recupera los datos de liquidación del empleado con ID 1 en la empresa con ID 101.

####  Excepciones:
La función retorna un diccionario vacío si no se encuentra la liquidación o los datos asociados al empleado o empresa.

Asegúrate de que los idliqui y idempresa proporcionados sean válidos y existan en la base de datos para evitar errores.

"""

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
            'cargo': str(liquidacion.idcontrato.cargo.nombrecargo),
            'ingreso': liquidacion.idcontrato.fechainiciocontrato,
            'terminación': liquidacion.idcontrato.fechafincontrato if liquidacion.idcontrato.fechafincontrato else '--' ,
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
