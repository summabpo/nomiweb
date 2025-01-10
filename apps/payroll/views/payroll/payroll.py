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

# @login_required
# @role_required('employee')
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
    })

    
class PayrollAPI2(View):
    def get(self, request, *args, **kwargs):
        ## el get es para obtener datos de 
        try:
            empresa_id = request.GET.get('empresa_id')
            
            conceptos_data = Conceptosdenomina.objects.filter(id_empresa_id = empresa_id ) 
            data = {
                    "empresa_id": empresa_id,
                    "conceptos": conceptos_data,
                }
            
            return JsonResponse(data)

        except Contratos.DoesNotExist:
            return JsonResponse({"error": "El contrato no existe"}, status=404)
        except Nomina.DoesNotExist:
            return JsonResponse({"error": "No se encontraron datos de nómina"}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Error interno: {str(e)}"}, status=500)

class PayrollAPI(View):
    def get(self, request, *args, **kwargs):
        # Obtener los parámetros de la URL
        print('llege aqui')
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
                    "id": concepto.idregistronom,
                    "empleado": concepto.cantidad,
                    "monto": concepto.valor
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
            print(empleado_id)
            return JsonResponse(data)

        except Contratos.DoesNotExist:
            return JsonResponse({"error": "El contrato no existe"}, status=404)
        except Nomina.DoesNotExist:
            return JsonResponse({"error": "No se encontraron datos de nómina"}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Error interno: {str(e)}"}, status=500)
    
        
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        print('llege' )
        try:
            print('veamos si el body llega')
            print('-------------------')
            print(request.body)
            print('-------------------')
            print('veamos si el json llega')

            # Aquí, en lugar de json.loads, puedes usar request.POST para obtener los datos del formulario
            data = request.POST
            print('-------------------')
            print(data)
            print('-------------------')

            # Aquí puedes realizar acciones con los datos recibidos
            # Ejemplo:
            # empleado_id = data.get('empleado_id')
            # nomina_id = data.get('nomina_id')
            # # Validar y procesar los datos...

            return JsonResponse({"success": True, "message": "Datos procesados exitosamente,","data":data}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Cuerpo de solicitud inválido"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
