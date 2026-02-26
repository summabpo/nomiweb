#!/usr/bin/env python
# apps/pila/scripts/analizar_txt_pila.py
"""
Analiza un archivo TXT PILA y valida campos según el layout oficial.
Identifica campos faltantes o incorrectos.
"""

import sys
import os


def analizar_registro_01(linea):
    """Analiza el registro 01 (encabezado)"""
    print("\n" + "="*80)
    print("ANÁLISIS REGISTRO 01 (Encabezado)")
    print("="*80)
    
    if len(linea) != 359:
        print(f"❌ ERROR: Longitud incorrecta: {len(linea)} (esperado: 359)")
        return
    
    campos = {
        "Tipo registro": (1, 2, linea[0:2]),
        "Código 3-7": (3, 7, linea[2:7]),
        "Razón social": (8, 207, linea[7:207].strip()),
        "Tipo doc": (208, 209, linea[207:209]),
        "NIT": (210, 218, linea[209:218]),
        "Flag 226": (226, 226, linea[225:226]),
        "Tipo planilla": (227, 227, linea[226:227]),
        "Periodo cotización": (305, 311, linea[304:311]),
        "Periodo pago": (312, 318, linea[311:318]),
        "Control": (339, 359, linea[338:359].strip()),
    }
    
    print("\nCampos identificados:")
    for nombre, (inicio, fin, valor) in campos.items():
        print(f"  {nombre:20} [{inicio:3}-{fin:3}]: '{valor}'")
    
    # Validaciones
    print("\nValidaciones:")
    issues = []
    
    if campos["Tipo registro"][2] != "01":
        issues.append("❌ Tipo registro debe ser '01'")
    else:
        print("  ✓ Tipo registro correcto")
    
    if not campos["Razón social"][2]:
        issues.append("❌ Razón social vacía")
    else:
        print(f"  ✓ Razón social: {campos['Razón social'][2][:50]}...")
    
    if campos["Tipo doc"][2] != "NI":
        issues.append("❌ Tipo doc debe ser 'NI' para empresas")
    else:
        print("  ✓ Tipo documento correcto (NI)")
    
    if not campos["NIT"][2].strip():
        issues.append("❌ NIT vacío")
    else:
        print(f"  ✓ NIT: {campos['NIT'][2].strip()}")
    
    if campos["Tipo planilla"][2] not in ["E", "I", "C", "A"]:
        issues.append(f"⚠️  Tipo planilla '{campos['Tipo planilla'][2]}' no estándar")
    else:
        print(f"  ✓ Tipo planilla: {campos['Tipo planilla'][2]}")
    
    periodo_cot = campos["Periodo cotización"][2]
    if len(periodo_cot.strip()) != 7:
        issues.append(f"❌ Periodo cotización inválido: '{periodo_cot}'")
    else:
        print(f"  ✓ Periodo cotización: {periodo_cot}")
    
    # Campos potencialmente faltantes
    print("\n⚠️  Campos que pueden necesitar revisión:")
    print(f"  - Campo 19 (Total cotizantes): necesita validación")
    print(f"  - Campo 20 (Valor total nómina): necesita validación")
    print(f"  - Campos 219-225, 228-304, 319-338: verificar si están completos")
    
    return issues


