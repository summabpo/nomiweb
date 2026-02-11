from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Crearnomina , Tipodenomina , EditHistory , Conceptosfijos , Salariominimoanual,Conceptosdenomina , Empresa , Anos , Nomina , Contratos
from apps.payroll.forms.PayrollForm import PayrollForm
from apps.payroll.forms.updateForm import UpdateForm
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
from django.shortcuts import get_object_or_404
import random
from django.http import HttpResponse
from decimal import Decimal
from django.views.decorators.http import require_GET
import json
from django.http import QueryDict
from django.urls import reverse
from decimal import Decimal, ROUND_HALF_UP


def get_empleado_name(empleado):
    papellido = empleado.get('idempleado__papellido', '') if empleado.get('idempleado__papellido') is not None else ""
    sapellido = empleado.get('idempleado__sapellido', '') if empleado.get('idempleado__sapellido') is not None else ""
    pnombre = empleado.get('idempleado__pnombre', '') if empleado.get('idempleado__pnombre') is not None else ""
    snombre = empleado.get('idempleado__snombre', '') if empleado.get('idempleado__snombre') is not None else ""
    return f"{papellido} {sapellido} {pnombre} {snombre}"


@login_required
@role_required('accountant')
def payroll(request):
    """
    Vista que permite listar las nóminas existentes y crear nuevas.

    Cuando se envía el formulario, se validan los datos ingresados y se calcula la cantidad de días
    de nómina según el tipo (mensual, quincenal u otro). También se determina automáticamente el mes
    y año a acumular. Si la creación es exitosa, se guarda un nuevo registro en el modelo `Crearnomina`.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP del usuario, puede ser GET para mostrar el formulario o POST para procesarlo.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla 'payroll/payroll.html' con el formulario, la lista de nóminas activas
        y mensajes de éxito o error.

    See Also
    --------
    PayrollForm : Formulario utilizado para registrar una nueva nómina.
    Crearnomina : Modelo que representa una nómina registrada.
    Tipodenomina : Define el tipo de nómina (mensual, quincenal, etc.).
    Anos : Representa el año fiscal vinculado a la nómina.
    generar_nombre_nomina : Función auxiliar para construir el nombre único de la nómina.
    """

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

                # Calcular días de nómina, asegurando que nunca sea mayor a 30
                if tiponomina.tipodenomina == 'Mensual':
                    dias_nomina = min(30, (fechafinal - fechainicial).days + 1)
                    
                elif tiponomina.tipodenomina == 'Quincenal':
                    dias_nomina = max(15, (fechafinal - fechainicial).days + 1)
                else:
                    dias_nomina = (fechafinal - fechainicial).days + 1  # Incluir día inicial
                
                


                mes_numero = fechainicial.month  # Obtener el número del mes (1-12)
                mes_acumular = MES_CHOICES[mes_numero][0] if mes_numero else ''
                
                ano_acumular = Anos.objects.get(ano=fechainicial.year)  # Año de la fecha
                
                tipo_nomina_text = tiponomina.tipodenomina 

                empresa = Empresa.objects.get(idempresa=idempresa)

                # Crear instancia de Crearnomina
                
                print('-----------------')
                print(form.cleaned_data['nombrenomina'])
                print(fechainicial)
                print(fechafinal)
                print(form.cleaned_data['fechapago'])
                print(tiponomina)
                print(mes_acumular)
                print(ano_acumular)
                print(dias_nomina)
                print(empresa)
                print('-----------------')


                # Crearnomina.objects.create(
                #     nombrenomina=generar_nombre_nomina(form.cleaned_data['nombrenomina'] , idempresa),
                #     fechainicial=fechainicial,
                #     fechafinal=fechafinal,
                #     fechapago=form.cleaned_data['fechapago'],
                #     tiponomina=tiponomina,
                #     mesacumular=mes_acumular,
                #     anoacumular=ano_acumular,
                #     estadonomina=True, 
                #     diasnomina=dias_nomina,  #Usamos el cálculo aquí
                #     id_empresa=empresa,
                # )
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
def payroll_create_add(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = PayrollForm()
    
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

                # Calcular días de nómina, asegurando que nunca sea mayor a 30
                if tiponomina.tipodenomina == 'Mensual':
                    dias_nomina = min(30, (fechafinal - fechainicial).days + 1)
                    
                elif tiponomina.tipodenomina == 'Quincenal':
                    dias_nomina = max(15, (fechafinal - fechainicial).days + 1)
                else:
                    dias_nomina = (fechafinal - fechainicial).days + 1  # Incluir día inicial
                
                mes_numero = fechainicial.month  # Obtener el número del mes (1-12)
                mes_acumular = MES_CHOICES[mes_numero][0] if mes_numero else ''
                
                ano_acumular = Anos.objects.get(ano=fechainicial.year)  # Año de la fecha
                
                empresa = Empresa.objects.get(idempresa=idempresa)

                # Crear instancia de Crearnomina
                name = generar_nombre_nomina(form.cleaned_data['nombrenomina'] , idempresa)
                
                print('-----------------')
                print(form.cleaned_data['nombrenomina'])
                print(fechainicial)
                print(fechafinal)
                print(form.cleaned_data['fechapago'])
                print(tiponomina)
                print(mes_acumular)
                print(ano_acumular)
                print(dias_nomina)
                print(empresa)
                print('-----------------')


                # Crearnomina.objects.create(
                #     nombrenomina=generar_nombre_nomina(form.cleaned_data['nombrenomina'] , idempresa),
                #     fechainicial=fechainicial,
                #     fechafinal=fechafinal,
                #     fechapago=form.cleaned_data['fechapago'],
                #     tiponomina=tiponomina,
                #     mesacumular=mes_acumular,
                #     anoacumular=ano_acumular,
                #     estadonomina=True, 
                #     diasnomina=dias_nomina,  #Usamos el cálculo aquí
                #     id_empresa=empresa,
                # )
                
                
                response = HttpResponse()
                response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
                response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
                response['X-Up-message'] = 'Familia guardada exitosamente'    
                response['X-Up-Location'] = reverse('payroll:payroll')           
                return response
                
            except (Tipodenomina.DoesNotExist, Empresa.DoesNotExist):
                response = HttpResponse()
                response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
                response['X-Up-icon'] = 'error'  # URL para recargar la página principal   
                response['X-Up-message'] = 'Hubo un problema al procesar la información.'    
                response['X-Up-Location'] = reverse('payroll:payroll')           
                return response
                #messages.error(request, "Hubo un problema al procesar la información.")
                
        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")    
            
            
    return render(request, './payroll/partials/payroll_create.html', {'form': form})



@login_required
@role_required('accountant')
def payroll_closet(request,id):
    if request.method == 'POST':
        nomina = Crearnomina.objects.get(idnomina = id)
        novedades = Nomina.objects.filter(idnomina_id = id )
        nomina.estadonomina = False
        for data in novedades:
            data.estadonomina = 2 
            data.save()
        nomina.save()
        
        # 2750
        response = HttpResponse()
        response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
        response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
        response['X-Up-Message'] = 'Nómina cerrada exitosamente'  
        response['X-Up-Location'] = reverse('payroll:payroll')           
        return response
    
    return render(request, './payroll/partials/payroll_closet.html',{'id':id})

@login_required
@role_required('accountant')
def payrollview(request, id):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    empleados_raw = Nomina.objects \
        .select_related('idcontrato') \
        .filter(idnomina=id, estadonomina=1) \
        .values(
            'idcontrato__idempleado__docidentidad',
            'idcontrato__idempleado__papellido',
            'idcontrato__idempleado__sapellido',
            'idcontrato__idempleado__pnombre',
            'idcontrato__idempleado__snombre',
            'idcontrato__salario',
            'idcontrato__idempleado__idempleado',
            'idcontrato'
        ) \
        .order_by('idcontrato__idempleado__papellido') \
        .distinct()

    # Limpieza de datos (quita "no data", None, vacíos y espacios extra)
    empleados = []
    for e in empleados_raw:
        doc = e.get('idcontrato__idempleado__docidentidad')
        if not doc or str(doc).strip().lower() == "no data":
            doc = ""

        nombres = [
            e.get('idcontrato__idempleado__pnombre'),
            e.get('idcontrato__idempleado__snombre'),
            e.get('idcontrato__idempleado__papellido'),
            e.get('idcontrato__idempleado__sapellido'),
        ]
        full_name = " ".join([
            n.strip() for n in nombres
            if n and n.strip().lower() != "no data"
        ])

        empleados.append({
            'documento': doc,
            'nombre_completo': full_name,
            'salario': e.get('idcontrato__salario'),
            'idempleado': e.get('idcontrato__idempleado__idempleado'),
            'idcontrato': e.get('idcontrato'),
        })

    nombre = Crearnomina.objects.get(idnomina=id)

    nomina = Nomina.objects.filter(idnomina_id=id, estadonomina=1).order_by('idregistronom')

    return render(request, './payroll/payrollviews.html', {
        'nomina': nomina,
        'nombre': nombre,
        'empleados': empleados,
        'id': id
    })


@login_required
@role_required('accountant')
def payroll_modal(request,id,idnomina):
    """
    Vista que muestra los detalles generales de una nómina específica.

    Obtiene la lista de empleados vinculados a la nómina y los muestra junto con la información
    de la nómina seleccionada.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP estándar.
    id : int
        Identificador de la nómina.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla 'payroll/payrollviews.html' con la nómina, los empleados asociados
        y su información básica.

    See Also
    --------
    Crearnomina : Modelo que contiene los datos generales de una nómina.
    Nomina : Contiene los conceptos asignados por empleado y nómina.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    ingreso = 0
    egreso = 0
    conceptos_data = []
    
    contrato = Contratos.objects.select_related('idempleado').get(idcontrato=id)

    conceptos = Nomina.objects.filter(
        idnomina__idnomina=idnomina,
        idcontrato__idcontrato=id,
        estadonomina=1
    ).select_related('idcontrato').order_by('idconcepto__codigo')
    
    if not conceptos.exists():
        conceptos = []

    for concepto in conceptos:
        concepto_info = {
            'idn': concepto.idregistronom,
            "id": concepto.idconcepto.idconcepto,
            "amount": concepto.cantidad,
            "value": concepto.valor,
        }
        conceptos_data.append(concepto_info)
        
        if concepto.valor > 0:
            ingreso += concepto.valor
        elif concepto.valor < 0:
            egreso += concepto.valor 

    # 🔹 Construcción limpia del nombre completo sin "no data", None ni vacíos
    empleado = contrato.idempleado
    partes_nombre = [
        empleado.papellido,
        empleado.sapellido,
        empleado.pnombre,
        empleado.snombre
    ]
    nombre_completo = " ".join([
        p.strip() for p in partes_nombre
        if p and p.strip().lower() != "no data"
    ])

    total = ingreso + egreso
        
    data = {
        "idnomina": idnomina,
        "idempleado": id,
        "nombre": nombre_completo,
        "cargo": contrato.cargo,
        "salario": f"{format_value(contrato.salario)}$",
        "ingresos": f"{format_value(ingreso)}$",
        "egresos": f"{format_value(egreso)}$",
        "total": f"{format_value(total)}$",
        "id": id,
        "conceptos": conceptos_data,
        "conceptors": [
            (item.idconcepto, f"{item.codigo} - {item.nombreconcepto}")
            for item in Conceptosdenomina.objects.filter(id_empresa_id=idempresa).order_by('codigo')
        ]
    }
    
    return render(request, './payroll/partials/payrollmodal2.html', {'data': data})



@login_required
@role_required('accountant')
def payroll_create(request):
    """
    Vista que permite registrar un nuevo concepto en la nómina de un empleado.

    Procesa los datos enviados por POST, calcula el valor del concepto si aplica una fórmula
    asociada y actualiza la lista de conceptos asignados al empleado en la nómina. También calcula
    totales de ingresos, egresos y el valor neto.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP que contiene los datos del formulario.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla 'payroll/partials/concepts_list.html' con la lista actualizada de
        conceptos del empleado y los totales asociados.

    See Also
    --------
    Nomina : Modelo donde se registran los conceptos por contrato y nómina.
    Conceptosdenomina : Contiene la configuración de cada concepto, incluidas fórmulas y multiplicadores.
    Contratos : Proporciona información contractual necesaria para cálculos.
    Salariominimoanual : Se usa en el cálculo de auxilio de transporte u otros conceptos relacionados.
    """

    ingreso = 0
    egreso = 0
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    conceptos_data = []

    if request.method == 'POST':
        # Procesar los datos del formulario
        mi_select = request.POST.get('concept')
        cantidad = request.POST.get('cantidad')
        valor = request.POST.get('valor')
        idnomina = request.POST.get('idnomina')
        id = request.POST.get('idempleado')
        
        conceptfi = Conceptosfijos.objects.get(idfijo=23)
        nomina = Crearnomina.objects.get(idnomina=idnomina)
        concept1 = Conceptosdenomina.objects.get(idconcepto=mi_select)
        formula = str(concept1.formula).strip() in ['0', '1', '2']

        if formula:
            if concept1.formula == '1':
                if concept1.codigo == 2:

                    aux = Salariominimoanual.objects.get(
                        ano=nomina.anoacumular.ano
                    ).auxtransporte

                    multiplier = Decimal(aux) / Decimal('30')

                else:
                    salario = Contratos.objects.get(idcontrato=id).salario
                    multiplier = Decimal(salario) / Decimal('30')

                valor = (
                    Decimal(cantidad) *
                    multiplier *
                    Decimal(concept1.multiplicadorconcepto)
                ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

            elif concept1.formula == '2':
                salario = Contratos.objects.get(idcontrato=id).salario

                multiplier = (
                    Decimal(salario) /
                    Decimal(conceptfi.valorfijo)
                )

                valor = (
                    Decimal(cantidad) *
                    multiplier *
                    Decimal(concept1.multiplicadorconcepto)
                ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

            else:
                cantidad = Decimal('0')
                valor = Decimal(valor.replace(',', '')).quantize(
                    Decimal('1'), rounding=ROUND_HALF_UP
                )

        else:
            cantidad = Decimal('0')
            valor = Decimal(valor.replace(',', '')).quantize(
                Decimal('1'), rounding=ROUND_HALF_UP
            )

        # 🔹 Limpieza del nombre del empleado (sin "no data", None, ni vacíos)
        contrato = Contratos.objects.select_related('idempleado').get(idcontrato=id)
        empleado = contrato.idempleado
        partes_nombre = [
            empleado.papellido,
            empleado.sapellido,
            empleado.pnombre,
            empleado.snombre
        ]
        nombre_completo = " ".join([
            p.strip() for p in partes_nombre
            if p and p.strip().lower() != "no data"
        ])

        # Crear registro de nómina
        Nomina.objects.create(
            idconcepto_id=mi_select,
            cantidad=cantidad,
            valor=valor,
            estadonomina=1,
            idcontrato_id=id,
            idnomina_id=idnomina,
        )
        
        # Obtener conceptos asociados a la nómina del empleado
        conceptos = Nomina.objects.filter(
            idnomina__idnomina=idnomina,
            idcontrato__idcontrato=id,
            estadonomina=1
        ).select_related('idcontrato').order_by('idconcepto__codigo')
            
        for concepto in conceptos:
            concepto_info = {
                'idn': concepto.idregistronom,
                "id": concepto.idconcepto.idconcepto,
                "amount": concepto.cantidad,
                "value": concepto.valor,
            }
            conceptos_data.append(concepto_info)
            
            if concepto.valor > 0:
                ingreso += concepto.valor
            elif concepto.valor < 0:
                egreso += concepto.valor 

    total = ingreso + egreso
    
    data = {    
        "nombre_empleado": nombre_completo,  # ✅ Nombre limpio
        "salario": f"{format_value(contrato.salario)}$",
        "ingresos": f"{format_value(ingreso)}$",
        "egresos": f"{format_value(egreso)}$",
        "total": f"{format_value(total)}$",
        "conceptos": conceptos_data,
        "value": True,
        "conceptors": [
            (item.idconcepto, f"{item.codigo} - {item.nombreconcepto}")
            for item in Conceptosdenomina.objects.filter(id_empresa_id=idempresa).order_by('codigo')
        ]
    }

    return render(request, './payroll/partials/concepts_list.html', {'data': data})



@login_required
@role_required('accountant')
def payroll_edit(request):
    
    """
    Edita los valores de cantidad y valor de un concepto de nómina individual.

    Esta vista permite a los usuarios con rol 'accountant' actualizar los valores de 
    un concepto de nómina específico. Si se detectan cambios respecto a los valores 
    previos, se registra la modificación en el historial de ediciones.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP de tipo POST que debe contener los campos:
        - idn: ID del concepto de nómina a editar.
        - amount: Nueva cantidad (con punto o coma como separador decimal).
        - value: Nuevo valor numérico (con o sin separador de miles).

    Returns
    -------
    JsonResponse
        - {'mensaje': 'Concepto actualizado correctamente'} si la operación fue exitosa.
        - {'error': 'Método no permitido'} si se accede por otro método.
        - Mensaje de error personalizado si no se encuentra el concepto.

    See Also
    --------
    Nomina : Modelo que almacena los conceptos de nómina por contrato.
    EditHistory : Modelo que registra los cambios aplicados a conceptos de nómina.

    Notes
    -----
    - El campo 'amount' puede incluir comas como separador decimal, las cuales se convierten.
    - Se registra el cambio solo si hay diferencia entre el valor anterior y el nuevo.
    - Las modificaciones se auditan por campo y se guardan con información del usuario y empresa.
    """
    
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    
    if request.method == 'POST':
        data = request.POST
        idn = data.get('idn')
        amount = data.get('amount').replace(',', '.')  # Reemplazamos la coma por un punto
        value = data.get('value').replace(',', '') 

        try:
            value_decimal = Decimal(value)
            # Obtener el concepto por ID
            concepto_obj = Nomina.objects.get(idregistronom=idn)
            
            ## anteriores =  
            before_amount = concepto_obj.cantidad
            before_value = concepto_obj.valor
            
            
            concepto_obj.cantidad = amount
            concepto_obj.valor = value_decimal
            concepto_obj.save()
            
            
            
            
            if amount != before_amount  and value_decimal == before_value : 
                EditHistory.objects.create(
                    modified_model = "Nomina"  , #Nombre del modelo modificado
                    modified_object_id = concepto_obj.idregistronom , #ID del objeto modificado
                    user_id = usuario['id']  , #Usuario que hizo la modificación
                    operation_type = "update" , #Tipo de operación
                    field_name = "cantidad" , #Campo modificado
                    old_value = before_amount ,  #Valor anterior (si aplica)
                    new_value = amount ,  #Valor nuevo (si aplica)
                    description =  "Modificacion de Cantidad de valor de concepto de Nomina" , #Descripción de la modificación 
                    id_empresa_id  = idempresa #Empresa a la que pertenece la modificación
                )
            
            
            elif value_decimal != before_value  and amount == before_amount :
                EditHistory.objects.create(
                    modified_model = "Nomina"  , #Nombre del modelo modificado
                    modified_object_id = concepto_obj.idregistronom , #ID del objeto modificado
                    user_id = usuario['id']  , #Usuario que hizo la modificación
                    operation_type = "update" , #Tipo de operación
                    field_name = "valor" , #Campo modificado
                    old_value = before_value  ,  #Valor anterior (si aplica)
                    new_value = value_decimal  ,  #Valor nuevo (si aplica)
                    description =  "Modificacion de valor concepto de Nomina" , #Descripción de la modificación 
                    id_empresa_id  = idempresa, #Empresa a la que pertenece la modificación
                )
                
            elif value_decimal != before_value and amount != before_amount :
                EditHistory.objects.create(
                    modified_model = "Nomina"  , #Nombre del modelo modificado
                    modified_object_id = concepto_obj.idregistronom , #ID del objeto modificado
                    user_id = usuario['id']  , #Usuario que hizo la modificación
                    operation_type = "update" , #Tipo de operación
                    field_name = "cantidad y valor" , #Campo modificado
                    old_value = f"{before_amount} - {before_value}" ,  #Valor anterior (si aplica)
                    new_value = f"{amount} - {value_decimal}"  ,  #Valor nuevo (si aplica)
                    description =  "Modificacion de Cantidad y valor de concepto de Nomina" , #Descripción de la modificación 
                    id_empresa_id  = idempresa, #Empresa a la que pertenece la modificación
                )
                
        except Nomina.DoesNotExist: 
            return JsonResponse(f"No se encontró el concepto con ID {idn}.")
            
        return JsonResponse({'mensaje': 'Concepto actualizado correctamente'})
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
@role_required('accountant')
def payroll_delete(request):
    
    """
    Elimina un concepto de nómina específico y actualiza el resumen de ingresos y egresos del contrato asociado.

    Esta vista permite a los usuarios con rol 'accountant' eliminar un concepto de nómina individual a través 
    de una solicitud POST. Luego de eliminar el concepto, recalcula los ingresos, egresos y total del contrato 
    relacionado, retornando además una lista actualizada de los conceptos restantes.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP de tipo POST que debe incluir en el cuerpo (`body`) el ID del concepto a eliminar (`idn`).

    Returns
    -------
    JsonResponse
        - 'message': Mensaje de confirmación.
        - 'data': Diccionario que contiene:
            - 'salario': Salario base del contrato en formato de moneda.
            - 'ingresos': Suma de los conceptos positivos.
            - 'egresos': Suma de los conceptos negativos.
            - 'total': Resultado neto (ingresos + egresos).
            - 'conceptos': Lista de conceptos de nómina restantes.
            - 'value': Valor booleano de control (siempre True).
            - 'conceptors': Lista de conceptos de nómina disponibles para la empresa.

    See Also
    --------
    Nomina : Modelo que almacena los conceptos de nómina por contrato.
    Conceptosdenomina : Modelo que representa los conceptos disponibles por empresa.

    Notes
    -----
    - El valor eliminado no se resta directamente, sino que se recalculan los totales en base a los conceptos restantes.
    - La vista formatea los valores monetarios para mejorar su legibilidad en la interfaz.
    - El contrato y la nómina asociados se determinan a partir del concepto recibido.
    """
    
    ingreso = 0  # Inicializamos la variable ingreso
    egreso = 0   # Inicializamos la variable egreso
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    conceptos_data = []

    if request.method == 'POST':
        
        body = QueryDict(request.body.decode('utf-8'))  # Parseamos el body
        idn = body.get('idn')
        #concepto = get_object_or_404(Nomina, idregistronom=idn)
        concepto = Nomina.objects.get(idregistronom=idn)
        
        conceptos = Nomina.objects.filter(
                    idnomina__idnomina=concepto.idnomina.idnomina,
                    idcontrato__idcontrato=concepto.idcontrato.idcontrato,
                    estadonomina = 1 
                ).select_related('idcontrato').order_by('idconcepto__codigo')
        
        for concepto1 in conceptos:
            # Crear el diccionario con los datos del concepto
            concepto_info = {
                'idn': concepto1.idregistronom,
                "id": concepto1.idconcepto.idconcepto,
                "amount": concepto1.cantidad,
                "value": concepto1.valor,
            }
            
            # Agregar el concepto al arreglo
            conceptos_data.append(concepto_info)
            
            # Revisar si el valor es mayor que 0 (ingreso) o negativo (egreso)
            if concepto.valor > 0:
                ingreso += concepto.valor  # Agregar a ingreso si es positivo
            elif concepto.valor < 0:
                egreso += concepto.valor 
        
        total = ingreso + egreso
        salario = concepto.idcontrato.salario 
        concepto.delete()
    
        
    
    data = {    
        "salario": f"{format_value(salario)}$",
        "ingresos": f"{format_value(ingreso)}$",
        "egresos": f"{format_value(egreso)}$",
        "total": f"{format_value(total)}$",
        "conceptos": conceptos_data,
        "value": True,
        "conceptors": [(item.idconcepto, f"{item.codigo} - {item.nombreconcepto}") for item in Conceptosdenomina.objects.filter(id_empresa_id=idempresa).order_by('codigo') ]
    }


    return JsonResponse({'message': 'Datos recibidos correctamente', 'data': data})











@login_required
@role_required('accountant')
def payroll_general(request, idnomina):
    
    """
    Renderiza la vista general de contratos activos para una nómina específica.

    Esta vista permite a los usuarios con rol 'accountant' visualizar los contratos activos asociados a la empresa,
    proporcionando los datos básicos de los empleados, incluyendo nombre completo, cargo y documento de identidad. 
    Se utiliza como punto de partida para la asignación o consulta de conceptos de nómina por contrato.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP que contiene la sesión activa del usuario autenticado.
    
    idnomina : int
        Identificador de la nómina con la que se relacionan los contratos que se mostrarán.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla `'./payroll/partials/payroll_general.html'` con un diccionario que incluye:
            - 'contratos_empleados': Lista de contratos activos con datos del empleado.
            - 'idnomina': Identificador de la nómina proporcionado como parámetro.

    See Also
    --------
    Contratos : Modelo que representa los contratos laborales activos.
    get_empleado_name : Función auxiliar que construye el nombre completo de un empleado.

    Notes
    -----
    - Solo se incluyen contratos con estado activo (`estadocontrato=1`).
    - Se utiliza `select_related` para optimizar las consultas relacionadas con empleados, sedes, cargos y tipos de contrato.
    - El nombre completo de cada empleado se construye dinámicamente para facilitar la presentación en la vista HTML.
    """
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    # Consulta de contratos activos
    contratos_empleados = list(
        Contratos.objects
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede')
        .filter(estadocontrato=1, id_empresa_id=idempresa)
        .values(
            'idempleado__docidentidad',
            'idempleado__papellido',
            'idempleado__sapellido',
            'idempleado__pnombre',
            'idempleado__snombre',
            'cargo__nombrecargo',
            'idcontrato'
        )
    )

    # Crear nombre completo y eliminar “no data”
    for empleado in contratos_empleados:
        nombres = [
            (empleado.get('idempleado__pnombre') or '').replace('no data', '').strip(),
            (empleado.get('idempleado__snombre') or '').replace('no data', '').strip(),
            (empleado.get('idempleado__papellido') or '').replace('no data', '').strip(),
            (empleado.get('idempleado__sapellido') or '').replace('no data', '').strip(),
        ]
        # Une solo los nombres válidos
        empleado['nombre_completo'] = ' '.join(n for n in nombres if n)

    dato = {
        'contratos_empleados': contratos_empleados,
        'idnomina': idnomina
    }

    return render(request, './payroll/partials/payroll_general.html', {'dato': dato})


@login_required
@role_required('accountant')
def payroll_general_data(request,idnomina):
    
    """
    Procesa y muestra los conceptos de nómina asignados a un contrato específico dentro de una nómina.

    Esta vista permite a los usuarios con rol 'accountant' consultar los conceptos de nómina asociados a un contrato 
    específico dentro de una nómina ya existente. Calcula ingresos, egresos y el total, y prepara los datos para 
    renderizar la interfaz parcial con los detalles del contrato y sus conceptos.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene la información del usuario autenticado y el contrato seleccionado.

    idnomina : int
        Identificador de la nómina en la que se encuentran los conceptos a consultar.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla `'./payroll/partials/payroll_general_data.html'` con un diccionario que incluye:
            - 'salario': Salario base del contrato.
            - 'ingresos': Total de conceptos positivos.
            - 'egresos': Total de conceptos negativos.
            - 'total': Suma de ingresos y egresos.
            - 'idnomina': ID de la nómina actual.
            - 'id': ID del contrato seleccionado.
            - 'conceptos': Lista detallada de conceptos asignados al contrato.
            - 'conceptors': Lista de conceptos registrados en la empresa para ser seleccionados.
            - 'true': Bandera booleana para indicar si hubo selección de contrato.

    See Also
    --------
    Nomina : Modelo que contiene los conceptos asignados por contrato.
    Contratos : Modelo que representa los contratos activos.
    Conceptosdenomina : Modelo con los conceptos válidos registrados para la empresa.

    Notes
    -----
    - La vista requiere una solicitud POST con el ID de contrato (`contrato_empleado`).
    - Se calcula automáticamente el total de ingresos y egresos del contrato.
    - Utiliza `select_related` para optimizar las consultas relacionadas con conceptos y contratos.
    - El salario se muestra en formato monetario.
    """
    
    ingreso = 0  # Inicializamos la variable ingreso
    egreso = 0   # Inicializamos la variable egreso
    conceptos_data = []
    variable = False
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    if request.method == 'POST':
        idcontrato = request.POST.get('contrato_empleado')
        variable = True
        
        conceptos = Nomina.objects.filter(
            idnomina__idnomina=idnomina,
            idcontrato__idcontrato=idcontrato ,
            estadonomina = 1 
        ).select_related('idcontrato').order_by('idconcepto__codigo')
            
        # Estructurar los datos para la respuesta
        for concepto in conceptos:
            # Crear el diccionario con los datos del concepto
            concepto_info = {
                'idn': concepto.idregistronom,
                "id": concepto.idconcepto.idconcepto,
                "amount": concepto.cantidad,
                "value": concepto.valor,
            }
            
            # Agregar el concepto al arreglo
            conceptos_data.append(concepto_info)
            
            # Revisar si el valor es mayor que 0 (ingreso) o negativo (egreso)
            if concepto.valor > 0:
                ingreso += concepto.valor  # Agregar a ingreso si es positivo
            elif concepto.valor < 0:
                egreso += concepto.valor 
        
        # Optimizar consulta del contrato
        contrato = Contratos.objects.select_related('idempleado').get(idcontrato=idcontrato)
        
    
    total = ingreso + egreso
    
    
    data = {
        'true': variable,
        "salario": f"{format_value(contrato.salario)}$",
        "ingresos": f"{format_value(ingreso)}$",
        "egresos": f"{format_value(egreso)}$",
        "total": f"{format_value(total)}$",
        "idnomina": idnomina,
        "id":idcontrato, 
        "conceptos": conceptos_data,
        "conceptors": [(item.idconcepto, f"{item.codigo} - {item.nombreconcepto}") for item in Conceptosdenomina.objects.filter(id_empresa_id=idempresa).order_by('codigo') ]
    }
    
    return render(request, './payroll/partials/payroll_general_data.html',{'data': data})
    



@login_required
@role_required('accountant')
def payroll_concept_info(request):
    """
    Retorna información detallada sobre un concepto de nómina específico aplicado a un contrato.

    Esta vista, restringida al rol 'accountant', se encarga de calcular el valor estimado de un concepto de nómina 
    utilizando su fórmula y multiplicador, en función del salario del empleado o del auxilio de transporte, 
    dependiendo del tipo de fórmula registrada en la base de datos.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que debe contener los siguientes datos en el cuerpo (formato POST codificado como `application/x-www-form-urlencoded` o `application/json`):
            - concept : int
                ID del concepto de nómina a consultar.
            - idempleado : int
                ID del contrato del empleado al que se le aplicará el concepto.
            - payroll : int
                ID de la nómina a la que pertenece el concepto.

    Returns
    -------
    JsonResponse
        Devuelve un JSON con:
            - 'message': Mensaje de éxito si todo fue correcto.
            - 'concept': ID del concepto solicitado.
            - 'formula': Booleano que indica si el concepto tiene fórmula válida (1 o 2).
            - 'multiplier': Valor numérico calculado con base en la fórmula del concepto.

        En caso de error, devuelve un mensaje apropiado con código HTTP 400 o 405.

    See Also
    --------
    Conceptosdenomina : Modelo con los conceptos de nómina y sus fórmulas.
    Contratos : Modelo que contiene información del salario del contrato activo.
    Salariominimoanual : Modelo con los valores del auxilio de transporte por año.
    Crearnomina : Modelo que representa la nómina mensual o acumulada.
    Conceptosfijos : Modelo que almacena valores fijos referenciales como el divisor estándar.

    Notes
    -----
    - Las fórmulas válidas son: 
        '1' para multiplicar por días y valor base (salario o auxilio),
        '2' para multiplicar por un factor fijo dividido entre salario,
        '0' u otros son considerados como sin fórmula válida.
    - El código `2` representa el auxilio de transporte, y se maneja de manera especial.
    - Si faltan datos requeridos o se usa un método diferente a POST, se devuelve un error.
    """
    
    if request.method == 'POST':
        body = QueryDict(request.body.decode('utf-8'))  # Parseamos el body
        concept = body.get('concept')
        idempleado = body.get('idempleado')
        idnomina = body.get('payroll')

        if not concept or not idempleado:
            return JsonResponse({'error': 'Faltan datos requeridos'}, status=400)
        # Dividir el string por '=' para obtener el valor (esto sirve si solo hay un valor)
        try:
            conceptfi = Conceptosfijos.objects.get(idfijo = 23) 
            nomina = Crearnomina.objects.get(idnomina=idnomina)
            concept1 = Conceptosdenomina.objects.get(idconcepto=concept)
            formula = str(concept1.formula).strip() in ['0', '1', '2']
            if formula:
                if concept1.formula == '1':
                    if concept1.codigo == 2:
                        aux =Salariominimoanual.objects.get(ano = nomina.anoacumular.ano ).auxtransporte
                        multiplier = (aux/30) * float(concept1.multiplicadorconcepto)
                    else :
                        multiplier = Contratos.objects.get(idcontrato=idempleado).salario
                        multiplier = (multiplier/30) * float(concept1.multiplicadorconcepto)
                elif concept1.formula == '2':
                    multiplier = Contratos.objects.get(idcontrato=idempleado).salario
                    salariohoras = (float(multiplier) / float(conceptfi.valorfijo))
                
                    multiplier =  salariohoras * float(concept1.multiplicadorconcepto)
                else:
                    multiplier = 0
            else:
                multiplier = 0
                
        except ValueError:
            concept = None
            formula = False
            multiplier = 0
            
        if not concept:
            return JsonResponse({'error': 'No se seleccionó ningún concepto'}, status=400)
        
        
        return JsonResponse({'message': 'Datos recibidos correctamente', 'concept': concept , 'formula': formula , 'multiplier': multiplier})
    return JsonResponse({'error': 'Método no permitido'}, status=405)



@login_required
@role_required('accountant')
def payroll_calculate(request,id):
    """
    Realiza un cálculo simple asociado a un contrato de nómina.

    Esta vista recibe una cantidad enviada mediante POST y devuelve el doble de dicha cantidad.
    Está restringida a usuarios autenticados con el rol 'accountant'. No realiza validaciones adicionales 
    ni consulta la base de datos más allá del ID del contrato recibido por parámetro.

    Parameters
    ----------
    request : HttpRequest
        La solicitud HTTP que contiene:
            - cantidad : int (en POST)
                Cantidad numérica que se desea multiplicar por 2.
    id : int
        ID del contrato del cual se quiere usar el dato, aunque no se utiliza directamente.

    Returns
    -------
    HttpResponse
        Una respuesta plana con el número calculado (cantidad * 2), o vacía si ocurre un error o no es POST.

    Notes
    -----
    - Esta vista puede usarse para pruebas o cálculos intermedios en el frontend.
    - No retorna HTML ni renderiza plantilla.
    """
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    if request.method == 'POST':
        idcontrato = id         
        try:
            cantidad = int(request.POST.get('cantidad', 0))
            resultado = cantidad * 2  # Por ejemplo, multiplicar por 2
            return HttpResponse(resultado)  # Solo devolvemos el número, nada de HTML
        except ValueError:
            return HttpResponse("")
    return HttpResponse("")



@login_required
@role_required('accountant')
def payroll_info_edit(request):
    """
    Retorna información detallada sobre un concepto aplicado a un registro específico de nómina.

    Esta vista permite obtener la fórmula y el multiplicador de un concepto existente en la base de datos
    vinculado a una línea de nómina. Se calcula el valor base del concepto con base en su tipo de fórmula
    y se devuelve junto con su identificador y estado.

    Parameters
    ----------
    request : HttpRequest
        La solicitud HTTP debe ser de tipo POST y debe contener en el cuerpo:
            - concept : int
                ID del concepto de nómina.
            - idn : int
                ID del registro de nómina (`idregistronom`) al que pertenece el concepto.

    Returns
    -------
    JsonResponse
        Retorna un JSON con:
            - 'message': Confirmación de recepción exitosa.
            - 'concept': ID del concepto solicitado.
            - 'idn': ID del registro de nómina.
            - 'formula': Booleano que indica si tiene fórmula asociada.
            - 'multiplier': Valor calculado según la fórmula del concepto.

        En caso de error o si no es método POST, retorna un mensaje apropiado con código HTTP 400 o 405.

    See Also
    --------
    Nomina : Modelo de registros de nómina.
    Conceptosdenomina : Contiene la fórmula y multiplicador del concepto.
    Salariominimoanual : Usado para obtener el valor del auxilio de transporte.
    Conceptosfijos : Referencia para fórmulas con divisores fijos.
    Crearnomina : Para obtener el año base del cálculo.
    Contratos : Modelo que contiene los salarios para aplicar en la fórmula.

    Notes
    -----
    - Fórmulas posibles:
        '1': Multiplica el salario o auxilio de transporte diario por el multiplicador.
        '2': Usa un valor fijo como divisor para calcular el proporcional.
        '0': No tiene fórmula y devuelve multiplicador 0.
    - Si el concepto tiene código 2, se trata como auxilio de transporte.
    """
    if request.method == 'POST':
        body = QueryDict(request.body.decode('utf-8'))
        concept = body.get('concept')
        idn = body.get('idn') 
        
        concepto_obj = Nomina.objects.get(idregistronom=idn)
        conceptfi = Conceptosfijos.objects.get(idfijo = 23) 
        nomina = Crearnomina.objects.get(idnomina=concepto_obj.idnomina.idnomina)
        concept1 = Conceptosdenomina.objects.get(idconcepto=concept)
        formula = str(concept1.formula).strip() in ['0', '1', '2']
        
        if formula:
            if concept1.formula == '1':
                if concept1.codigo == 2:
                    aux =Salariominimoanual.objects.get(ano = nomina.anoacumular.ano ).auxtransporte
                    multiplier = (aux/30) * float(concept1.multiplicadorconcepto)
                else :
                    multiplier = Contratos.objects.get(idcontrato=concepto_obj.idcontrato.idcontrato).salario
                    multiplier = (multiplier/30) * float(concept1.multiplicadorconcepto)
            elif concept1.formula == '2':
                multiplier = Contratos.objects.get(idcontrato=concepto_obj.idcontrato.idcontrato).salario
                multiplier = (float(multiplier) / float(conceptfi.valorfijo)) * float(concept1.multiplicadorconcepto)
            else:
                multiplier = 0
        else:    
            multiplier = 0
        
        if not concept:
            return JsonResponse({'error': 'No se seleccionó ningún concepto'}, status=400)
        
        return JsonResponse({'message': 'Datos recibidos correctamente', 'concept': concept , 'idn': idn , 'formula': formula , 'multiplier': multiplier})
    return JsonResponse({'error': 'Método no permitido'}, status=405)
        
    

# Nueva vista: crear nómina desde un modal Unpoly
@login_required
@role_required('accountant')
def payroll_create_nomina_modal(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario.get('idempresa')
    form = PayrollForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            try:
                tiponomina_id = form.cleaned_data['tiponomina']
                tiponomina = Tipodenomina.objects.get(idtiponomina=tiponomina_id)

                fechainicial = form.cleaned_data['fechainicial']
                fechafinal = form.cleaned_data['fechafinal']

                if tiponomina.tipodenomina == 'Mensual':
                    dias_nomina = min(30, (fechafinal - fechainicial).days + 1)
                elif tiponomina.tipodenomina == 'Quincenal':
                    dias_nomina = max(15, (fechafinal - fechainicial).days + 1)
                else:
                    dias_nomina = (fechafinal - fechainicial).days + 1

                mes_numero = fechainicial.month
                mes_acumular = MES_CHOICES[mes_numero][0] if mes_numero else ''
                ano_acumular = Anos.objects.get(ano=fechainicial.year)
                empresa = Empresa.objects.get(idempresa=idempresa)

                Crearnomina.objects.create(
                    nombrenomina=generar_nombre_nomina(form.cleaned_data['nombrenomina'], idempresa),
                    fechainicial=fechainicial,
                    fechafinal=fechafinal,
                    fechapago=form.cleaned_data['fechapago'],
                    tiponomina=tiponomina,
                    mesacumular=mes_acumular,
                    anoacumular=ano_acumular,
                    estadonomina=True,
                    diasnomina=dias_nomina,
                    id_empresa=empresa,
                )

                response = HttpResponse()
                response['X-Up-Accept-Layer'] = 'true'
                response['X-Up-Icon'] = 'success'
                response['X-Up-Message'] = 'Nómina creada exitosamente.'
                return response
            except (Tipodenomina.DoesNotExist, Empresa.DoesNotExist, Anos.DoesNotExist):
                pass

    return render(request, './payroll/partials/create_nomina_modal.html', {'form': form})