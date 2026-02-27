"""
Comando para verificar la estructura del archivo TXT PILA
Valida posiciones, longitudes y formato según LAYOUT_REGISTRO_02.md
"""

from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    help = 'Verifica estructura del archivo TXT PILA'

    def add_arguments(self, parser):
        parser.add_argument(
            '--archivo',
            type=str,
            help='Ruta al archivo TXT a verificar',
            default='apps/pila/archivos/PILA_NW-EMP1-2025-12_2025-12.txt'
        )

    def handle(self, *args, **options):
        archivo = options['archivo']
        
        if not os.path.exists(archivo):
            self.stdout.write(self.style.ERROR(f'❌ Archivo no encontrado: {archivo}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'\n📋 Verificando estructura: {archivo}\n'))
        
        with open(archivo, 'r', encoding='iso-8859-1') as f:
            lineas = f.readlines()
        
        errores = []
        advertencias = []
        
        # Verificar registro 01
        if lineas:
            reg01 = lineas[0].rstrip('\n\r')
            self.stdout.write(f'✅ Registro 01 encontrado (longitud: {len(reg01)})')
            
            if len(reg01) != 359:
                errores.append(f'❌ Registro 01: longitud incorrecta ({len(reg01)}, esperado 359)')
            
            # Verificar campos críticos del registro 01
            tipo_reg = reg01[0:2]
            if tipo_reg != '01':
                errores.append(f'❌ Registro 01: tipo incorrecto ({tipo_reg})')
            
            # DV (posición 226, 1-based = índice 225)
            dv = reg01[225] if len(reg01) > 225 else ''
            self.stdout.write(f'   - DV (pos 226): [{dv}]')
            
            # Tipo presentación (posición 248, 1-based = índice 247)
            tipo_pres = reg01[247] if len(reg01) > 247 else ''
            self.stdout.write(f'   - Tipo presentación (pos 248): [{tipo_pres}]')
            
            # Código ARL (posición 299-304, 1-based = índice 298-303)
            codigo_arl = reg01[298:304] if len(reg01) > 303 else ''
            self.stdout.write(f'   - Código ARL (pos 299-304): [{codigo_arl}]')
        
        # Verificar registros 02
        registros_02 = [l.rstrip('\n\r') for l in lineas[1:] if l.startswith('02')]
        self.stdout.write(f'\n✅ Registros 02 encontrados: {len(registros_02)}\n')
        
        # Analizar primer registro 02 en detalle
        if registros_02:
            self.stdout.write(self.style.WARNING('📊 Análisis del primer registro 02:\n'))
            reg = registros_02[0]
            
            if len(reg) != 693:
                errores.append(f'❌ Registro 02 línea 2: longitud incorrecta ({len(reg)}, esperado 693)')
            
            # Extraer campos clave (1-based positions, convert to 0-based)
            tipo_doc = reg[7:9]
            num_doc = reg[9:25].strip()
            papellido = reg[36:56].strip()
            sapellido = reg[56:86].strip()
            pnombre = reg[86:106].strip()
            snombre = reg[106:136].strip()
            
            # Días cotizados
            dias_pension = reg[183:185]
            dias_salud = reg[185:187]
            dias_arl = reg[187:189]
            dias_ccf = reg[189:191]
            
            # IBC
            salario_basico = reg[191:200]
            tipo_salario = reg[200]
            ibc_pension = reg[201:210]
            ibc_salud = reg[210:219]
            ibc_arl = reg[219:228]
            ibc_ccf = reg[228:237]
            
            # Tarifas
            tarifa_pension = reg[237:244]
            tarifa_salud = reg[307:314]
            tarifa_arl = reg[380:389]
            tarifa_ccf = reg[407:414]
            
            # Valores
            valor_pension = reg[244:253]
            valor_salud = reg[314:323]
            valor_arl = reg[398:407]
            valor_ccf = reg[414:423]
            
            # ARL
            codigo_arl = reg[506:512]
            clase_riesgo = reg[512]
            
            # Horas
            horas = reg[673:676]
            
            # Actividad económica
            act_economica = reg[686:693]
            
            self.stdout.write(f'   Tipo doc: {tipo_doc}')
            self.stdout.write(f'   Num doc: {num_doc}')
            self.stdout.write(f'   Nombre: {papellido} {sapellido}, {pnombre} {snombre}')
            self.stdout.write(f'\n   📅 Días cotizados:')
            self.stdout.write(f'      - Pensión: {dias_pension}')
            self.stdout.write(f'      - Salud: {dias_salud}')
            self.stdout.write(f'      - ARL: {dias_arl}')
            self.stdout.write(f'      - CCF: {dias_ccf}')
            
            if dias_salud != dias_arl:
                advertencias.append(f'⚠️  Días salud ({dias_salud}) ≠ días ARL ({dias_arl}) → Error 691')
            
            self.stdout.write(f'\n   💰 IBC:')
            self.stdout.write(f'      - Salario básico: ${salario_basico} (tipo: {tipo_salario})')
            self.stdout.write(f'      - Pensión: ${ibc_pension}')
            self.stdout.write(f'      - Salud: ${ibc_salud}')
            self.stdout.write(f'      - ARL: ${ibc_arl}')
            self.stdout.write(f'      - CCF: ${ibc_ccf}')
            
            if ibc_salud != ibc_arl:
                advertencias.append(f'⚠️  IBC salud ({ibc_salud}) ≠ IBC ARL ({ibc_arl}) → Error 691')
            
            self.stdout.write(f'\n   📊 Tarifas:')
            self.stdout.write(f'      - Pensión: {tarifa_pension}')
            self.stdout.write(f'      - Salud: {tarifa_salud}')
            self.stdout.write(f'      - ARL: {tarifa_arl}')
            self.stdout.write(f'      - CCF: {tarifa_ccf}')
            
            self.stdout.write(f'\n   💵 Valores aportados:')
            self.stdout.write(f'      - Pensión: ${valor_pension}')
            self.stdout.write(f'      - Salud: ${valor_salud}')
            self.stdout.write(f'      - ARL: ${valor_arl}')
            self.stdout.write(f'      - CCF: ${valor_ccf}')
            
            if valor_ccf == '000000000':
                errores.append(f'❌ Valor CCF = $0 → Error 195')
            
            self.stdout.write(f'\n   🏢 ARL:')
            self.stdout.write(f'      - Código ARL: {codigo_arl}')
            self.stdout.write(f'      - Clase riesgo: {clase_riesgo}')
            
            self.stdout.write(f'\n   ⏰ Horas laboradas: {horas}')
            if horas == '000':
                advertencias.append(f'⚠️  Horas laboradas = 0 → Error 806')
            
            self.stdout.write(f'   🏭 Actividad económica ARL: {act_economica}')
        
        # Verificar todos los registros 02 para patrones comunes
        self.stdout.write(self.style.WARNING(f'\n📊 Análisis de todos los registros 02:\n'))
        
        dias_diferentes = 0
        ibc_diferentes = 0
        ccf_cero = 0
        horas_cero = 0
        
        for i, reg in enumerate(registros_02, start=2):
            if len(reg) != 693:
                errores.append(f'❌ Línea {i}: longitud incorrecta ({len(reg)}, esperado 693)')
                continue
            
            dias_salud = reg[185:187]
            dias_arl = reg[187:189]
            ibc_salud = reg[210:219]
            ibc_arl = reg[219:228]
            valor_ccf = reg[414:423]
            horas = reg[673:676]
            
            if dias_salud != dias_arl:
                dias_diferentes += 1
            
            if ibc_salud != ibc_arl:
                ibc_diferentes += 1
            
            if valor_ccf == '000000000':
                ccf_cero += 1
            
            if horas == '000':
                horas_cero += 1
        
        self.stdout.write(f'   - Empleados con días salud ≠ ARL: {dias_diferentes}')
        self.stdout.write(f'   - Empleados con IBC salud ≠ ARL: {ibc_diferentes}')
        self.stdout.write(f'   - Empleados con valor CCF = $0: {ccf_cero}')
        self.stdout.write(f'   - Empleados con horas = 0: {horas_cero}')
        
        # Resumen
        self.stdout.write(self.style.WARNING(f'\n📋 RESUMEN:\n'))
        
        if errores:
            self.stdout.write(self.style.ERROR(f'❌ ERRORES CRÍTICOS ({len(errores)}):'))
            for err in errores:
                self.stdout.write(f'   {err}')
        
        if advertencias:
            self.stdout.write(self.style.WARNING(f'\n⚠️  ADVERTENCIAS ({len(advertencias)}):'))
            for adv in advertencias:
                self.stdout.write(f'   {adv}')
        
        if not errores and not advertencias:
            self.stdout.write(self.style.SUCCESS('✅ No se encontraron errores de estructura'))
        
        self.stdout.write('\n')
