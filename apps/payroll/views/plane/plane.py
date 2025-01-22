from django.shortcuts import render
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from apps.components.decorators import role_required
import pandas as pd
from openpyxl.utils.exceptions import InvalidFileException
from apps.common.models import Conceptosdenomina, Contratos


# Diccionario de mensajes de error con números como claves
error_messages = {
    '1': "Error code 1001: Id contrato inválido o faltante",
    '2': "Error code 1002: Concepto faltante o no es un número entero",
    '3': "Error code 1003: Contrato no encontrado",
    '4': "Error code 1004: El estado del contrato no es válido (debe estar activo)",
    '5': "Error code 1005: Concepto no encontrado",
    '6': "Error code 1006: El contrato no pertenece a la empresa actual",
    '7': "Error code 1007: Fila vacía o incompleta",
    '8': "Error code 1008: El valor debe ser mayor que cero",
    '9': "Error code 1009: Concepto duplicado para este contrato",
    '10': "Error code 1010: Faltan valores críticos (Id contrato, Concepto)",
    '11': "Error code 1012: La cantidad no puede ser negativa",
    '12': "Error code 1013: El contrato está cerrado o inactivo",
    '13': "Error code 1014: El valor no puede ser negativo",
    '15': "Error code 1015: El contrato y concepto ya existen",
    'general': "Error general: Ocurrió un error procesando el archivo",
}

@login_required
@role_required('accountant')
def plane(request, id):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    # Diccionario para almacenar los errores por fila
    errors = [] 
    
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        
        if not file.name.endswith('.xlsx'):
            errors['general'] = [{'error': 'Solo se aceptan archivos con extensión .xlsx.'}]
            return render(request, './payroll/plane.html', {'id': id, 'errors': errors})
        
        try:
            file_name = default_storage.save(file.name, file)
            file_path = default_storage.path(file_name)
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip()
            
            required_columns = ['Cedula', 'Id contrato', 'Concepto', 'cantidad', 'Valor']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                errors['general'] = [{'error': f'El archivo debe contener las columnas: {", ".join(missing_columns)}.'}]
                return render(request, './payroll/plane.html', {'id': id, 'errors': errors})
            
            for index, row in df.iterrows():
                row_errors = []
                
                # Validar y convertir valores
                try:
                    cedula = int(row['Cedula']) if not pd.isna(row['Cedula']) else None
                except ValueError:
                    cedula = None
                
                try:
                    contract_id = int(row['Id contrato']) if not pd.isna(row['Id contrato']) else None
                except ValueError:
                    contract_id = None
                
                try:
                    concepto = int(row['Concepto']) if not pd.isna(row['Concepto']) else None
                except ValueError:
                    concepto = None
                
                valor = row['Valor'] if not pd.isna(row['Valor']) else 0
                
                try:
                    cantidad = float(row['cantidad']) if not pd.isna(row['cantidad']) else 0  # Asigna 0 si está vacío o no presente
                    if cantidad <= 0:  # Si la cantidad es menor o igual a cero
                        cantidad = 0  # Asigna 0
                except ValueError:
                    cantidad = 0  # Asigna 0 si ocurre un error al convertir a float
                
                # Verificar valores y agregar claves de errores al diccionario
                
                if contract_id is None:
                    row_errors.append('1')  # Error por Id contrato inválido o faltante
                
                if concepto is None:
                    row_errors.append('2')  # Error por Concepto faltante o no es un número entero
                
                if concepto is not None:
                    try:
                        concepto_existente = Conceptosdenomina.objects.filter(idconcepto=concepto).exists()
                        if not concepto_existente:
                            row_errors.append('5')  # Concepto no encontrado
                    except Conceptosdenomina.DoesNotExist:
                        row_errors.append('5')
                
                if contract_id is not None:
                    try:
                        contrato_existente = Contratos.objects.filter(idcontrato=contract_id).first()
                        
                        if not contrato_existente:
                            row_errors.append('3')  # Error por contrato no encontrado
                        else:
                            if contrato_existente.estadocontrato != 1:
                                row_errors.append('4')  # El estado del contrato no es válido (no activo)
                            
                            if contrato_existente.id_empresa_id != idempresa:
                                row_errors.append('6')  # El contrato no pertenece a la empresa actual
                            
                            if contrato_existente.estadocontrato == 2:  # Asumiendo que 2 es estado 'cerrado' u otro
                                row_errors.append('12')  # El contrato está cerrado o inactivo
                        
                        
                    except Contratos.DoesNotExist:
                        row_errors.append('3')  # Error por contrato no encontrado
                
                # Validar fila vacía o incompleta
                if row.isnull().all():
                    row_errors.append('7')  # Fila vacía o incompleta
                
                # Validar si faltan valores críticos (Cédula, Id contrato, Concepto)
                if pd.isna(row['Id contrato']) or pd.isna(row['Concepto']):
                    row_errors.append('10')  # Faltan valores críticos
                
                # Validar cantidad negativa
                if cantidad < 0:
                    row_errors.append('11')  # La cantidad no puede ser negativa
                
                # Validar valor negativo
                if valor < 0:
                    row_errors.append('13')  # El valor no puede ser negativo
                
                # Si hay errores, guarda los detalles de la fila y los errores
                if row_errors:
                    errors.append({
                        'line': index + 1,  # Fila 1 en Excel corresponde al índice 0 en DataFrame
                        'contract_id': contract_id,
                        'identification': cedula,
                        'name': 'Nombre no disponible',  # Suponiendo que no se tiene la columna Nombre
                        'concept': concepto,
                        'value': valor,
                        'quantity': cantidad,
                        'error': "".join([f"<li>{error_messages[err]}</li>" for err in row_errors])
                    })
            
            default_storage.delete(file_name)
        
        except Exception as e:
            errors['general'] = [{'error': f'Ocurrió un error procesando el archivo: {str(e)}'}]
    
    return render(request, './payroll/plane.html', {'id': id, 'errors': errors})
