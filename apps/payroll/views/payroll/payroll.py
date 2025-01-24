from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Crearnomina , Tipodenomina ,Subcostos,Costos,Conceptosdenomina , Empresa , Anos , Nomina , Contratos
from apps.payroll.forms.PayrollForm import PayrollForm
from django.contrib import messages
from .common import generar_nombre_nomina , MES_CHOICES
from apps.payroll.forms.ConceptForm import ConceptForm
from datetime import timedelta
from django.http import JsonResponse
from django.views import View
from apps.components.humani import format_value
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.http import JsonResponse
from django.core.files.storage import default_storage

@login_required
@role_required('accountant')
def payroll(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = PayrollForm()
    nominas = Crearnomina.objects.filter(estadonomina=True, id_empresa_id=idempresa).order_by('-idnomina')
    error = False

    if request.method == 'POST':
        form = PayrollForm(request.POST)
        if form.is_valid():
            try:
                # Obtener datos del formulario
                tiponomina_id = form.cleaned_data['tiponomina']

                # Buscar los objetos relacionados
                tiponomina = Tipodenomina.objects.get(idtiponomina=tiponomina_id)

                # Calcular mes y año acumulados a partir de fechainicial
                fechainicial = form.cleaned_data['fechainicial']
                fechafinal = form.cleaned_data['fechafinal']

                # Calcular días de nómina
                dias_nomina = (fechafinal - fechainicial).days + 1  # Incluir día inicial

                mes_numero = fechainicial.month  # Obtener el número del mes (1-12)
                mes_acumular = MES_CHOICES[mes_numero][0] if mes_numero else ''
                
                ano_acumular = Anos.objects.get(ano=fechainicial.year)  # Año de la fecha
                
                tipo_nomina_text = tiponomina.tipodenomina 

                empresa = Empresa.objects.get(idempresa=idempresa)

                # Crear instancia de Crearnomina
                Crearnomina.objects.create(
                    nombrenomina=generar_nombre_nomina(tipo_nomina_text, fechainicial),
                    fechainicial=fechainicial,
                    fechafinal=fechafinal,
                    fechapago=form.cleaned_data['fechapago'],
                    tiponomina=tiponomina,
                    mesacumular=mes_acumular,
                    anoacumular=ano_acumular,
                    estadonomina=True, 
                    diasnomina=dias_nomina,  # Usamos el cálculo aquí
                    id_empresa=empresa,
                )

                messages.success(request, "Nómina creada exitosamente.")
                return redirect('payroll:payroll')  # Redirigir a una vista de lista, por ejemplo
            except (Tipodenomina.DoesNotExist, Empresa.DoesNotExist):
                messages.error(request, "Hubo un problema al procesar la información.")

        else:
            error = True
            # Si el formulario no es válido, recopilamos todos los errores y los mostramos en un solo mensaje
            error_message = "Por favor, corrija los siguientes errores:"
            for field in form:
                for error in field.errors:
                    error_message += f"\n- {error}"

            messages.error(request, error_message)
    
    return render(request, './payroll/payroll.html', {'nominas': nominas, 'form': form, 'error': error})
    
    
    
    


@login_required
@role_required('accountant')
def payrollview(request, id):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    empleados = Contratos.objects\
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede') \
        .order_by('idempleado__papellido') \
        .filter(estadocontrato=1, id_empresa=idempresa) \
        .values(
            'idempleado__docidentidad', 'idempleado__papellido', 'idempleado__pnombre',
            'idempleado__snombre', 'salario', 'idempleado__idempleado', 'idempleado__sapellido', 'idcontrato'
        )
    


    nombre = Crearnomina.objects.get(idnomina=id)
    # Inicializamos 'nomina' para cuando no se filtra
    nomina = Nomina.objects.filter(idnomina_id=id).order_by('idregistronom')
    

    return render(request, './payroll/payrollviews.html', {
        'nomina': nomina,
        'nombre':nombre,
        'empleados': empleados,
        'id': id
    })


