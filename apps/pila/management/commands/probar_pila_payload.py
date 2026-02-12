# nomiweb/apps/pila/management/commands/probar_pila_payload.py

import json
from django.core.management.base import BaseCommand
from apps.pila.services.payload_builder import build_payload_pila_minimo


class Command(BaseCommand):
    help = 'Genera y valida un payload PILA desde Nomiweb'

    def add_arguments(self, parser):
        parser.add_argument(
            '--empresa',
            type=int,
            required=True,
            help='ID de la empresa (idempresa)'
        )
        parser.add_argument(
            '--periodo',
            type=str,
            required=True,
            help='Periodo en formato YYYY-MM (ej: 2025-12)'
        )
        parser.add_argument(
            '--output',
            type=str,
            default=None,
            help='Ruta del archivo JSON de salida (opcional)'
        )
        parser.add_argument(
            '--pretty',
            action='store_true',
            help='Imprimir JSON con formato legible'
        )
        parser.add_argument(
            '--enviar',
            action='store_true',
            help='Enviar el payload al microservicio PILA'
        )

    def handle(self, *args, **options):
        empresa_id = options['empresa']
        periodo = options['periodo']
        output_file = options['output']
        pretty = options['pretty']
        enviar = options['enviar']

        self.stdout.write(self.style.WARNING(
            f"\n{'='*60}\n"
            f"Generando payload PILA\n"
            f"{'='*60}\n"
            f"Empresa ID: {empresa_id}\n"
            f"Periodo: {periodo}\n"
            f"{'='*60}\n"
        ))

        try:
            # Generar payload
            payload = build_payload_pila_minimo(
                empresa_id_interno=empresa_id,
                periodo=periodo
            )

            # Estadísticas
            num_empleados = len(payload.get('empleados', []))
            empresa_info = payload.get('empresa', {})

            self.stdout.write(self.style.SUCCESS(
                f"\n✅ Payload generado exitosamente\n"
            ))

            self.stdout.write(
                f"\n📊 Estadísticas:\n"
                f"  • Empresa: {empresa_info.get('razon_social', 'N/A')}\n"
                f"  • NIT: {empresa_info.get('nit', 'N/A')}\n"
                f"  • Tipo aportante: {empresa_info.get('tipo_aportante', 'N/A')}\n"
                f"  • Clase aportante: {empresa_info.get('clase_aportante', 'N/A')}\n"
                f"  • Total empleados: {num_empleados}\n"
            )

            # Validar estructura básica
            self._validar_estructura(payload)

            # Mostrar o guardar el JSON
            if pretty:
                json_str = json.dumps(payload, indent=2, ensure_ascii=False, default=str)
            else:
                json_str = json.dumps(payload, ensure_ascii=False, default=str)

            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(json_str)
                self.stdout.write(self.style.SUCCESS(
                    f"\n💾 Payload guardado en: {output_file}\n"
                ))
            else:
                self.stdout.write(f"\n📄 Payload JSON:\n{json_str}\n")

            # Enviar al microservicio si se solicita
            if enviar:
                self._enviar_a_microservicio(payload)

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"\n❌ Error al generar payload: {str(e)}\n"
            ))
            import traceback
            self.stdout.write(traceback.format_exc())
            return

    def _validar_estructura(self, payload):
        """Valida la estructura básica del payload"""
        errores = []
        advertencias = []

        # Validar empresa
        empresa = payload.get('empresa', {})
        if not empresa.get('nit'):
            errores.append("Empresa: NIT vacío")
        if not empresa.get('razon_social'):
            errores.append("Empresa: Razón social vacía")
        if not empresa.get('tipo_aportante'):
            advertencias.append("Empresa: Tipo aportante no especificado")

        # Validar empleados
        empleados = payload.get('empleados', [])
        if not empleados:
            advertencias.append("No hay empleados en el payload")

        for idx, emp in enumerate(empleados):
            emp_id = emp.get('id_empleado', f'#{idx+1}')
            
            # Validar identificación
            if not emp.get('tipo_doc'):
                errores.append(f"Empleado {emp_id}: tipo_doc vacío")
            if not emp.get('num_doc'):
                errores.append(f"Empleado {emp_id}: num_doc vacío")
            
            # Validar nombres
            if not emp.get('primer_nombre'):
                advertencias.append(f"Empleado {emp_id}: primer_nombre vacío")
            if not emp.get('primer_apellido'):
                advertencias.append(f"Empleado {emp_id}: primer_apellido vacío")
            
            # Validar DANE
            if not emp.get('cod_departamento'):
                advertencias.append(f"Empleado {emp_id}: cod_departamento vacío")
            if not emp.get('cod_municipio'):
                advertencias.append(f"Empleado {emp_id}: cod_municipio vacío")
            
            # Validar tarifa ARL
            tarifas = emp.get('tarifas', {})
            if not tarifas.get('arl'):
                advertencias.append(f"Empleado {emp_id}: tarifa ARL vacía")
            
            # Validar días
            dias = emp.get('dias', {})
            if not any([dias.get('salud'), dias.get('pension')]):
                advertencias.append(f"Empleado {emp_id}: días de cotización en 0")

        # Mostrar resultados
        if errores:
            self.stdout.write(self.style.ERROR(
                f"\n❌ Errores de validación ({len(errores)}):\n"
            ))
            for error in errores:
                self.stdout.write(self.style.ERROR(f"  • {error}"))
        
        if advertencias:
            self.stdout.write(self.style.WARNING(
                f"\n⚠️  Advertencias ({len(advertencias)}):\n"
            ))
            for adv in advertencias[:10]:  # Mostrar máximo 10
                self.stdout.write(self.style.WARNING(f"  • {adv}"))
            if len(advertencias) > 10:
                self.stdout.write(self.style.WARNING(
                    f"  ... y {len(advertencias) - 10} advertencias más\n"
                ))
        
        if not errores and not advertencias:
            self.stdout.write(self.style.SUCCESS(
                "\n✅ Validación: sin errores ni advertencias\n"
            ))

    def _enviar_a_microservicio(self, payload):
        """Envía el payload al microservicio PILA"""
        try:
            from apps.pila.services.pila_cliente import enviar_payload_pila
            
            self.stdout.write(self.style.WARNING(
                "\n📤 Enviando payload al microservicio PILA...\n"
            ))
            
            respuesta = enviar_payload_pila(payload)
            
            self.stdout.write(self.style.SUCCESS(
                f"\n✅ Payload enviado exitosamente\n"
                f"Respuesta: {json.dumps(respuesta, indent=2, ensure_ascii=False)}\n"
            ))
        except ImportError:
            self.stdout.write(self.style.ERROR(
                "\n❌ No se pudo importar pila_cliente. "
                "Verifica que el módulo exista.\n"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"\n❌ Error al enviar al microservicio: {str(e)}\n"
            ))