def analizar_registro_02(linea, num_linea):
    """Analiza un registro 02 (detalle)"""
    if num_linea == 1:  # Solo primera línea para no saturar
        print("\n" + "="*80)
        print("ANÁLISIS REGISTRO 02 (Detalle - Primera línea)")
        print("="*80)
    
    if len(linea) != 693:
        print(f"❌ Línea {num_linea}: Longitud incorrecta: {len(linea)} (esperado: 693)")
        return ["Longitud incorrecta"]
    
    if num_linea == 1:
        campos = {
            "Tipo registro": (1, 2, linea[0:2]),
            "Secuencia": (3, 7, linea[2:7]),
            "Tipo doc": (8, 9, linea[7:9]),
            "Num doc": (10, 25, linea[9:25].strip()),
            "Tipo cotizante": (26, 27, linea[25:27]),
            "Subtipo": (28, 29, linea[27:29]),
            "Cod depto": (32, 33, linea[31:33]),
            "Cod municipio": (34, 36, linea[33:36]),
            "Primer apellido": (37, 56, linea[36:56].strip()),
            "Segundo apellido": (57, 86, linea[56:86].strip()),
            "Primer nombre": (87, 106, linea[86:106].strip()),
            "Segundo nombre": (107, 136, linea[106:136].strip()),
            "ING": (137, 137, linea[136:137]),
            "RET": (138, 138, linea[137:138]),
            "VST": (145, 145, linea[144:145]),
            "IRL": (152, 153, linea[151:153]),
            "AFP": (154, 159, linea[153:159].strip()),
            "EPS": (166, 171, linea[165:171].strip()),
            "CCF": (178, 183, linea[177:183].strip()),
            "Días salud": (184, 185, linea[183:185]),
            "Días pensión": (186, 187, linea[185:187]),
            "Días ARL": (188, 189, linea[187:189]),
            "Días CCF": (190, 191, linea[189:191]),
            "Salario básico": (192, 200, linea[191:200]),
            "IBC pensión": (202, 210, linea[201:210]),
            "IBC salud": (211, 219, linea[210:219]),
            "IBC ARL": (220, 228, linea[219:228]),
            "IBC CCF": (229, 237, linea[228:237]),
            "Tarifa pensión": (238, 244, linea[237:244]),
            "Cotiz pensión": (245, 253, linea[244:253]),
            "Tarifa salud": (308, 314, linea[307:314]),
            "Cotiz salud": (315, 323, linea[314:323]),
            "ARL código": (507, 512, linea[506:512].strip()),
            "Clase riesgo": (513, 513, linea[512:513]),
        }
        
        print("\nCampos principales:")
        for nombre, (inicio, fin, valor) in list(campos.items())[:15]:
            print(f"  {nombre:20} [{inicio:3}-{fin:3}]: '{valor}'")
        
        print("\nCampos de entidades:")
        for nombre in ["AFP", "EPS", "CCF", "ARL código"]:
            inicio, fin, valor = campos[nombre]
            print(f"  {nombre:20} [{inicio:3}-{fin:3}]: '{valor}'")
        
        print("\nCampos de días:")
        for nombre in ["Días salud", "Días pensión", "Días ARL", "Días CCF"]:
            inicio, fin, valor = campos[nombre]
            print(f"  {nombre:20} [{inicio:3}-{fin:3}]: '{valor}'")
        
        print("\nValidaciones:")
        issues = []
        
        if campos["Tipo registro"][2] != "02":
            issues.append("❌ Tipo registro debe ser '02'")
            print("  ❌ Tipo registro incorrecto")
        else:
            print("  ✓ Tipo registro correcto")
        
        if not campos["Num doc"][2]:
            issues.append("❌ Número documento vacío")
            print("  ❌ Número documento vacío")
        else:
            print(f"  ✓ Número documento: {campos['Num doc'][2]}")
        
        if not campos["Primer apellido"][2]:
            issues.append("❌ Primer apellido vacío")
            print("  ❌ Primer apellido vacío")
        else:
            print(f"  ✓ Primer apellido: {campos['Primer apellido'][2]}")
        
        if not campos["Primer nombre"][2]:
            issues.append("❌ Primer nombre vacío")
            print("  ❌ Primer nombre vacío")
        else:
            print(f"  ✓ Primer nombre: {campos['Primer nombre'][2]}")
        
        # Validar entidades
        if campos["AFP"][2]:
            print(f"  ✓ AFP: {campos['AFP'][2]}")
        else:
            issues.append("⚠️  AFP vacío")
            print("  ⚠️  AFP vacío (puede ser válido si no aplica)")
        
        if campos["EPS"][2]:
            print(f"  ✓ EPS: {campos['EPS'][2]}")
        else:
            issues.append("⚠️  EPS vacío")
            print("  ⚠️  EPS vacío (puede ser válido si no aplica)")
        
        if campos["CCF"][2]:
            print(f"  ✓ CCF: {campos['CCF'][2]}")
        else:
            issues.append("⚠️  CCF vacío")
            print("  ⚠️  CCF vacío (puede ser válido si no aplica)")
        
        # Campos potencialmente faltantes o incompletos
        print("\n⚠️  Campos que necesitan revisión:")
        
        # Verificar cola (333-693)
        cola = linea[332:693]
        if cola.strip() == "":
            print("  ❌ Campos 333-693 completamente vacíos")
            print("     Estos incluyen:")
            print("     - Autorizaciones IGE/LMA (333-371)")
            print("     - Valores IGE/LMA (372-380)")
            print("     - Tarifa ARL (381-389)")
            print("     - Centro trabajo (390-398)")
            print("     - Cotización ARL (399-407)")
            print("     - Parafiscales (408-487)")
            print("     - Tipo doc principal (488-489) - cotizante 40")
            print("     - Código ARL (507-512)")
            print("     - Fechas novedades (515-664)")
            print("     - Actividad económica (687-693)")
        else:
            # Verificar campos específicos importantes
            if linea[380:389].strip() == "":
                print("  ⚠️  Tarifa ARL vacía (381-389)")
            if linea[506:512].strip() == "":
                print("  ⚠️  Código ARL vacío (507-512)")
            if linea[512:513].strip() == "":
                print("  ⚠️  Clase de riesgo vacía (513)")
            if linea[686:693].strip() == "":
                print("  ⚠️  Actividad económica vacía (687-693)")
        
        return issues
    
    return []


