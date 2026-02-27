# nomiweb/apps/pila/management/commands/descargar_pila_txt.py

import os
from django.core.management.base import BaseCommand, CommandError
from apps.pila.services.pila_cliente import descargar_archivo, consultar_planilla, PilaServiceError


class Command(BaseCommand):
    help = 'Descarga el archivo TXT PILA desde el microservicio'

    def add_arguments(self, parser):
        parser.add_argument(
            '--planilla-id',
            type=int,
            required=True,
            help='ID de la planilla en el microservicio PILA'
        )
        parser.add_argument(
            '--output',
            type=str,
            default=None,
            help='Ruta del archivo TXT de salida (opcional, por defecto: apps/pila/archivos/)'
        )
        parser.add_argument(
            '--tipo-planilla',
            type=str,
            choices=['K', 'E'],
            default=None,
            help='K: solo estudiantes (tipo 23). E: solo no estudiantes. Sin especificar: todos.'
        )
        parser.add_argument(
            '--ver',
            action='store_true',
            help='Mostrar las primeras líneas del archivo descargado'
        )

    def handle(self, *args, **options):
        planilla_id = options['planilla_id']
        output_file = options['output']
        tipo_planilla = options.get('tipo_planilla')
        ver = options['ver']

        self.stdout.write(self.style.WARNING(
            f"\n{'='*80}\n"
            f"Descarga de archivo TXT PILA\n"
            f"{'='*80}\n"
        ))

        try:
            # Primero consultar la planilla para obtener info
            self.stdout.write("📋 Consultando información de la planilla...")
            info = consultar_planilla(planilla_id)
            
            numero_interno = info.get('numero_interno', f'planilla_{planilla_id}')
            periodo = info.get('periodo', 'sin-periodo')
            estado = info.get('estado', 'DESCONOCIDO')
            resumen = info.get('resumen', {})
            
            self.stdout.write(self.style.SUCCESS(
                f"✓ Planilla encontrada:\n"
                f"  - ID: {planilla_id}\n"
                f"  - Número interno: {numero_interno}\n"
                f"  - Periodo: {periodo}\n"
                f"  - Estado: {estado}\n"
                f"  - Empleados procesados: {resumen.get('empleados_procesados', 0)}\n"
                f"  - Empleados con error: {resumen.get('empleados_con_error', 0)}\n"
            ))

            # Validar que no tenga errores
            if resumen.get('empleados_con_error', 0) > 0:
                self.stdout.write(self.style.WARNING(
                    f"⚠️  La planilla tiene empleados con error. "
                    f"El archivo puede estar incompleto."
                ))

            # Descargar archivo
            self.stdout.write("\n📥 Descargando archivo TXT desde el microservicio...")
            contenido = descargar_archivo(planilla_id, tipo_planilla=tipo_planilla)
            
            # Decodificar contenido (usar ISO-8859-1 para caracteres especiales)
            contenido_texto = contenido.decode('iso-8859-1')
            lineas = contenido_texto.split('\n')
            
            # Filtrar líneas vacías al final
            lineas = [l for l in lineas if l.strip()]
            
            self.stdout.write(self.style.SUCCESS(
                f"✓ Archivo descargado:\n"
                f"  - Tamaño: {len(contenido):,} bytes\n"
                f"  - Líneas: {len(lineas)}\n"
            ))

            # Validar estructura básica
            if len(lineas) > 0:
                linea_01 = lineas[0]
                if len(linea_01) == 359 and linea_01.startswith('01'):
                    self.stdout.write(self.style.SUCCESS(
                        f"  ✓ Registro 01 válido (359 caracteres)\n"
                    ))
                else:
                    self.stdout.write(self.style.ERROR(
                        f"  ✗ Registro 01 inválido (longitud: {len(linea_01)}, tipo: {linea_01[:2]})\n"
                    ))
                
                if len(lineas) > 1:
                    linea_02 = lineas[1]
                    if len(linea_02) == 693 and linea_02.startswith('02'):
                        self.stdout.write(self.style.SUCCESS(
                            f"  ✓ Registros 02 válidos ({len(lineas)-1} detalles de 693 caracteres)\n"
                        ))
                    else:
                        self.stdout.write(self.style.ERROR(
                            f"  ✗ Registro 02 inválido (longitud: {len(linea_02)}, tipo: {linea_02[:2]})\n"
                        ))

            # Determinar ruta de salida
            if output_file:
                ruta_salida = output_file
            else:
                # Usar carpeta por defecto
                carpeta_base = os.path.join('apps', 'pila', 'archivos')
                os.makedirs(carpeta_base, exist_ok=True)
                sufijo = f"_{tipo_planilla}" if tipo_planilla else ""
                nombre_archivo = f"PILA_{numero_interno}_{periodo}{sufijo}.txt"
                ruta_salida = os.path.join(carpeta_base, nombre_archivo)

            # Guardar archivo
            # Guardar con codificación ISO-8859-1 (Latin-1) para compatibilidad PILA
            with open(ruta_salida, 'w', encoding='iso-8859-1') as f:
                f.write(contenido_texto)

            self.stdout.write(self.style.SUCCESS(
                f"\n✓ Archivo guardado en: {ruta_salida}\n"
            ))

            # Mostrar primeras líneas si se solicitó
            if ver and len(lineas) > 0:
                self.stdout.write(self.style.WARNING(
                    f"\n{'='*80}\n"
                    f"Muestra del archivo (primeras 3 líneas):\n"
                    f"{'='*80}\n"
                ))
                
                for i, linea in enumerate(lineas[:3], 1):
                    self.stdout.write(f"\nLínea {i} ({len(linea)} chars):")
                    # Mostrar por segmentos para mejor legibilidad
                    self.stdout.write(f"  [1-80]: {linea[:80]}")
                    if len(linea) > 80:
                        self.stdout.write(f"  [81-160]: {linea[80:160]}")
                    if len(linea) > 200:
                        self.stdout.write(f"  [200-280]: {linea[199:280]}")
                    if len(linea) > 359:
                        self.stdout.write(f"  [360-440]: {linea[359:440]}")

            # Resumen final
            self.stdout.write(self.style.WARNING(
                f"\n{'='*80}\n"
                f"DESCARGA COMPLETADA\n"
                f"{'='*80}\n"
                f"Planilla ID: {planilla_id}\n"
                f"Archivo: {ruta_salida}\n"
                f"Líneas: {len(lineas)} (1 encabezado + {len(lineas)-1} detalles)\n"
                f"\nPróximos pasos:\n"
                f"1. Revisar el archivo generado\n"
                f"2. Subir a Aportes en Línea para validación\n"
                f"3. Corregir errores según mensajes del operador\n"
                f"{'='*80}\n"
            ))

        except PilaServiceError as e:
            raise CommandError(f"Error del servicio PILA: {e}")
        except Exception as e:
            raise CommandError(f"Error inesperado: {e}")
