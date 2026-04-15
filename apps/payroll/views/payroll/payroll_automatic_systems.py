from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Crearnomina , Contratos,NovFijos , EditHistory ,Incapacidades, Conceptosfijos ,Costos,Salariominimoanual, Crearnomina ,EmpVacaciones,Prestamos ,Conceptosdenomina , Empresa , Vacaciones , Nomina , Contratos
from django.contrib import messages
from django.db import transaction, models
from datetime import datetime
from django.db.models import Sum, Q
from types import SimpleNamespace

from apps.payroll.views.payroll.common import MES_CHOICES
from datetime import date, timedelta
from apps.components.humani import format_value
from django.http import JsonResponse
from django.utils import timezone
import calendar
from apps.components.salary import salario_mes
from decimal import Decimal, ROUND_HALF_UP , getcontext , ROUND_CEILING , ROUND_UP
from apps.components.salary_nomina import salary_nomina_update
from apps.companies.views.disabilities.disabilities import disabilities_ibc
from apps.payroll.views.payroll.auto_recalculate import auto_recalculate

#prueba git
@login_required
@role_required('accountant')
def automatic_systems(request, type_payroll=0,idnomina=0):
    """
        Ejecuta procesos automáticos sobre distintos tipos de nómina según el tipo de cálculo seleccionado.

        Esta vista permite al usuario contable ejecutar distintos tipos de procesos automáticos sobre una
        nómina ya creada, como: cálculo básico, incapacidades, aportes o transporte. Además, maneja opciones
        adicionales como comentarios obligatorios para la modificacion del modal en donde se visualiza el procesp y centros de costo.

        Parameters
        ----------
        request : HttpRequest
            Solicitud HTTP de tipo GET o POST que puede contener los siguientes campos en el POST:
            - no-cost-center: Indica si se omite el centro de costo (valor 'on' si está marcado).
            - costos: ID del centro de costo, solo si se requiere usarlo.

        type_payroll : int, opcional
            Define el tipo de proceso a ejecutar:
            - 0: Nómina básica.
            - 1: Incapacidades.
            - 2: Aportes.
            - 3: Transporte.
            - Otro: Error de tipo.

        idnomina : int, opcional
            ID de la nómina sobre la que se aplicará el proceso.

        Returns
        -------
        HttpResponse
            - Renderiza el template 'payroll/partials/payroll_automatic_systems.html' si es una solicitud GET.
            - Redirige a la vista de la nómina con un mensaje de éxito o error si es una solicitud POST.

        See Also
        --------
        Costos : Modelo que representa los centros de costo disponibles por empresa.
        messages : Sistema de mensajes de Django utilizado para notificar el estado del proceso.

        Notes
        -----
        - El título del proceso se adapta dinámicamente al tipo de proceso seleccionado.
        - Las funciones de procesamiento de nómina (`procesar_nomina_basica`, `procesar_nomina_incapacidad`, etc.) 
            se encargan de realizar el cálculo según el tipo seleccionado.
        - La vista maneja redirecciones con mensajes de éxito o error dependiendo de si el proceso fue exitoso o no.
    """
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    titles = {
        0: 'Nómina Básica',
        1: 'Incapacidades',
        2: 'Aportes',
        3: 'Transporte',
        4: 'Reinicio de Nómina',
        5: 'Recalcular de Nómina'
    }

    titulo = titles.get(type_payroll, 'Sistemas Automáticos')
    centros = Costos.objects.filter(id_empresa_id=idempresa)
    empleados = Contratos.objects.filter(estadocontrato=1, id_empresa=idempresa).order_by('idempleado__papellido').values('idcontrato','idempleado__docidentidad','idempleado__papellido','idempleado__pnombre','idempleado__sapellido')
    
    
    
    if request.method == 'POST':
        need_comment = request.POST.get('need_comment', False)  # Devuelve 'on' si está marcado, None si no
        costo = request.POST.get('costos', False)
        empleados_ids = request.POST.getlist('empleados', False)
        # Convertir a enteros
        if empleados_ids :
            empleados_ids = [int(e) for e in empleados_ids if e.isdigit()]

        
        need_comment = need_comment == 'on'
        
        ne = costo if need_comment else 0
                
        if type_payroll == 0:
            if procesar_nomina_basica(idnomina,ne,idempresa,empleados_ids):
                messages.success(request, "Proceso Basico realizado correctamente")
                return redirect('payroll:payrollview', id=idnomina)
            else :
                messages.error(request, "Error al procesar la nómina")
                return redirect('payroll:payrollview', id=idnomina)
            
        
        elif  type_payroll == 1:
            if procesar_nomina_incapacidad(idnomina, ne , idempresa,empleados_ids):
                messages.success(request, "Proceso de Incapacidades realizado correctamente")
                return redirect('payroll:payrollview', id=idnomina)
            else :
                messages.error(request, "Error al realizar procesar la nómina")
                return redirect('payroll:payrollview', id=idnomina)
        
        elif  type_payroll == 2:
            if procesar_nomina_aportes(idnomina, ne , idempresa,empleados_ids):
                messages.success(request, "Proceso de Aportes realizado correctamente")
                return redirect('payroll:payrollview', id=idnomina)
            else :
                messages.error(request, "Error al realizar procesar la nómina")
                return redirect('payroll:payrollview', id=idnomina)
            
        elif  type_payroll == 3:
            if procesar_nomina_transporte(idnomina, ne , idempresa,empleados_ids):
                messages.success(request, "Proceso de Transporte realizado correctamente")
                return redirect('payroll:payrollview', id=idnomina)
            else :
                messages.error(request, "Error al realizar procesar la nómina")
                return redirect('payroll:payrollview', id=idnomina)
        
        elif type_payroll == 4:
            if procesar_nomina_reset(idnomina, ne, idempresa,empleados_ids,usuario):
                messages.success(request, "Reinicio de nómina realizado correctamente.")
                return redirect('payroll:payrollview', id=idnomina)
            else:
                messages.error(request, "Error al procesar el reinicio de la nómina.")
                return redirect('payroll:payrollview', id=idnomina)
        
        elif type_payroll == 5:
            if recalcular_nomina(idnomina):
                messages.success(request, "El recálculo de la nómina se realizó correctamente.")
                return redirect('payroll:payrollview', id=idnomina)
            else:
                messages.error(request, "No fue posible recalcular la nómina. Intente nuevamente.")
                return redirect('payroll:payrollview', id=idnomina)
        
        else:
            messages.error(request, "Error #13 al procesar la nómina.")
            return redirect('payroll:payrollview', id=idnomina)

    
    return render(request, 'payroll/partials/payroll_automatic_systems.html', 
                    {
                        'titulo': titulo,
                        'empleados':empleados, 
                        'centros': centros, 
                        'type_payroll': type_payroll , 
                        'idnomina':idnomina
                        
                        })



