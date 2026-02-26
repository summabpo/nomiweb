"""
Comando para verificar el cálculo del IBC de un empleado específico
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Verifica el cálculo del IBC de un empleado'

    def add_arguments(self, parser):
        parser.add_argument(
            '--num-doc',
            type=str,
            required=True,
            help='Número de documento del empleado'
        )
        parser.add_argument(
            '--periodo',
            type=str,
            default='2025-12',
            help='Periodo en formato YYYY-MM'
        )

    def handle(self, *args, **options):
        num_doc = options['num_doc']
        periodo = options['periodo']
        
        ano, mes_num = periodo.split('-')
        ano = int(ano)
        mes_num = int(mes_num)
        
        # Mapeo de meses
        meses = {
            1: 'ENERO', 2: 'FEBRERO', 3: 'MARZO', 4: 'ABRIL',
            5: 'MAYO', 6: 'JUNIO', 7: 'JULIO', 8: 'AGOSTO',
            9: 'SEPTIEMBRE', 10: 'OCTUBRE', 11: 'NOVIEMBRE', 12: 'DICIEMBRE'
        }
        mesacumular = meses[mes_num]
        
        self.stdout.write(self.style.SUCCESS(f'\n🔍 Verificando IBC para empleado {num_doc} en {periodo}\n'))
        
        # 1. Buscar el contrato
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT c.idcontrato, ce.pnombre, ce.papellido, c.salario
                FROM contratos c
                JOIN contratosemp ce ON ce.idempleado = c.idempleado_id
                WHERE ce.docidentidad::text = %s
                LIMIT 1
            """, [num_doc])
            
            row = cursor.fetchone()
            if not row:
                self.stdout.write(self.style.ERROR(f'❌ No se encontró contrato para documento {num_doc}'))
                return
            
            idcontrato, pnombre, papellido, salario = row
            self.stdout.write(f'✅ Contrato encontrado:')
            self.stdout.write(f'   - ID: {idcontrato}')
            self.stdout.write(f'   - Nombre: {pnombre} {papellido}')
            self.stdout.write(f'   - Salario: ${salario:,.0f}')
        
        # 2. Buscar movimientos de nómina con indicador 6 (basesegsocial)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    cd.nombreconcepto,
                    n.valor,
                    cdi.indicador_id,
                    i.nombre AS indicador_nombre
                FROM nomina n
                JOIN crearnomina cn ON cn.idnomina = n.idnomina_id
                JOIN anos a ON a.idano = cn.anoacumular_id
                JOIN conceptosdenomina cd ON cd.idconcepto = n.idconcepto_id
                LEFT JOIN conceptosdenomina_indicador cdi ON cdi.conceptosdenomina_id = cd.idconcepto
                LEFT JOIN indicadores i ON i.id = cdi.indicador_id
                WHERE n.idcontrato_id = %s
                  AND cn.mesacumular = %s
                  AND a.ano = %s
                  AND cn.estadonomina = FALSE
                  AND n.estadonomina = 2
                ORDER BY cd.nombreconcepto, cdi.indicador_id
            """, [idcontrato, mesacumular, ano])
            
            rows = cursor.fetchall()
            
            if not rows:
                self.stdout.write(self.style.WARNING(f'\n⚠️  No se encontraron movimientos de nómina para este empleado en {periodo}'))
                return
            
            self.stdout.write(f'\n📊 Movimientos de nómina encontrados ({len(rows)}):\n')
            
            total_ibc = 0
            conceptos_con_indicador_6 = []
            
            for nombreconcepto, valor, indicador_id, indicador_nombre in rows:
                indicador_str = f'{indicador_id} ({indicador_nombre})' if indicador_id else 'Sin indicador'
                self.stdout.write(f'   - {nombreconcepto}: ${valor:,.0f} → {indicador_str}')
                
                if indicador_id == 6:  # basesegsocial
                    total_ibc += valor
                    conceptos_con_indicador_6.append((nombreconcepto, valor))
            
            self.stdout.write(f'\n💰 Cálculo del IBC (indicador 6 - basesegsocial):')
            
            if conceptos_con_indicador_6:
                for nombreconcepto, valor in conceptos_con_indicador_6:
                    self.stdout.write(f'   + {nombreconcepto}: ${valor:,.0f}')
                self.stdout.write(f'   {"="*50}')
                self.stdout.write(self.style.SUCCESS(f'   TOTAL IBC: ${total_ibc:,.0f}'))
            else:
                self.stdout.write(self.style.WARNING('   ⚠️  No hay conceptos con indicador 6 (basesegsocial)'))
        
        # 3. Verificar qué hay en el payload.json
        import json
        import os
        
        payload_path = 'apps/pila/payloads/payload.json'
        if os.path.exists(payload_path):
            with open(payload_path, 'r') as f:
                payload = json.load(f)
            
            empleado_payload = None
            for emp in payload.get('empleados', []):
                if emp.get('num_doc') == num_doc:
                    empleado_payload = emp
                    break
            
            if empleado_payload:
                self.stdout.write(f'\n📄 Datos en payload.json:')
                self.stdout.write(f'   - Salario básico: ${empleado_payload.get("salario_basico")}')
                self.stdout.write(f'   - IBC salud: ${empleado_payload["ibc"]["salud"]}')
                self.stdout.write(f'   - IBC pensión: ${empleado_payload["ibc"]["pension"]}')
                self.stdout.write(f'   - IBC ARL: ${empleado_payload["ibc"]["arl"]}')
                self.stdout.write(f'   - IBC parafiscales: ${empleado_payload["ibc"]["parafiscales"]}')
                self.stdout.write(f'   - Días salud: {empleado_payload["dias"]["salud"]}')
                self.stdout.write(f'   - Días ARL: {empleado_payload["dias"]["arl"]}')
                
                # Comparar
                ibc_payload = int(empleado_payload["ibc"]["salud"])
                if ibc_payload == total_ibc:
                    self.stdout.write(self.style.SUCCESS(f'\n✅ IBC en payload coincide con BD'))
                else:
                    self.stdout.write(self.style.ERROR(f'\n❌ IBC en payload (${ibc_payload:,}) ≠ IBC calculado desde BD (${total_ibc:,})'))
        
        self.stdout.write('\n')