class PayrollAPI2(View):
    def get(self, request, *args, **kwargs):
        usuario = request.session.get('usuario', {})
        idempresa = usuario['idempresa']
        try:
            # Obtener los datos de la base de datos
            conceptos_data = Conceptosdenomina.objects.filter(id_empresa_id = idempresa).values('idconcepto','nombreconcepto','multiplicadorconcepto','formula','codigo').order_by('nombreconcepto') # Convertir el QuerySet a un formato serializable
            conceptos_list = list(conceptos_data)  # Convertir el QuerySet a una lista de diccionarios
            
            # Construir la respuesta JSON
            data = {
                "conceptos": conceptos_list,
            }
            return JsonResponse(data, safe=False)

        except Conceptosdenomina.DoesNotExist:
            return JsonResponse({"error": "No se encontraron conceptos de nómina"}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Error interno: {str(e)}"}, status=500)


class PayrollAPI(View):
    def get(self, request, *args, **kwargs):
        # Obtener los parámetros de la URL
        nomina_id = request.GET.get('nomina_id')
        empleado_id = request.GET.get('empleado_id')

        if not nomina_id or not empleado_id:
            return JsonResponse({"error": "Faltan parámetros: nomina_id o empleado_id"}, status=400)

        try:
            # Optimizar consultas con select_related
            conceptos = Nomina.objects.filter(
                idnomina__idnomina=nomina_id,
                idcontrato__idcontrato=empleado_id
            ).select_related('idcontrato')

            # Verificar si hay conceptos encontrados
            if not conceptos.exists():
                return JsonResponse({"error": "No se encontraron conceptos para este empleado y nómina"}, status=404)

            # Optimizar consulta del contrato
            contrato = Contratos.objects.select_related('idempleado').get(idcontrato=empleado_id)

            # Estructurar los datos para la respuesta
            conceptos_data = [
                {   
                    "codigo": concepto.idregistronom ,
                    "id": concepto.idconcepto.idconcepto,
                    "amount": concepto.cantidad,
                    "value": concepto.valor ,
                    "bloquearAmount": "true" if concepto.idconcepto.formula == '2' else "false" if not concepto.idconcepto.formula else "undefined",
                    "bloquearValue": "true" if concepto.idconcepto.formula == '1' else "false" if not concepto.idconcepto.formula else "undefined",
                }
                for concepto in conceptos
            ]

            # Construir el nombre completo
            empleado = contrato.idempleado
            nombre_completo = " ".join(filter(None, [empleado.papellido, empleado.sapellido, empleado.pnombre, empleado.snombre]))

            # Respuesta estructurada
            data = {
                
                "nombre": nombre_completo,
                "salario": f"{format_value(contrato.salario)} $",
                "conceptos": conceptos_data,
            }
            return JsonResponse(data)

        except Contratos.DoesNotExist:
            return JsonResponse({"error": "El contrato no existe"}, status=404)
        except Nomina.DoesNotExist:
            return JsonResponse({"error": "No se encontraron datos de nómina"}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Error interno: {str(e)}"}, status=500)
    
        
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        try:
            # Filtrar solo las claves que contienen 'new' y agruparlas por fila
            registros_creados = []
            rows_to_create = {}
            cont = 0
            data = json.loads(request.body.decode('utf-8'))  # Decodifica el JSON
            submit_direct = data.get('submit_direct')
            # Verificar si 'submit_direct' está presente
            if not submit_direct:
                raise ValueError("Falta el campo 'submit_direct'.")
            
            # Usamos el método split para dividir la cadena en dos partes
            partes = submit_direct.split('-')

            # Verificar si 'submit_direct' tiene el formato esperado
            if len(partes) != 2:
                raise ValueError("El formato de 'submit_direct' no es válido. Se espera 'nomina-idcontrato'.")

            nomina = partes[0]  # "900"
            idcontrato = partes[1]  # "16"

            ## Actualizar
            for key, value in data.items():
                if 'old' in key:
                    # Obtener el row_id de la clave
                    parts = key.split('-')
                    
                    # Verificar si la clave tiene el formato esperado
                    if len(parts) < 3:
                        raise ValueError(f"Clave con formato inesperado: {key}. No tiene suficientes partes.")
                    
                    row_id = parts[1]  # '148574' -> '148574'

                    # Agrupar datos por fila
                    if row_id not in rows_to_create:
                        rows_to_create[row_id] = {}

                    field_name = '-'.join(parts[2:])  # 'concept-old', 'amount-old', etc.
                    rows_to_create[row_id][field_name] = value
                    
            # Actualizar los registros
            for row_id, fields in rows_to_create.items():
                # Asegurarse de que tengamos todos los datos necesarios para esa fila
                concepto = fields.get('concept-old')
                amount = fields.get('amount-old')
                value = fields.get('value-old')
                
                if not concepto or not amount or not value:
                    raise ValueError(f"Faltan datos requeridos en la fila {row_id}: concepto, cantidad o valor.")
                
                try:
                    # Obtener el concepto por ID
                    concepto_obj = Nomina.objects.get(idregistronom=row_id)
                    concepto_obj.idconcepto_id = concepto  # Asigna el ID del concepto (no el objeto completo)
                    concepto_obj.cantidad = amount
                    concepto_obj.valor = value
                    
                    concepto_obj.save()
                except Nomina.DoesNotExist:
                    raise ValueError(f"No se encontró el concepto con ID {row_id}.")
            
            rows_to_create = {}

            ## Crear Nuevos Registros
            for key, value in data.items():
                if 'new' in key:
                    # Obtener el row_id de la clave
                    parts = key.split('-')
                    
                    # Verificar si la clave tiene el formato esperado
                    if len(parts) < 3:
                        raise ValueError(f"Clave con formato inesperado: {key}. No tiene suficientes partes.")
                    
                    row_id = parts[1]  # 'row-2-concept-new' -> '2'

                    # Agrupar datos por fila
                    if row_id not in rows_to_create:
                        rows_to_create[row_id] = {}

                    field_name = '-'.join(parts[2:])  # 'concept-new', 'amount-new', etc.
                    rows_to_create[row_id][field_name] = value
            
            # Crear los registros
            for row_id, fields in rows_to_create.items():
                # Asegurarse de que tengamos todos los datos necesarios para esa fila
                concepto = fields.get('concept-new')
                amount = fields.get('amount-new')
                value = fields.get('value-new')

                if not concepto or not amount or not value:
                    raise ValueError(f"Faltan datos requeridos en la fila {row_id}: concepto, cantidad o valor.")

                # Crear el nuevo registro solo una vez por fila
                registro = Nomina(
                    idconcepto_id=concepto,
                    cantidad=amount,
                    valor=value,
                    idcontrato_id=idcontrato,
                    idnomina_id=nomina,
                )
                registro.save()
            
            return JsonResponse({'success': True, 'message': 'Los conceptos fueron agregados o actualizados exitosamente.'})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Error al decodificar el JSON. Verifique el formato."}, status=400)
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            return JsonResponse({"error": f"Error inesperado: {str(e)}"}, status=500)