@transaction.atomic
def recalcular_nomina(idn):

    getcontext().prec = 50

    nomina = Crearnomina.objects.select_related('anoacumular').get(idnomina=idn)

    salario_anual = Salariominimoanual.objects.get(ano=nomina.anoacumular.ano)
    sal_min = salario_anual.salariominimo
    aux_tra = salario_anual.auxtransporte

    mes = nomina.fechainicial.month
    anio = nomina.fechainicial.year

    conceptos = [1, 2, 4, 34]

    registros = Nomina.objects.select_related(
        'idcontrato', 'idconcepto'
    ).filter(
        idnomina_id=idn,
        idconcepto__codigo__in=conceptos
    )

    contratos_procesados = {}
    updates = []
    deletes = []

    for data in registros:

        contrato = data.idcontrato
        codigo = data.idconcepto.codigo
        contrato_id = contrato.idcontrato

        # ==========================================
        # PROCESAR CONTRATO UNA SOLA VEZ
        # ==========================================
        if contrato_id not in contratos_procesados:

            calculo_prestamo(contrato, idn)
            Calculo_vacaciones(contrato, idn)
            calculo_novfija(contrato, idn)

            acumulados = precargar_acumulados(nomina, int(codigo))

            salario = salario_mes(contrato, mes, anio)

            contratos_procesados[contrato_id] = {
                "acumulados": acumulados,
                "salario": salario
            }

        else:
            acumulados = contratos_procesados[contrato_id]["acumulados"]
            salario = contratos_procesados[contrato_id]["salario"]

        # ==========================================
        # CALCULO DE DIAS
        # ==========================================
        diasnomina = calcular_dias(contrato, nomina, codigo, acumulados)

        if diasnomina <= 0:
            deletes.append(data.id)
            continue

        # ==========================================
        # SUELDO BASE
        # ==========================================
        if codigo in [1, 4, 34]:

            valor = (
                Decimal(salario) * Decimal(diasnomina) / Decimal('30')
            ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

        # ==========================================
        # TRANSPORTE
        # ==========================================
        elif codigo == 2:

            if contrato.salario >= (sal_min * 2):
                deletes.append(data.id)
                continue

            total_base_trans = Nomina.objects.filter(
                idcontrato=contrato,
                idnomina_id=idn,
                estadonomina=1,
                idconcepto__indicador__nombre='basetransporte'
            ).exclude(
                idconcepto__codigo=2
            ).aggregate(total=Sum('valor'))['total'] or 0

            if total_base_trans <= 0:
                deletes.append(data.id)
                continue

            if total_base_trans >= (sal_min * 2):
                deletes.append(data.id)
                continue

            valor = (
                Decimal(diasnomina) *
                (Decimal(aux_tra) / Decimal('30'))
            ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

        else:
            continue

        # ==========================================
        # ACTUALIZAR SOLO SI CAMBIA
        # ==========================================
        if data.valor != valor or data.cantidad != diasnomina:
            data.valor = valor
            data.cantidad = diasnomina
            updates.append(data)

    # ==========================================
    # BULK OPERATIONS (MUCHO MÁS RÁPIDO)
    # ==========================================
    if updates:
        Nomina.objects.bulk_update(updates, ["valor", "cantidad"])

    if deletes:
        Nomina.objects.filter(id__in=deletes).delete()


    empleados_raw = Nomina.objects \
        .select_related('idcontrato') \
        .filter(idnomina=id, estadonomina=1) \
        .values(
            'idcontrato'
        ) \
        .distinct()

    for empleado in empleados_raw:
        auto_recalculate(idn, empleado['idcontrato'])

    return True



def procesar_nomina_reset(idn, parte_nomina, idempresa, empleados, iduser):
    # Buscar registros de la nómina
    qs = Nomina.objects.filter(idnomina_id=idn)

    if qs.exists():
        # Eliminar registros
        count = qs.count()
        qs.delete()
        
        # Fecha y hora del reset
        fecha_reset = timezone.now().strftime("%d-%m-%Y %H:%M:%S")
        
        # Construir descripción detallada
        text = (
            f"Reset de nómina ID {idn} | "
            f"Empresa: {idempresa} | "
            f"Parte: {parte_nomina} | "
            f"Empleados afectados: {len(empleados) if empleados else 0} | "
            f"Registros eliminados: {count} | "
            f"Usuario: {iduser['id']} | "
            f"Fecha: {fecha_reset}"
        )
        
        # Guardar historial
        EditHistory.objects.create(
            modified_model="Nomina-all",
            modified_object_id=idn,
            user_id=iduser["id"],
            operation_type="delete",
            field_name="data",
            description=text,
            id_empresa_id=iduser["idempresa"],
        )

    # Si no existía nada, no se guarda nada en histórico
    return True



def procesar_nomina_basica(idn, parte_nomina,idempresa,empleados):
    """
    Procesa la nómina básica para todos los contratos activos de una empresa en un periodo determinado.

    Esta función calcula y registra el valor correspondiente a los días trabajados de cada contrato
    en una nómina específica. El valor se ajusta por ausencias relacionadas con vacaciones o incapacidades, 
    y se determina el concepto de nómina según el tipo de salario o contrato del empleado.

    Parameters
    ----------
    idn : int
        ID de la nómina a procesar.

    parte_nomina : int
        ID del centro de costo o parte de nómina a filtrar (0 si no se desea filtrar).

    idempresa : int
        ID de la empresa a la que pertenecen los contratos.

    Returns
    -------
    bool
        True si el proceso se ejecuta correctamente, o un string de error si ocurre un problema
        al obtener la nómina.

    See Also
    --------
    Crearnomina : Modelo que almacena los datos generales de una nómina.
    Contratos : Modelo que representa los contratos de empleados.
    Nomina : Modelo donde se registran los conceptos individuales por empleado.
    Conceptosdenomina : Catálogo de conceptos utilizados en la nómina.
    EditHistory : Registro de modificaciones hechas en la nómina.

    Notes
    -----
    - Se descuenta del total de días de nómina los días de vacaciones e incapacidades.
    - El código del concepto de nómina depende del tipo de salario y tipo de contrato.
    - Si el concepto ya existe y no tiene historial de edición, se actualiza; de lo contrario, se crea uno nuevo.
    """
    
    try:
        nomina = Crearnomina.objects.get(idnomina=idn)
    except Crearnomina.DoesNotExist:
        return "Error de creación de nómina"
    
    
    if not parte_nomina:
        parte_nomina = 0

    #  , idcontrato = 10353
    contratos = Contratos.objects.filter(estadoliquidacion=3, id_empresa =  idempresa  ) 
    

    if parte_nomina != 0:
        contratos = contratos.filter(idcosto=parte_nomina)

    if empleados: 
        contratos = contratos.filter(idcontrato__in = empleados)


    

    for contrato in contratos:

        if contrato.tiposalario.idtiposalario == 2:
            codigo_aux = '4'
        elif contrato.tipocontrato_id == 6:
            codigo_aux = '34'
        else:
            codigo_aux = '1'

        acumulados = precargar_acumulados(nomina, int(codigo_aux))
        concepto = Conceptosdenomina.objects.get(codigo=codigo_aux, id_empresa_id = idempresa)

        diasnomina = calcular_dias(contrato,nomina,int(codigo_aux),acumulados)

        calculo_prestamo(contrato, idn)
        Calculo_vacaciones(contrato, idn)
        calculo_novfija(contrato, idn)
        
        if diasnomina > 0:
            
            getcontext().prec = 50

            mes = nomina.fechainicial.month
            anio = nomina.fechainicial.year

            salario = salario_mes(contrato,mes,anio)

            valorsalario = (
                Decimal(str(salario))
                * Decimal(str(diasnomina))
                / Decimal('30')
            ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)


            aux_pass = Nomina.objects.filter(
                idconcepto=concepto,
                idcontrato=contrato,
                estadonomina = 1,
                idnomina_id=idn
            ).first()
            
            if aux_pass:
                if not EditHistory.objects.filter(
                    id_empresa_id=idempresa,
                    modified_object_id=aux_pass.idregistronom,
                    modified_model='Nomina',
                ).exists():
                    aux_pass.cantidad = diasnomina
                    aux_pass.valor = valorsalario
                    aux_pass.save()  
                    
            else:
                Nomina.objects.create(
                    idconcepto = concepto ,#*
                    cantidad=diasnomina ,#*
                    valor=valorsalario , #*
                    estadonomina = 1,
                    idcontrato_id=contrato.idcontrato ,
                    idnomina_id = idn ,
                )   
    
    
    return True





def procesar_nomina_incapacidad(idn, parte_nomina,idempresa,empleados):
    """
    Procesa las incapacidades médicas reportadas dentro del rango de fechas de una nómina.

    Esta función calcula y registra los valores correspondientes a las horas de incapacidad 
    asumidas por la empresa o por las entidades de salud, dependiendo del tipo de incapacidad. 
    Los valores son calculados a partir del IBC (ingreso base de cotización), ajustado según normativas.

    Parameters
    ----------
    idn : int
        ID de la nómina que se está procesando.

    parte_nomina : int
        ID del centro de costo o parte de nómina a filtrar (0 si no se desea filtrar).

    idempresa : int
        ID de la empresa sobre la que se aplican los cálculos.

    Returns
    -------
    bool
        True si el proceso se ejecuta correctamente.

    See Also
    --------
    Crearnomina : Modelo que representa los datos de una nómina.
    Incapacidades : Modelo con el registro de incapacidades por contrato.
    Nomina : Modelo donde se almacenan los conceptos resultantes de la incapacidad.
    Conceptosdenomina : Catálogo de conceptos de nómina.
    EditHistory : Modelo para auditar cambios en los registros de nómina.

    Notes
    -----
    - El IBC puede ser ajustado según si la empresa paga el 100% o el 66.7% de la incapacidad.
    - El valor mínimo del IBC es el salario mínimo del año correspondiente.
    - La función distingue los conceptos según si la incapacidad es EPS (primera o prolongada), ARL u otra.
    - Se registra la incapacidad en dos conceptos si hay días asumidos por la empresa y por la EPS/ARL.
    - Las horas se calculan a partir de los días usando una jornada de 8 horas diarias.
    - Si ya existe un registro del concepto y no ha sido editado, se actualiza; si no, se crea uno nuevo.
    """
    
    if not parte_nomina:
        parte_nomina = 0
        
    nomina = Crearnomina.objects.get(idnomina=idn)
    inicio_nomina, fin_nomina = nomina.fechainicial, nomina.fechafinal
    ano = nomina.anoacumular.ano 
    
    salario_minimo = Salariominimoanual.objects.get( ano = ano ).salariominimo
    pago_incapacidad = Empresa.objects.get(idempresa=1).ige100 or "NO"
    
    contratos = Contratos.objects.filter(estadoliquidacion=3, id_empresa =  idempresa )
    
    if parte_nomina != 0:
        contratos = contratos.filter(idcosto = parte_nomina)
    
    if empleados: 
        contratos = contratos.filter(idcontrato__in = empleados)
    
    incapacidades = Incapacidades.objects.filter(idcontrato__id_empresa =  idempresa, idcontrato__estadoliquidacion=3 )
    
    
    
    if parte_nomina != 0:
        incapacidades = incapacidades.filter(idcontrato__idcosto = parte_nomina)
    
    for incapacidad in incapacidades:
        #salario_minimo = Salariominimoanual.objects.get( ano = incapacidad.fechainicial.year ).salariominimo
        dias_incapacidad = 0 
        dias_asumidos = 0
        ini = incapacidad.fechainicial
        fin = ini + timedelta(days = incapacidad.dias ) - timedelta(days = 1 )
        
        
        ibc = incapacidad.ibc
        tipo = incapacidad.origenincap
        prorroga = incapacidad.prorroga
        dias = incapacidad.dias

    if empleados: 

        contratos = contratos.filter(idcontrato__in = empleados)

    for contract in contratos : 
        incapacidades = Incapacidades.objects.filter(idcontrato__id_empresa =  idempresa, idcontrato = contract ).order_by('fechainicial')
        if parte_nomina != 0:
            incapacidades = incapacidades.filter(idcontrato__idcosto = parte_nomina)
        
        for incapacidad in incapacidades:
            dias_incapacidad = 0 
            dias_asumidos = 0
            ini = incapacidad.fechainicial
            fin = ini + timedelta(days = incapacidad.dias ) - timedelta(days = 1 )
            
            
            ibc = incapacidad.ibc
            tipo = incapacidad.origenincap
            prorroga = incapacidad.prorroga
            dias = incapacidad.dias

            segundo_dia = ini + timedelta(days=1)
            dia_asumido_1 = int(inicio_nomina <= ini <= fin_nomina)
            dia_asumido_2 = int(inicio_nomina <= segundo_dia <= fin_nomina)
            dias_asumidos = dia_asumido_1 + dia_asumido_2 if dias != 1 else dia_asumido_1
            
            
            if ini <= inicio_nomina <= fin <= fin_nomina:
                # Incapacidad empieza antes de la nómina y termina dentro de ella
                dias_incapacidad = (fin - inicio_nomina).days + 1   # ✅ antes estaba (fin_nomina - inicio_nomina)
            elif ini <= inicio_nomina <= fin_nomina <= fin:
                # Incapacidad cubre toda la nómina
                dias_incapacidad = (fin_nomina - inicio_nomina).days + 1
            elif inicio_nomina <= ini <= fin <= fin_nomina:
                # Incapacidad completamente dentro de la nómina
                dias_incapacidad = (fin - ini).days + 1
            elif ini >= inicio_nomina and fin >= fin_nomina:
                # Incapacidad empieza en la nómina y sigue después
                dias_incapacidad = (fin_nomina - ini).days + 1

            else:
                dias_incapacidad = 0
                    
            #Calculo del IBC
            if pago_incapacidad == "NO":
                ibc = round(ibc * 2 / 3, 0)
                
            if ibc < salario_minimo:
                ibc = salario_minimo
            

            #Tipo de incapacidad
            if tipo == '1':
                idconceptoi = Conceptosdenomina.objects.get(codigo=25, id_empresa_id = idempresa)
                idconceptoa = Conceptosdenomina.objects.get(codigo=26, id_empresa_id = idempresa) 
                
            elif tipo == '2':
                
                dias_asumidos = dia_asumido_1
                ibc = incapacidad.ibc
                
                idconceptoi = Conceptosdenomina.objects.get(codigo=27, id_empresa_id = idempresa)
                idconceptoa = Conceptosdenomina.objects.get(codigo=28, id_empresa_id = idempresa) 
                
            elif tipo == '3':
                dias_asumidos = 0
                idconceptoi = Conceptosdenomina.objects.get(codigo=29, id_empresa_id = idempresa)
            
            else :
                idconceptoa = None
                idconceptoi = None
            
                
            if prorroga:

                dias_incapacidad = calculo_incapacidad(contract.idcontrato, nomina)
                ibc = disabilities_ibc(contract , str(inicio_nomina) )
                valor_incapacidad = (ibc / 30 ) * dias_incapacidad

        valor_asumido = (
            Decimal(ibc) / Decimal('240') * Decimal(horas_asumidas)
        ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        
        
        if dias_asumidos > 0 :
            if idconceptoa :
                
                aux_pass = Nomina.objects.filter(
                    idconcepto = idconceptoa,
                    idcontrato = incapacidad.idcontrato , 
                    estadonomina = 1,
                    control = incapacidad.idincapacidad,
                    idnomina_id=idn
                ).first()

                dias_incapacidad -= dias_asumidos

                
                horas_incapacidad = dias_incapacidad * 8
                horas_asumidas = dias_asumidos * 8

                valor_incapacidad = (
                    Decimal(ibc) / Decimal('240') * Decimal(horas_incapacidad)
                ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

                valor_asumido = (
                    Decimal(ibc) / Decimal('240') * Decimal(horas_asumidas)
                ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
                
                
                if dias_asumidos > 0 :
                    if idconceptoa :
                        aux_pass = Nomina.objects.filter(
                            idconcepto = idconceptoa,
                            idcontrato = incapacidad.idcontrato , 
                            estadonomina = 1,
                            idnomina_id=idn
                        ).first()

                        if aux_pass:
                            if not EditHistory.objects.filter(
                                id_empresa_id=idempresa,
                                modified_object_id=aux_pass.idregistronom,
                                modified_model='Nomina',
                            ).exists():


                                aux_pass.cantidad = horas_asumidas/8
                                aux_pass.valor =  valor_asumido
                                aux_pass.save() 
                                
                        else:
                            Nomina.objects.create(
                                valor = valor_asumido,
                                cantidad = horas_asumidas/8,
                                idconcepto = idconceptoa , 
                                idnomina = nomina , 
                                estadonomina = 1,
                                idcontrato = incapacidad.idcontrato , 
                                control = incapacidad.idincapacidad,
                            ) 
                        

                if dias_incapacidad > 0:
                    if idconceptoi :
                        aux_pass = Nomina.objects.filter(
                            idconcepto = idconceptoi,
                            idcontrato = incapacidad.idcontrato , 
                            idnomina_id=idn
                        ).first()
                        
                        if aux_pass:
                            if not EditHistory.objects.filter(
                                id_empresa_id=idempresa,
                                modified_object_id=aux_pass.idregistronom,
                                modified_model='Nomina',
                            ).exists():
                                aux_pass.cantidad = horas_incapacidad/8
                                aux_pass.valor =  valor_incapacidad
                                aux_pass.save()  
                                            
                        else:
                            Nomina.objects.create(
                                valor = valor_incapacidad,
                                cantidad = horas_incapacidad/8,
                                idconcepto = idconceptoi, 
                                idnomina = nomina, 
                                estadonomina = 1,
                                idcontrato = incapacidad.idcontrato, 
                                control = incapacidad.idincapacidad,
                            )  
                        
        
        
    
    return True


def procesar_nomina_aportes(idn, parte_nomina,idempresa,empleados):
    """
    Procesa los aportes obligatorios a seguridad social (EPS, AFP y FSP) para los contratos activos en una nómina.

    Esta función calcula los valores que deben descontarse al empleado por concepto de EPS, AFP y FSP 
    según la base de cotización determinada por los conceptos salariales devengados. El cálculo considera 
    topes máximos de cotización y aplica condiciones especiales como tipo de salario integral y 
    exenciones por condición de pensionado.

    Parameters
    ----------
    idn : int
        ID de la nómina que se está procesando.

    parte_nomina : int
        ID del centro de costo o parte de nómina a filtrar (0 si no se desea filtrar).

    idempresa : int
        ID de la empresa sobre la que se aplican los cálculos.

    Returns
    -------
    bool
        True si el proceso se ejecuta correctamente.

    See Also
    --------
    Nomina : Modelo donde se almacenan los conceptos deducidos de la nómina.
    Conceptosfijos : Tabla de valores fijos como porcentaje EPS/AFP o topes.
    Conceptosdenomina : Catálogo de conceptos de nómina con su codificación.
    Contratos : Modelo que representa los contratos activos de los empleados.
    EditHistory : Modelo para auditar cambios en los registros de nómina.

    Notes
    -----
    - El cálculo de la base de cotización excluye ciertos conceptos como cesantías, primas, etc.
    - Si el salario es de tipo integral, se ajusta la base según el porcentaje del factor integral.
    - El FSP se aplica solo si la base supera los 4 salarios mínimos, y su porcentaje varía por rango.
    - Si el empleado es pensionado (valor '2'), no se aplican descuentos de AFP ni FSP.
    - Los valores se registran como negativos en la tabla `Nomina`, indicando deducción.
    - Si ya existe un registro y no ha sido editado por el usuario, se actualiza; si no, se crea uno nuevo.
    """
    
    
    EPS = Conceptosfijos.objects.get(idfijo = 8)
    AFP = Conceptosfijos.objects.get(idfijo = 10)
    tope_ibc = Conceptosfijos.objects.get(idfijo = 2)
    factor_integral = Conceptosfijos.objects.get(idfijo = 1).valorfijo
    
    ## pruebas de valores 
    fsp416 = Conceptosfijos.objects.get(idfijo = 12).valorfijo
    fsp1617 = Conceptosfijos.objects.get(idfijo = 13).valorfijo
    fsp1718 = Conceptosfijos.objects.get(idfijo = 14).valorfijo
    fsp1819 = Conceptosfijos.objects.get(idfijo = 15).valorfijo
    fsp1920 = Conceptosfijos.objects.get(idfijo = 16).valorfijo
    fsp21 = Conceptosfijos.objects.get(idfijo = 17).valorfijo

    
    sal_min = Salariominimoanual.objects.get(ano = datetime.now().year).salariominimo

    if not parte_nomina:
        parte_nomina = 0
    # ,idcontrato = 8113
    contratos = Contratos.objects.filter(estadocontrato=1, id_empresa =  idempresa  )
    if parte_nomina != 0:
        contratos = contratos.filter(idcosto = parte_nomina)
    
    if empleados: 
        contratos = contratos.filter(idcontrato__in = empleados)
    
    for contrato in contratos:
        
        tipo_salario = contrato.tiposalario.idtiposalario

        
        # Obtener la suma de las deducciones de la eps 
        total_base_ss = Nomina.objects.filter(
            idcontrato=contrato,
            idnomina_id=idn,
            estadonomina = 1 ,
            idconcepto__indicador__nombre='basesegsocial'
        ).exclude(
            idconcepto__codigo__in=[60, 70, 90] # Excluir conceptos cuyo código sea el de EPS
        ).aggregate(total=Sum('valor'))['total'] or 0  # Reemplaza 'monto' con el nombre correcto de la columna
                
        nomina = Crearnomina.objects.get( idnomina = idn)
        
        base_ss_fsp =   Nomina.objects.filter(
            idcontrato = contrato,
            idnomina__mesacumular = nomina.mesacumular ,
            idnomina__anoacumular = nomina.anoacumular ,
            idconcepto__indicador__nombre='basesegsocial'
        ).exclude(
            idconcepto__codigo__in=[60, 70, 90] # Excluir conceptos cuyo código sea el de EPS
        ).aggregate(total=Sum('valor'))['total'] or 0  # Reemplaza 'monto' con el nombre correcto de la columna
        
        
        if contrato.tiposalario.idtiposalario == 2:
            base_ss_fsp2 = base_ss_fsp * Decimal('0.7')
        else : 
            base_ss_fsp2 = base_ss_fsp


        if total_base_ss > 0:
                    
            concepto1 = Conceptosdenomina.objects.get(codigo=60, id_empresa_id=idempresa)
            concepto2 = Conceptosdenomina.objects.get(codigo=70, id_empresa_id=idempresa)
            concepto3 = Conceptosdenomina.objects.get(codigo=90, id_empresa_id=idempresa)
            
            base_max = sal_min * tope_ibc.valorfijo

            if tipo_salario == 2:
                total_base_ss *= (factor_integral / 100)
                total_base_ss = round(total_base_ss, 2)
            
            base_ss = min(total_base_ss, base_max)
            base_ss = round(base_ss, 2)
        

            if base_ss_fsp2 <= (sal_min * 4):
                FSP = 0
            if (base_ss_fsp2 > (sal_min * 4)) :
                FSP = fsp416
            elif (base_ss_fsp2 > (sal_min * 16)):
                FSP = fsp1617
            elif (base_ss_fsp2 > (sal_min * 17)):
                FSP = fsp1718
            elif (base_ss_fsp2 > (sal_min * 18)):
                FSP = fsp1819
            elif (base_ss_fsp2 > (sal_min * 19)):
                FSP = fsp1920
            elif base_ss_fsp2 > (sal_min * 20):
                FSP = fsp21
            else:
                FSP = 0
            

            valorfsp = (
                    Decimal(str(base_ss_fsp2)) * Decimal(str(FSP)) / Decimal('100')
                ).quantize(Decimal('1'), rounding=ROUND_HALF_UP) if FSP > 0 else Decimal('0')
            
            
            valoreps = (
                Decimal(total_base_ss) *
                Decimal(EPS.valorfijo) / Decimal('100')
            ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

            valorafp = (
                Decimal(total_base_ss) *
                Decimal(AFP.valorfijo) / Decimal('100')
            ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

            


            if contrato.pensionado == '2':
                valorafp = 0.00
                valorfsp = 0.00
            



            #* Crear o actualizar el registro de la EPS
            aux_pass = Nomina.objects.filter(
                idconcepto=concepto1,
                idcontrato=contrato,
                estadonomina = 1,
                idnomina_id=idn
            ).first()
            
            if aux_pass:
                if not EditHistory.objects.filter(
                    id_empresa_id=idempresa,
                    modified_object_id=aux_pass.idregistronom,
                    modified_model='Nomina',
                ).exists():
                    aux_pass.cantidad = 0
                    aux_pass.valor = -1*valoreps
                    aux_pass.save() 
            else:
                Nomina.objects.create(
                        idconcepto = concepto1 ,#*
                        cantidad= 0 ,#*
                        estadonomina = 1,
                        valor=-1*valoreps , #*
                        idcontrato_id=contrato.idcontrato ,
                        idnomina_id = idn ,
                    )  
                
    
            #* Crear o actualizar el registro de la Pension
            
            aux_pass = Nomina.objects.filter(
                idconcepto=concepto2,
                idcontrato=contrato,
                estadonomina = 1,
                idnomina_id=idn
            ).first()
            
            
            if aux_pass:
                if not EditHistory.objects.filter(
                    id_empresa_id=idempresa,
                    modified_object_id=aux_pass.idregistronom,
                    modified_model='Nomina',
                ).exists():
                    aux_pass.cantidad = 0
                    aux_pass.valor = -1*valorafp
                    aux_pass.save() 
                                
            else:


                Nomina.objects.create(
                        idconcepto = concepto2 ,#*
                        cantidad= 0,#*
                        estadonomina = 1,
                        valor=-1*valorafp , #*
                        idcontrato_id=contrato.idcontrato ,
                        idnomina_id = idn ,
                    ) 
            
            
            
            if valorfsp > 0:

                aux_pass1 = Nomina.objects.filter(
                    idconcepto=concepto3,
                    idcontrato=contrato,
                    idnomina__mesacumular = nomina.mesacumular ,
                    idnomina__anoacumular = nomina.anoacumular ,
                    estadonomina = 2,
                ).first()
                

                if aux_pass1 :
                    valorfsp = (
                            Decimal(str(valorfsp)) / Decimal('2')
                        ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

                aux_pass = Nomina.objects.filter(
                    idconcepto=concepto3,
                    idcontrato=contrato,
                    estadonomina = 1,
                    idnomina_id=idn
                ).first()
                
                
                if aux_pass:
                    if not EditHistory.objects.filter(
                        id_empresa_id=idempresa,
                        modified_object_id=aux_pass.idregistronom,
                        modified_model='Nomina',
                    ).exists():
                        aux_pass.cantidad = 0
                        aux_pass.valor = -1*valorfsp
                        aux_pass.save() 
                                    
                else:
                    Nomina.objects.create(
                            idconcepto = concepto3 ,#*
                            cantidad= 0,#*
                            estadonomina = 1,
                            valor=-1*valorfsp , #*
                            idcontrato_id=contrato.idcontrato ,
                            idnomina_id = idn ,
                        ) 
                    
    return True



def _mes_numero_desde_mesacumular(mesacumular_str):
    if not mesacumular_str or not str(mesacumular_str).strip():
        return None
    target = str(mesacumular_str).strip().upper()
    for idx, (key, _lbl) in enumerate(MES_CHOICES):
        if key and key.upper() == target:
            return idx
    return None


def procesar_nomina_transporte(idn, parte_nomina, idempresa, empleados):
    """
    Procesa el auxilio de transporte para los contratos activos dentro de una nómina.

    En general los días se alinean al sueldo básico del periodo (típicamente 15 o 30). Si ya hubo
    transporte en otra nómina del mes, se liquida el saldo restando lo pagado, sin superar el básico
    actual. Si la primera quincena del mes no tiene días de transporte y en otras nóminas del mes
    tampoco se pagó, en la segunda se liquida el saldo del mes completo aunque el básico sea 15.

    Parameters
    ----------
    idn : int
        ID de la nómina que se está procesando.

    parte_nomina : int
        ID del centro de costo o parte de nómina a filtrar (0 si no se desea filtrar).

    idempresa : int
        ID de la empresa sobre la que se aplican los cálculos.

    Returns
    -------
    bool
        True si el proceso se ejecuta correctamente.

    See Also
    --------
    Crearnomina : Modelo que representa los datos de una nómina.
    Nomina : Modelo donde se almacenan los conceptos resultantes del auxilio.
    Conceptosdenomina : Catálogo de conceptos de nómina.
    EditHistory : Modelo para auditar cambios en los registros de nómina.
    Salariominimoanual : Tabla con los valores del salario mínimo y auxilio de transporte por año.

    Notes
    -----
    - Solo se liquida el auxilio si el salario es inferior a dos salarios mínimos y el contrato
        no tiene ``auxiliotransporte`` (vive en el lugar de trabajo).
    - Requiere base ``basetransporte`` por debajo de 2 SMMLV o días de básico calculables en la nómina.
    - El concepto usado tiene código ``2``.
    """

    if not parte_nomina:
        parte_nomina = 0

    contratos = Contratos.objects.filter(estadocontrato=1, id_empresa=idempresa)

    if parte_nomina != 0:
        contratos = contratos.filter(idcosto=parte_nomina)

    if empleados:
        contratos = contratos.filter(idcontrato__in=empleados)

    try:
        nomina = Crearnomina.objects.get(idnomina=idn)
    except Crearnomina.DoesNotExist:
        return "Error de creación de nómina"

    sal_min = Salariominimoanual.objects.get(ano=nomina.anoacumular.ano).salariominimo
    aux_tra = Salariominimoanual.objects.get(ano=nomina.anoacumular.ano).auxtransporte
    concepto = Conceptosdenomina.objects.get(codigo=2, id_empresa_id=idempresa)
    acumulados = precargar_acumulados(nomina, 2)

    for contrato in contratos:
        diasnomina = calcular_dias(
            contrato,
            nomina,
            2,
            acumulados
        )

        if contrato.tipocontrato.idtipocontrato in [5, 6]:
            continue

        transporte = return_transporte(contrato, nomina, diasnomina, sal_min, aux_tra)

        aux_pass = Nomina.objects.filter(
            idconcepto=concepto,
            idcontrato=contrato,
            estadonomina=1,
            idnomina_id=idn,
        ).first()

        if diasnomina > 0 and transporte > 0:
            if aux_pass:
                if not EditHistory.objects.filter(
                    id_empresa_id=idempresa,
                    modified_object_id=aux_pass.idregistronom,
                    modified_model='Nomina',
                ).exists():
                    aux_pass.cantidad = diasnomina
                    aux_pass.valor = transporte
                    aux_pass.save()
            else:
                Nomina.objects.create(
                    idconcepto=concepto,
                    cantidad=diasnomina,
                    valor=transporte,
                    estadonomina=1,
                    idcontrato=contrato,
                    idnomina_id=idn,
                )
        elif aux_pass and not EditHistory.objects.filter(
            id_empresa_id=idempresa,
            modified_object_id=aux_pass.idregistronom,
            modified_model='Nomina',
        ).exists():
            aux_pass.cantidad = 0
            aux_pass.valor = Decimal('0')
            aux_pass.save()

    return True



def normalizar_dia(d):
    """Convierte día 31 en 30 para calendario laboral."""
    if d.day == 31:
        return d.replace(day=30)
    return d


def dias_360(inicio, fin):
    """Calcula diferencia usando calendario 30/360."""
    inicio = normalizar_dia(inicio)
    fin = normalizar_dia(fin)

    return (
        (fin.year - inicio.year) * 360 +
        (fin.month - inicio.month) * 30 +
        (fin.day - inicio.day)
    ) + 1



def calcular_vacaciones(contrato,nomina):
    """
    Calcula los días de vacaciones que se cruzan con el período de la nómina.

    Esta función determina cuántos días de vacaciones corresponden dentro del rango de fechas 
    de una nómina, considerando únicamente vacaciones efectivas de tipo legal ('tipovac' = '1') 
    y con estado aprobado (`estado = 2`).

    Parameters
    ----------
    contrato : Contratos
        Objeto de contrato al que se le desea calcular los días de vacaciones.

    nomina : Crearnomina
        Objeto de nómina con las fechas que se utilizarán para determinar el cruce.

    Returns
    -------
    int
        Número de días de vacaciones que coinciden con el período de la nómina.

    See Also
    --------
    EmpVacaciones : Modelo maestro de solicitudes de vacaciones.
    Vacaciones : Modelo con el detalle de fechas por solicitud de vacaciones.
    """
    dias_vacaciones = dias_en_nomina = 0

    vacaciones = Vacaciones.objects.filter(
        idcontrato_id=contrato,
        tipovac__idvac=1
    )

    if not vacaciones.exists():
        return 0

    dias_nomina = (nomina.diasnomina)

    for vac in vacaciones:

        if not vac.fechainicialvac or not vac.ultimodiavac:
            continue

        # validar cruce
        if vac.fechainicialvac <= nomina.fechafinal and vac.ultimodiavac >= nomina.fechainicial:

            inicio_cruce = max(vac.fechainicialvac, nomina.fechainicial)
            fin_cruce = min(vac.ultimodiavac, nomina.fechafinal)

            # si cubre toda la nómina
            if inicio_cruce == nomina.fechainicial and fin_cruce == nomina.fechafinal:
                dias_en_nomina = dias_nomina
            else:
                dias_en_nomina = dias_360(inicio_cruce, fin_cruce)
    
            dias_vacaciones += dias_en_nomina


    return min(dias_vacaciones, dias_nomina)



def calcular_suspenciones(contrato,nomina ):
    """
    Calcula los días de vacaciones que se cruzan con el período de la nómina.

    Esta función determina cuántos días de vacaciones corresponden dentro del rango de fechas 
    de una nómina, considerando únicamente vacaciones efectivas de tipo legal ('tipovac' = '1') 
    y con estado aprobado (`estado = 2`).

    Parameters
    ----------
    contrato : Contratos
        Objeto de contrato al que se le desea calcular los días de vacaciones.

    nomina : Crearnomina
        Objeto de nómina con las fechas que se utilizarán para determinar el cruce.

    Returns
    -------
    int
        Número de días de vacaciones que coinciden con el período de la nómina.

    See Also
    --------
    EmpVacaciones : Modelo maestro de solicitudes de vacaciones.
    Vacaciones : Modelo con el detalle de fechas por solicitud de vacaciones.
    """

    dias_vacaciones = 0

    vacaciones = Vacaciones.objects.filter(
        idcontrato_id=contrato,
        tipovac__idvac__in=[3, 4, 5]
    )

    if not vacaciones.exists():
        return 0

    dias_nomina = (nomina.diasnomina)

    for vac in vacaciones:
        
        if not vac.fechainicialvac or not vac.ultimodiavac:
            continue

        # Validar cruce con la nómina
        if vac.fechainicialvac <= nomina.fechafinal and vac.ultimodiavac >= nomina.fechainicial:
            
            inicio_cruce = max(vac.fechainicialvac, nomina.fechainicial)
            fin_cruce = min(vac.ultimodiavac, nomina.fechafinal)
            
            # si cubre toda la nómina
            if inicio_cruce == nomina.fechainicial and fin_cruce == nomina.fechafinal:
                dias_en_nomina = dias_nomina
            else:
                dias_en_nomina = dias_360(inicio_cruce, fin_cruce)
            
            dias_vacaciones += dias_en_nomina
            #print(f"id {vac.idvacaciones}  ds {dias_en_nomina} ddb {vac.diascalendario}")
    
    return min(dias_vacaciones, dias_nomina)

def calcular_suspenciones2(vac, nomina):
    """
    Calcula los días de una vacación que se cruzan con la nómina.
    """

    if not vac.fechainicialvac or not vac.ultimodiavac:
        return 0

    if not (vac.fechainicialvac <= nomina.fechafinal and vac.ultimodiavac >= nomina.fechainicial):
        return 0
    
    dias_nomina = (nomina.diasnomina)

    inicio_cruce = max(vac.fechainicialvac, nomina.fechainicial)
    fin_cruce = min(vac.ultimodiavac, nomina.fechafinal)

    # si cubre toda la nómina
    if inicio_cruce == nomina.fechainicial and fin_cruce == nomina.fechafinal:
        dias_en_nomina = dias_nomina
    else:
        dias_en_nomina = dias_360(inicio_cruce, fin_cruce)

    return dias_en_nomina

def calculo_incapacidad(contrato,nomina):  
    """
    Calcula los días de incapacidad registrados en la nómina para un contrato.

    Esta función consulta los registros de incapacidad presentes en la nómina 
    a través de los conceptos con códigos específicos asociados a incapacidades.

    Parameters
    ----------
    contrato : Contratos
        Objeto de contrato al que se le desea calcular la incapacidad.

    idn : int
        ID de la nómina correspondiente al período a evaluar.

    Returns
    -------
    int
        Número total de días de incapacidad registrados.

    See Also
    --------
    Nomina : Modelo donde se registran los conceptos de nómina, incluyendo incapacidades.
    """

    dias_incapacidad = 0

    # 🔹 Obtener incapacidades del contrato actual
    incapacidades = Incapacidades.objects.filter(idcontrato_id=contrato)
    
    

    for inc in incapacidades:
            

        if inc.fechainicial and inc.dias:
            fechaini = inc.fechainicial
            fechafin = fechaini + timedelta(days=inc.dias - 1)
            
            # Solo si hay cruce entre incapacidad y periodo de nómina
            if fechaini <= nomina.fechafinal and fechafin >= nomina.fechainicial:
                inicio = max(fechaini, nomina.fechainicial)
                fin = min(fechafin, nomina.fechafinal)
                dias_incapacidad += (fin - inicio).days + 1
                #print(f"id {inc.idincapacidad}  ds {dias_incapacidad} ddb {inc.dias}")
    return dias_incapacidad




def Calculo_vacaciones(contrato, idn):

    nomina_actual = Crearnomina.objects.get(idnomina=idn)

    vacaciones = Vacaciones.objects.filter(
        idcontrato=contrato,
        tipovac__idvac__in=[3, 4, 5]
    )

    for vaca in vacaciones:
        if not vaca.fechainicialvac or not vaca.ultimodiavac:
            continue

        concepto1 = None
        concepto2 = None
        if vaca.fechainicialvac <= nomina_actual.fechafinal and vaca.ultimodiavac >= nomina_actual.fechainicial:

            # Definir conceptos según tipo
            if vaca.tipovac.idvac == 4:
                concepto1 = Conceptosdenomina.objects.get(
                    codigo=31,
                    id_empresa_id=contrato.id_empresa_id
                )
                concepto2 = Conceptosdenomina.objects.get(
                    codigo=83,
                    id_empresa_id=contrato.id_empresa_id
                )

            elif vaca.tipovac.idvac == 3:
                concepto2 = Conceptosdenomina.objects.get(
                    codigo=82,
                    id_empresa_id=contrato.id_empresa_id
                )

            elif vaca.tipovac.idvac == 5:
                concepto1 = Conceptosdenomina.objects.get(
                    codigo=30,
                    id_empresa_id=contrato.id_empresa_id
                )
                concepto2 = Conceptosdenomina.objects.get(
                    codigo=86,
                    id_empresa_id=contrato.id_empresa_id
                )

            dias_suspensiones = calcular_suspenciones2(
                vaca,
                nomina_actual
            )

            if dias_suspensiones <= 0:
                continue


            mes = vaca.fechainicialvac.month
            anio = vaca.fechainicialvac.year

            salario = salario_mes(contrato,mes,anio)

            dias =  salario / 30
            valor_calculado = dias * dias_suspensiones

            # 🔹 Si NO es tipo 3, manejar concepto1
            if vaca.tipovac.idvac != 3 and concepto1:

                Nomina.objects.update_or_create(
                    idnomina=nomina_actual,
                    idconcepto=concepto1,
                    control=vaca.idvacaciones,
                    defaults={
                        "cantidad": dias_suspensiones,
                        "estadonomina": 1,
                        "valor": valor_calculado,
                        "idcontrato": vaca.idcontrato,
                    }
                )

                # 🔹 Manejar concepto2 (siempre existe en los 3 tipos)
                Nomina.objects.update_or_create(
                    idnomina=nomina_actual,
                    idconcepto=concepto2,
                    control=vaca.idvacaciones,
                    defaults={
                        "cantidad": dias_suspensiones,
                        "estadonomina": 1,
                        "valor": -valor_calculado,
                        "idcontrato": vaca.idcontrato,
                    }
                )
            else : 
                # 🔹 Manejar concepto2 (siempre existe en los 3 tipos)
                Nomina.objects.update_or_create(
                    idnomina=nomina_actual,
                    idconcepto=concepto2,
                    control=vaca.idvacaciones,
                    defaults={
                        "cantidad": dias_suspensiones,
                        "estadonomina": 1,
                        "valor": valor_calculado,
                        "idcontrato": vaca.idcontrato,
                    }
                )



def calculo_prestamo(contrato, idn):
    """
    Calcula y registra las deducciones por préstamos activos de un contrato.

    Esta función verifica si un préstamo está activo y si ya fue deducido en la nómina actual. 
    Si no ha sido registrado, se calcula el valor correspondiente a descontar (cuota del préstamo) 
    y se crea un registro en la nómina. Si ya hay deducciones previas, se verifica si el préstamo 
    ya está totalmente cubierto.

    Parameters
    ----------
    contrato : Contratos
        Objeto de contrato asociado al préstamo.

    idn : int
        ID de la nómina actual donde se registra la deducción.

    See Also
    --------
    Prestamos : Modelo que representa los préstamos otorgados.
    Conceptosdenomina : Catálogo de conceptos de nómina.
    Nomina : Modelo donde se registran los descuentos de los préstamos.
    """

    # Obtener la nómina actual
    nomina_actual = Crearnomina.objects.get(idnomina=idn)

    # Préstamos activos del contrato
    loans = Prestamos.objects.filter(
        idcontrato=contrato,
        estadoprestamo=True
    ).order_by('-idprestamo')
    
    # Concepto del préstamo
    conceptosdenomina = Conceptosdenomina.objects.get(
        codigo=50,
        id_empresa=contrato.id_empresa_id
    )

    for load in loans:
        # ---------------------------------------------------------
        # Ejecutar solo si el préstamo se creó ANTES o el MISMO día
        # ---------------------------------------------------------

        fecha = load.fechaprestamo

        if fecha is None:
            break

        # ignorar solo los que nacen después de la nómina
        if fecha > nomina_actual.fechafinal:
            continue

        # Verificar si ya está registrado en la nómina actual
        nominactual = Nomina.objects.filter(
            idnomina=idn,
            idconcepto=conceptosdenomina,
            control=load.idprestamo
        ).exists()

        # Deducciones anteriores de este préstamo
        deducciones = Nomina.objects.filter(
            idconcepto=conceptosdenomina,
            control=load.idprestamo,
        )

        suma_deducciones = deducciones.aggregate(
            total=Sum('valor')
        )['total'] or 0

        # --- Cálculo del valor a descontar ---
        if deducciones.exists():
            # Ya existen descuentos previos
            
            if not nominactual:
                # No está en la nómina actual → crear registro

                if (load.valorprestamo + suma_deducciones) > load.valorcuota:
                    valor = load.valorcuota
                else:
                    valor = load.valorprestamo + suma_deducciones

                if valor != 0:
                    Nomina.objects.create(
                        idconcepto=conceptosdenomina,
                        cantidad=1,
                        estadonomina=1,
                        valor=-1 * valor,
                        idcontrato=contrato,
                        idnomina_id=idn,
                        control=load.idprestamo
                    )

            else:
                # Ya existe en esta nómina → actualizar
                
                aux_pass = Nomina.objects.filter(
                    idconcepto=conceptosdenomina,
                    idcontrato=contrato,
                    estadonomina = 1,
                    idnomina_id=idn
                ).first()
                
                # if aux_pass:
                #     if not EditHistory.objects.filter(
                #         id_empresa_id=idempresa,
                #         modified_object_id=aux_pass.idregistronom,
                #         modified_model='Nomina',
                #     ).exists():
                #         aux_pass.cantidad = diasnomina
                #         aux_pass.valor = valorsalario
                #         aux_pass.save() 

                registro = Nomina.objects.get(
                    idnomina=idn,
                    idconcepto=conceptosdenomina,
                    control=load.idprestamo
                )

                if (load.valorprestamo + suma_deducciones) > load.valorcuota:
                    valor = load.valorcuota
                else:
                    valor = load.valorprestamo + suma_deducciones

                if valor != 0:
                    registro.valor = -1 * valor
                    registro.save()

        else:
            # Primera cuota del préstamo
            valor = load.valorcuota
            if valor != 0:
                Nomina.objects.create(
                    idconcepto=conceptosdenomina,
                    cantidad=1,
                    valor=-1 * valor,
                    estadonomina=1,
                    idcontrato=contrato,
                    idnomina_id=idn,
                    control=load.idprestamo
                )
    
def calculo_novfija(contrato, idn):
    """
    Regenera las novedades fijas para un contrato en la nómina dada.

    Flujo:
        1) Trae NovFijos activas del contrato.
        2) Construye lista de ids (idnovfija).
        3) Elimina en Nomina únicamente los registros con control en esos ids para la nómina y contrato.
        4) Recrea las filas en Nomina según la lógica de días/fechas.
    """
    # Obtener la nómina
    nomina = Crearnomina.objects.get(pk=idn)

    # 1) Traer las novedades fijas activas del contrato
    novs = list(NovFijos.objects.filter(idcontrato=contrato, estado_novfija=True).order_by('-idnovfija'))

    if not novs:
        # No hay novedades fijas activas -> nada que recrear
        return 0

    # 2) lista de ids de novedad (control)
    nov_ids = [nov.idnovfija for nov in novs]

    created_count = 0

    # 3) Transacción: eliminar y recrear
    with transaction.atomic():
        # Eliminar solamente los registros de Nomina asociados a esas novedades, esa nómina y ese contrato
        Nomina.objects.filter(
            idcontrato=contrato,
            idnomina_id=idn,
            control__in=nov_ids
        ).delete()
        

        # Preparar instancias para bulk_create
        objetos_a_crear = []

        for nov in novs:
            # Determinar valor base (asegúrate que nov.valor está definido)
            valor = getattr(nov, 'valor', 0) or 0
            if nomina.diasnomina < 16:
                valor = valor / 2

            cantidad = 1

            # # Lógica de fecha fin de novedad
            # if nov.fechafinnovedad:
            #     # Si la fecha fin cae dentro del periodo de la nómina => cantidad 0
            #     if nomina.fechainicial <= nov.fechafinnovedad <= nomina.fechafinal:
            #         cantidad = 0
            #     else:
            #         # Si la fecha fin ya pasó marcamos la novedad como inactiva
            #         nov.estado_novfija = False
            #         nov.save()

            if nov.idconcepto.codigo == 91:
                nuevo = Nomina(
                    idconcepto=nov.idconcepto,
                    cantidad=cantidad,
                    valor = -(float(nov.pago)) ,
                    estadonomina=1,
                    idcontrato=contrato,
                    idnomina_id=idn,
                    control=nov.idnovfija
                )
    
            else : 
                # Construir instancia Nomina (sin .save())
                nuevo = Nomina(
                    idconcepto=nov.idconcepto,
                    cantidad=cantidad,
                    valor= valor,
                    estadonomina=1,
                    idcontrato=contrato,
                    idnomina_id=idn,
                    control=nov.idnovfija
                )
            objetos_a_crear.append(nuevo)

        # Bulk create para eficiencia
        if objetos_a_crear:
            created_objs = Nomina.objects.bulk_create(objetos_a_crear)
            created_count = len(created_objs)

    return created_count





def calcular_dias_en_nomina(contrato, inicio_nomina, fin_nomina, tipo_nomina,nomina):
    """
    Calcula los días que un contrato debe tener dentro de una nómina de forma eficiente.
    
    Reglas especiales:
    - Febrero mensual: siempre 30 días
    - Febrero quincenal: siempre 15 días  
    - Mes 31 días: máximo 30 (mensual) o 15 (quincenal)
    
        1 calcular diasnomina
        2 ajustar febrero (NUEVO)
        3 restar vacaciones
        4 restar incapacidades
        5 restar suspensiones
        6 validaciones finales

    Parameters
    ----------
    contrato : Contratos
    inicio_nomina : date
    fin_nomina : date
    tipo_nomina : int (1=mensual, 2=quincenal)
    nombre_nomina : str (para detectar segunda quincena con '#2')
    
    Returns
    -------
    int
        Días válidos en la nómina (0-30 máximo)
    """
    
    def _to_date(d):
        if d is None:
            return None
        if isinstance(d, datetime):
            return d.date()
        return d

    # Normalizar fechas
    inicio_nomina = _to_date(inicio_nomina)
    fin_nomina = _to_date(fin_nomina)
    inicio_contrato = _to_date(contrato.fechainiciocontrato)
    fin_contrato = _to_date(contrato.fechafincontrato)

    

    # Determinar si el contrato cubre toda la nómina
    contrato_vigente = (
        inicio_contrato <= inicio_nomina and
        (fin_contrato is None or fin_contrato >= fin_nomina)
    )

    max_dias = 30 if tipo_nomina == 1 else 15



    # 1. VERIFICAR SI CONTRATO ESTÁ VIGENTE EN TODO EL PERIODO
    if contrato_vigente:
        diasnomina = max_dias
    else:
        # calcular intersección
        inicio_periodo = max(inicio_nomina, inicio_contrato)
        fin_periodo = min(fin_nomina, fin_contrato or fin_nomina)

        if fin_periodo < inicio_periodo:
            return 0

        dias_reales = dias_360(inicio_periodo, fin_periodo)
        diasnomina = min(dias_reales, max_dias)

    # ==========================================
    # AJUSTE ESPECIAL: FEBRERO SEGUNDA QUINCENA
    # ==========================================
    if  inicio_nomina.month == 2:

        # si el contrato inicia dentro de esta nómina
        if inicio_contrato >= inicio_nomina and inicio_contrato <= fin_nomina and  ( inicio_nomina.day > 15 or tipo_nomina == 1 ):

            dias_febrero = calendar.monthrange(inicio_nomina.year, 2)[1]
            if dias_febrero < 30:
                ajuste = 30 - dias_febrero
                diasnomina += ajuste

    # DESCUENTOS
    dias_vacaciones = calcular_vacaciones(contrato.idcontrato, nomina)
    dias_incapacidad = calculo_incapacidad(contrato.idcontrato, nomina)
    dias_suspensiones = calcular_suspenciones(contrato.idcontrato, nomina)

    diasnomina -= dias_vacaciones
    diasnomina -= dias_incapacidad
    diasnomina -= dias_suspensiones

    # VALIDACIONES FINALES
    if diasnomina > 30:
        diasnomina = 30
    
    if diasnomina > nomina.diasnomina:
        diasnomina = nomina.diasnomina

    return max(0, diasnomina) 
        


def calcular_dias(contrato,nomina ,concep,data): 
    d = 0 
    if nomina.tiponomina.idtiponomina == 2 :
        d = calculate_biweekly_days(contrato,nomina ,concep,data)
    elif nomina.tiponomina.idtiponomina == 1 :
        d = calculate_monthly_days(contrato,nomina ,concep)
    return d


def precargar_acumulados(nomina, concep):
    data = (
        Nomina.objects
        .filter(
            idnomina__mesacumular=nomina.mesacumular,
            idnomina__anoacumular=nomina.anoacumular,
            idnomina__id_empresa=nomina.id_empresa,
            idconcepto__codigo=concep
        )
        .exclude(idnomina_id=nomina.pk)
        .values('idcontrato')
        .annotate(total=Sum('cantidad'))
    )

    return {row['idcontrato']: row['total'] or 0 for row in data}




def calculate_biweekly_days(contrato, nomina, concep,acumulados_dict):
    diasnomina2 = acumulados_dict.get(contrato.idcontrato, 0)

    print('---------------------------')
    print(concep)

    diasnomina1 = calcular_dias_en_nomina(
        contrato,
        nomina.fechainicial,
        nomina.fechafinal,
        nomina.tiponomina.idtiponomina,
        nomina
    )

    # CASO 1: YA EXISTE → NO SUMAR (ya está pago)
    if diasnomina2 > 0:
        return diasnomina1
    

    # CASO 2: NO EXISTE y es cierre → reconstruir mes
    ultimo_dia_mes = calendar.monthrange(
        nomina.fechafinal.year,
        nomina.fechafinal.month
    )[1]

    es_cierre_mes = nomina.fechafinal.day == ultimo_dia_mes



    if diasnomina2 == 0 and es_cierre_mes:
        mes_num = _mes_numero_desde_mesacumular(nomina.mesacumular)

        ano = (
            nomina.anoacumular.ano
            if nomina.anoacumular_id
            else (nomina.fechainicial.year if nomina.fechainicial else date.today().year)
        )

        if not mes_num:
            mes_num = nomina.fechainicial.month if nomina.fechainicial else 1

        inicio = date(ano, mes_num, 1)

        fin = nomina.fechainicial - timedelta(days=1)
        


        shadow = SimpleNamespace(
            fechainicial=inicio,
            fechafinal=fin,
            diasnomina=int(nomina.diasnomina),
            tiponomina=SimpleNamespace(idtiponomina=nomina.tiponomina.idtiponomina),
        )

        print('---------------------------')
        print(shadow)   
        

        
        diasnomina2 = calcular_dias_en_nomina(
            contrato,
            inicio,
            fin,
            nomina.tiponomina.idtiponomina,
            shadow
        )

    print('---------------------------')
    print(diasnomina1 , '+' , diasnomina2)
    return diasnomina1 + diasnomina2



def calculate_monthly_days(contrato, nomina, concep):
    diasnomina1 =  0

    diasnomina1 = calcular_dias_en_nomina(
        contrato,
        nomina.fechainicial,
        nomina.fechafinal,
        nomina.tiponomina.idtiponomina,
        nomina
    )

    return diasnomina1 

def return_transporte(contrato, nomina, diasnomina , sal_min, aux_tra):
    value = Decimal('0')

    if contrato.tipocontrato_id in (5, 6):
        return Decimal('0')
    if contrato.auxiliotransporte:
        return Decimal('0')
    if contrato.salario >= (sal_min * 2):
        return Decimal('0')

    total_base_trans = (
        Nomina.objects.filter(
            idcontrato=contrato,
            idnomina_id=nomina.idnomina,
            estadonomina=1,
            idconcepto__indicador__nombre='basetransporte',
        )
        .exclude(idconcepto__codigo=2)
        .aggregate(total=Sum('valor'))['total']
        or 0
    )

    if total_base_trans >= (sal_min * 2):
        return Decimal('0')
    

    if total_base_trans <= 0 and diasnomina <= 0:
        return Decimal('0')
    
    value = (
        Decimal(diasnomina) * (Decimal(str(aux_tra)) / Decimal('30'))
    ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

    return value