def main():
    if len(sys.argv) < 2:
        print("Uso: python analizar_txt_pila.py <archivo.txt>")
        sys.exit(1)
    
    archivo = sys.argv[1]
    
    if not os.path.exists(archivo):
        print(f"❌ Error: Archivo no encontrado: {archivo}")
        sys.exit(1)
    
    print("="*80)
    print("ANÁLISIS DE ARCHIVO TXT PILA")
    print("="*80)
    print(f"Archivo: {archivo}")
    print(f"Tamaño: {os.path.getsize(archivo):,} bytes")
    
    with open(archivo, 'r', encoding='utf-8') as f:
        lineas = [l.rstrip('\n') for l in f.readlines()]
    
    print(f"Líneas: {len(lineas)}")
    
    if len(lineas) == 0:
        print("❌ Error: Archivo vacío")
        sys.exit(1)
    
    # Analizar registro 01
    issues_01 = analizar_registro_01(lineas[0])
    
    # Analizar registros 02
    all_issues_02 = []
    for i, linea in enumerate(lineas[1:], 1):
        issues = analizar_registro_02(linea, i)
        all_issues_02.extend(issues)
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN DEL ANÁLISIS")
    print("="*80)
    print(f"Total líneas: {len(lineas)}")
    print(f"  - Registro 01: 1")
    print(f"  - Registros 02: {len(lineas)-1}")
    
    if issues_01:
        print(f"\n⚠️  Registro 01: {len(issues_01)} problemas encontrados")
        for issue in issues_01:
            print(f"  {issue}")
    else:
        print("\n✓ Registro 01: Sin problemas críticos")
    
    if all_issues_02:
        print(f"\n⚠️  Registros 02: {len(all_issues_02)} problemas encontrados")
    else:
        print("\n✓ Registros 02: Sin problemas críticos de longitud")
    
    print("\n" + "="*80)
    print("RECOMENDACIONES")
    print("="*80)
    print("1. Completar campos 333-693 del registro 02 (ver tareas 2.1.1 y 2.4.1)")
    print("2. Validar registro 01 completo (ver tarea 2.5.1)")
    print("3. Probar carga en Aportes en Línea (tarea 2.6.2)")
    print("="*80)


if __name__ == "__main__":
    main()
