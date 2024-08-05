
import openpyxl
from openpyxl.styles import PatternFill, Alignment
from io import BytesIO


output_path = './static/docs/excel_temporal.xlsx'

def generate_employee_excel(diccionario_empleados,month1,year1,month2,year2):
    # Crear un archivo en memoria
    output = BytesIO()
    
    # Crear un nuevo libro de trabajo y seleccionar la hoja activa
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reporte de acumulados"
    
    # Definir colores y alineación
    azul_fill = PatternFill(start_color="00B0F0", end_color="00B0F0", fill_type="solid")
    amarillo_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    centro_alignment = Alignment(horizontal="center", vertical="center")
    
    # Encabezados del reporte
    ws["A1"] = "Reporte de acumulados"
    ws.merge_cells("A1:H1")
    
    # Fila de Mes Inicial y Año
    ws["A2"] = "Mes Inicial"
    ws["B2"] = month1
    ws["C2"] = "Año"
    ws["D2"] = year1
    ws["E2"] = "Mes Final"
    ws["F2"] = month2
    ws["G2"] = "Año"
    ws["H2"] = year2
    
    #Estilos para la fila de Mes Inicial y Año
    for cell in ["A2", "E2", "C2", "G2"]:
        ws[cell].fill = azul_fill
    for cell in ["B2", "F2", "D2", "H2"]:
        ws[cell].fill = amarillo_fill
        ws[cell].alignment = centro_alignment
    
    #Datos de empleados
    row_start = 7
    for empleado, info in diccionario_empleados.items():
        # Escribir el nombre del empleado
        ws[f"B{row_start}"] = "Empleado"
        ws[f"C{row_start}"] = info["Empleado"]
        ws.merge_cells(f"C{row_start}:H{row_start}")
        ws[f"C{row_start}"].alignment = centro_alignment
        
        row_start += 1
        
        ws[f"B{row_start}"] = "Id Concepto"
        ws[f"C{row_start}"] = "Nombre Concepto"
        ws[f"D{row_start}"] = "Cantidad"
        ws[f"E{row_start}"] = "Valor"
        
        ws[f"B{row_start}"].fill = azul_fill
        ws[f"C{row_start}"].fill = azul_fill
        ws[f"D{row_start}"].fill = azul_fill
        ws[f"E{row_start}"].fill = azul_fill
        ws[f"B{row_start}"].alignment = centro_alignment
        ws[f"C{row_start}"].alignment = centro_alignment
        ws[f"D{row_start}"].alignment = centro_alignment
        ws[f"E{row_start}"].alignment = centro_alignment
        
        # Escribir los datos de los conceptos
        for concepto in info["data"]:
            row_start += 1
            ws[f"B{row_start}"] = concepto["idconcepto"]
            ws[f"C{row_start}"] = concepto["nombreconcepto"]
            ws[f"D{row_start}"] = concepto["cantidad"]
            ws[f"E{row_start}"] = concepto["valor"]
            
        row_start += 1
        #Dejar una fila en blanco después de cada empleado
        ws[f"B{row_start}"] = 'Total'
        ws[f"C{row_start}"] = info["total"]
        
        
        row_start += 2
    
    # Ajustar el ancho de las columnas
    for col in ['A', 'B', 'C', 'D', 'E']:
        ws.column_dimensions[col].width = 20
    
    wb.save(output_path)
    
    # Guardar el archivo en memoria
    wb.save(output)
    output.seek(0)
    
    
    return output.getvalue()
