from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Crearnomina , Contratos,NovFijos , EditHistory ,Incapacidades, Conceptosfijos ,Costos,Salariominimoanual, Crearnomina ,EmpVacaciones,Prestamos ,Conceptosdenomina , Empresa , Vacaciones , Nomina , Contratos
from django.contrib import messages
from django.db import transaction, models
from datetime import datetime
from django.db.models import Sum , Q
from datetime import timedelta
from apps.components.humani import format_value
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, timedelta


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
        4: 'Reinicio de Nómina'
    }

    titulo = titles.get(type_payroll, 'Sistemas Automáticos')
    centros = Costos.objects.filter(id_empresa_id=idempresa)
    empleados = Contratos.objects.filter(estadocontrato=1, id_empresa=idempresa).order_by('idempleado__papellido')
    
    
    
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
        else:
            messages.error(request, "Error #13 al procesar la nómina.")
            return redirect('payroll:payrollview', id=idnomina)

    
    return render(request, 'payroll/partials/payroll_automatic_systems.html', {'titulo': titulo,'empleados':empleados, 'centros': centros, 'type_payroll': type_payroll , 'idnomina':idnomina})





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


def calcular_dias_nomina(idn):
    try:
        nomina = Crearnomina.objects.get(idnomina=idn)
    except Crearnomina.DoesNotExist:
        return "Error: nómina no encontrada"

    fecha_inicio_nomina = nomina.fechainicial
    fecha_fin_nomina = nomina.fechafinal

    # Contratos vigentes según fechas
    contratos_vigentes = Contratos.objects.filter(
        Q(fechainiciocontrato__lte=fecha_fin_nomina) &
        (Q(fechafincontrato__isnull=True) | Q(fechafincontrato__gte=fecha_inicio_nomina)) &
        Q(id_empresa=nomina.id_empresa)
    )

    # Excluir contratos liquidados o retirados antes del inicio de la nómina
    contratos_excluir = contratos_vigentes.filter(
        Q(estadoliquidacion='1') | Q(estadoliquidacion='2'),
        fechafincontrato__lt=fecha_inicio_nomina
    )

    contratos_finales = contratos_vigentes.exclude(
        idcontrato__in=contratos_excluir.values_list('idcontrato', flat=True)
    )

    resultado = {}

    for contrato in contratos_finales:
        # Fecha inicial efectiva
        inicio = max(contrato.fechainiciocontrato, fecha_inicio_nomina)
        # Fecha final efectiva
        fin = contrato.fechafincontrato if contrato.fechafincontrato else fecha_fin_nomina
        fin = min(fin, fecha_fin_nomina)

        # Días dentro de la nómina
        dias = (fin - inicio).days + 1
        resultado[contrato.idcontrato] = dias

    return resultado

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

    contratos = Contratos.objects.filter(estadoliquidacion=3, id_empresa =  idempresa ) 
    

    if parte_nomina != 0:
        contratos = contratos.filter(idcosto=parte_nomina)

    if empleados: 
        contratos = contratos.filter(idcontrato__in = empleados)

    for contrato in contratos:
        
        # --- opcional: normalizar a date si hubiera datetimes ---
        def _to_date(d):
            if d is None:
                return None
            if isinstance(d, datetime):
                return d.date()
            return d

        inicio_nomina = _to_date(nomina.fechainicial)
        fin_nomina = _to_date(nomina.fechafinal)
        inicio_contrato = _to_date(contrato.fechainiciocontrato)
        fin_contrato = _to_date(contrato.fechafincontrato) or fin_nomina

        # --- calcular intersección del intervalo [inicio_nomina, fin_nomina] con [inicio_contrato, fin_contrato]
        diasnomina = nomina.diasnomina
        inicio_periodo = max(inicio_nomina, inicio_contrato)
        fin_periodo = min(fin_nomina, fin_contrato)
        
        
        if fin_periodo < inicio_periodo:
            diasnomina = 0
        else:
            
            if nomina.tiponomina.idtiponomina == 1 :
    
                # días calculados por Python (sin incluir el día final)
                dias_base = (fin_periodo - inicio_periodo).days

                # determinar días del mes del fin_periodo
                mes = fin_periodo.month
                ano = fin_periodo.year
                
                if mes == 12:
                    dias_en_mes = 31
                else:
                    dias_en_mes = (date(ano, mes + 1, 1) - timedelta(days=1)).day

                if dias_en_mes == 31:
                    diasnomina = dias_base 
                else:
                    diasnomina = dias_base + 1
            elif nomina.tiponomina.idtiponomina == 2 :
                nombre_original = nomina.nombrenomina or ""
                if '#2' in nombre_original:
                    diasnomina = (fin_periodo - inicio_periodo).days  
                else : 
                    diasnomina = (fin_periodo - inicio_periodo).days + 1 
                

        dias_vacaciones = calcular_vacaciones(contrato.idcontrato,nomina)
        dias_incapacidad = calculo_incapacidad(contrato.idcontrato,nomina)
        dias_suspensiones = calcular_suspenciones(contrato.idcontrato,nomina)
        
        
        # if contrato.idcontrato == 7991:
        #     print(f" v {dias_vacaciones} I {dias_incapacidad} S {dias_suspensiones}")
        
        
        d = diasnomina
        
        diasnomina -= dias_vacaciones 
        diasnomina -= dias_incapacidad 
        diasnomina -= dias_suspensiones 

        
        calculo_prestamo(contrato, idn)
        #Calculo_vacaciones(contrato, idn)
        calculo_novfija(contrato, idn)
        
        if contrato.tiposalario.idtiposalario == 2:
            codigo_aux = '4'
        elif contrato.tipocontrato_id == 6:
            codigo_aux = '34'
        else:
            codigo_aux = '1'
            
            
        concepto = Conceptosdenomina.objects.get(codigo=codigo_aux, id_empresa_id = idempresa)
        
        if diasnomina > 0:
            
            if diasnomina > 30:
                diasnomina = 30
                
            
            if diasnomina > nomina.diasnomina :
                diasnomina = nomina.diasnomina
        

            valorsalario = (contrato.salario / 30) * diasnomina

            
        
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
        
    if empleados: 
        contratos = contratos.filter(idcontrato__in = empleados)
        
        
    nomina = Crearnomina.objects.get(idnomina=idn)
    inicio_nomina, fin_nomina = nomina.fechainicial, nomina.fechafinal
    ano = nomina.anoacumular.ano 
    
    salario_minimo = Salariominimoanual.objects.get( ano = ano ).salariominimo
    pago_incapacidad = Empresa.objects.get(idempresa=1).ige100 or "NO"
    
    contratos = Contratos.objects.filter(estadoliquidacion=3, id_empresa =  idempresa)
    
    if parte_nomina != 0:
        contratos = contratos.filter(idcosto = parte_nomina)
    
    incapacidades = Incapacidades.objects.filter(idcontrato__id_empresa =  idempresa, idcontrato__estadoliquidacion=3)
    
    
    
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
            dias_asumidos = 0
        
        
        
        dias_incapacidad -= dias_asumidos

        
        horas_incapacidad = dias_incapacidad * 8
        valor_incapacidad = ibc / 240 * horas_incapacidad
        horas_asumidas = dias_asumidos * 8
        valor_asumido = ibc / 240 * horas_asumidas
        
        
        
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

    contratos = Contratos.objects.filter(estadocontrato=1, id_empresa =  idempresa)
    if parte_nomina != 0:
        contratos = contratos.filter(idcosto = parte_nomina)
    
    if empleados: 
        contratos = contratos.filter(idcontrato__in = empleados)
    
    for contrato in contratos:
        
        salario_emp = contrato.salario
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
        
        
        from decimal import Decimal

        base_ss_fsp2 = base_ss_fsp * Decimal('0.7')

        
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
            
            if (base_ss > (sal_min * 4)) and (base_ss < (sal_min * 16)):
                FSP = fsp416
            elif (base_ss > (sal_min * 16)) and (base_ss < (sal_min * 17)):
                FSP = fsp1617
            elif (base_ss > (sal_min * 17)) and (base_ss < (sal_min * 18)):
                FSP = fsp1718
            elif (base_ss > (sal_min * 18)) and (base_ss < (sal_min * 19)):
                FSP = fsp1819
            elif (base_ss > (sal_min * 19)) and (base_ss < (sal_min * 20)):
                FSP = fsp1920
            elif base_ss > (sal_min * 20):
                FSP = fsp21
            else:
                FSP = 0
            
            
            
            
            valoreps = round((total_base_ss * EPS.valorfijo) / 100, 2)
            valorafp = round((total_base_ss * AFP.valorfijo) / 100, 2)
            valorfsp = round((base_ss_fsp2 * FSP) / 100, 2) if base_ss_fsp2 >= (sal_min * 4) else 0.00
            
        

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
                    aux_pass.valor = -1*valorafp
                    aux_pass.save() 
                                
            else:


                Nomina.objects.create(
                        idconcepto = concepto2 ,#*
                        cantidad= 0 ,#*
                        estadonomina = 1,
                        valor=-1*valorafp , #*
                        idcontrato_id=contrato.idcontrato ,
                        idnomina_id = idn ,
                    ) 
            
            
            
            if valorfsp > 0:
                valorfsp = valorfsp / 2 
                # round((base_ss_fsp * FSP) / 100, 2) if base_ss_fsp >= (sal_min * 4) else 0.00 
                
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
                        aux_pass.valor = -1*valorfsp
                        aux_pass.save() 
                                    
                else:
                    Nomina.objects.create(
                            idconcepto = concepto3 ,#*
                            cantidad= 0 ,#*
                            estadonomina = 1,
                            valor=-1*valorfsp , #*
                            idcontrato_id=contrato.idcontrato ,
                            idnomina_id = idn ,
                        ) 
                    
    return True



def procesar_nomina_transporte(idn, parte_nomina,idempresa,empleados):
    """
    Procesa el auxilio de transporte para los contratos activos dentro de una nómina.

    Esta función calcula y registra el valor correspondiente al auxilio de transporte, 
    teniendo en cuenta si el empleado tiene derecho a este beneficio según su salario 
    y condiciones del contrato. El valor es proporcional a los días efectivamente laborados, 
    excluyendo vacaciones e incapacidades.

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
    - Solo se liquida el auxilio si el salario es igual o inferior a dos salarios mínimos y 
        si el contrato tiene activado el beneficio (`auxiliotransporte`).
    - No se liquida auxilio durante días de vacaciones o incapacidades.
    - El cálculo es proporcional a los días efectivamente laborados, con un tope de 30 días.
    - Si ya existe un registro del auxilio y no ha sido editado, se actualiza; si no, se crea uno nuevo.
    - El concepto usado para registrar el auxilio tiene código `2`.
    - Se excluyen conceptos específicos con indicador 25 para calcular la base del auxilio.
    """


    if not parte_nomina:
        parte_nomina = 0

    contratos = Contratos.objects.filter(estadocontrato=1, id_empresa =  idempresa)

    if parte_nomina != 0:
        contratos = contratos.filter(idcosto = parte_nomina)

    if empleados: 
        contratos = contratos.filter(idcontrato__in = empleados)
        
    try:
        nomina = Crearnomina.objects.get(idnomina=idn)
    except Crearnomina.DoesNotExist:
        return "Error de creación de nómina"
    
    sal_min = Salariominimoanual.objects.get(ano = nomina.anoacumular.ano).salariominimo
    aux_tra = Salariominimoanual.objects.get(ano = nomina.anoacumular.ano).auxtransporte
    
    for contrato in contratos:
        # --- opcional: normalizar a date si hubiera datetimes ---
        def _to_date(d):
            if d is None:
                return None
            if isinstance(d, datetime):
                return d.date()
            return d

        nombre_original = nomina.nombrenomina or ""
        print(nombre_original)
        
        #passs = nomina.
        existe = Nomina.objects.filter(
            idnomina__mesacumular=nomina.mesacumular,
            idnomina__id_empresa=nomina.id_empresa,
            idcontrato=contrato,
            idconcepto__codigo = 2
        ).exists()
        
        

        # Solo entra si NO existe el concepto en esa nómina
        if not existe and '#2' in nombre_original:
            
            nuevo_nombre = nombre_original.replace('#2', '#1')
            

            nomina2 = Crearnomina.objects.filter(nombrenomina = nuevo_nombre).first()
            diasnomina2 = nomina2.diasnomina
            
            inicio_nomina2 = _to_date(nomina2.fechainicial)
            fin_nomina2 = _to_date(nomina2.fechafinal)
            inicio_contrato2 = _to_date(contrato.fechainiciocontrato)
            fin_contrato2 = _to_date(contrato.fechafincontrato) or fin_nomina2
            
            inicio_periodo2 = max(inicio_nomina2, inicio_contrato2)
            fin_periodo2 = min(fin_nomina2, fin_contrato2)
            
            
            if fin_periodo2 < inicio_periodo2:
                diasnomina2 = 0
            else:
                diasnomina2 = (fin_periodo2 - inicio_periodo2).days + 1 

                if diasnomina2 > nomina2.diasnomina :
                    diasnomina2 = nomina2.diasnomina

            dias_vacaciones = calcular_vacaciones(contrato,nomina2)
            dias_incapacidad = calculo_incapacidad(contrato,nomina2)
            dias_suspensiones = calcular_suspenciones(contrato,nomina2)
            
            diasnomina2 -= dias_vacaciones 
            diasnomina2 -= dias_incapacidad 
            diasnomina2 -= dias_suspensiones 

        else :
            diasnomina2 = 0


        inicio_nomina = _to_date(nomina.fechainicial)
        fin_nomina = _to_date(nomina.fechafinal)
        inicio_contrato = _to_date(contrato.fechainiciocontrato)
        fin_contrato = _to_date(contrato.fechafincontrato) or fin_nomina

        # --- calcular intersección del intervalo [inicio_nomina, fin_nomina] con [inicio_contrato, fin_contrato]
        diasnomina1 = nomina.diasnomina
        inicio_periodo = max(inicio_nomina, inicio_contrato)
        fin_periodo = min(fin_nomina, fin_contrato)
        
        
        if fin_periodo < inicio_periodo:
            diasnomina1 = 0
        else:
            
            if nomina.tiponomina.idtiponomina == 1 :
                dias_base = (fin_periodo - inicio_periodo).days
                mes = fin_periodo.month
                ano = fin_periodo.year
                
                if mes == 12:
                    dias_en_mes = 31
                else:
                    dias_en_mes = (date(ano, mes + 1, 1) - timedelta(days=1)).day

                if dias_en_mes == 31:
                    diasnomina1 = dias_base + 2
                else:
                    diasnomina1 = dias_base + 1
                    
            elif nomina.tiponomina.idtiponomina == 2 :
                nombre_original = nomina.nombrenomina or ""
                if '#2' in nombre_original:
                    mes = fin_periodo.month
                    ano = fin_periodo.year
                    
                    if mes == 12:
                        dias_en_mes = 31
                    else:
                        dias_en_mes = (date(ano, mes + 1, 1) - timedelta(days=1)).day

                    if dias_en_mes == 31:
                        diasnomina1 = (fin_periodo - inicio_periodo).days 
                    else:
                        diasnomina1 = (fin_periodo - inicio_periodo).days  + 1 
                else : 
                    diasnomina1 = (fin_periodo - inicio_periodo).days + 1 

        
        
        diasnomina =  diasnomina1 + diasnomina2
        
        
        
        # --- tope de 30 días (y si quieres, también tope por nomina.diasnomina) ---
        if diasnomina > 30:
            diasnomina = 30

        dias_vacaciones = calcular_vacaciones(contrato,nomina)
        dias_incapacidad = calculo_incapacidad(contrato,nomina)
        dias_suspensiones = calcular_suspenciones(contrato,nomina)
        
        
        diasnomina -= dias_vacaciones 
        diasnomina -= dias_incapacidad 
        diasnomina -= dias_suspensiones 
        

        if contrato.auxiliotransporte :
            transporte = 0
            diasnomina = 0
                
        if contrato.salario <= (sal_min * 2):
            # Obtener la suma de las deducciones de la eps 
            total_base_trans = Nomina.objects.filter(
                idcontrato=contrato,
                idnomina_id=idn,
                estadonomina = 1 ,
                idconcepto__indicador__nombre='basetransporte'  
            ).exclude(
                idconcepto__codigo=2
            ).distinct().aggregate(total=Sum('valor'))['total'] or 0# Reemplaza 'monto' con el nombre correcto de la columna
            
                        
            if total_base_trans < (sal_min * 2):
                transporte = diasnomina * (aux_tra / 30)
            else:
                transporte = 0
                diasnomina = 0
        
            concepto = Conceptosdenomina.objects.get(codigo= 2 , id_empresa_id = idempresa)
            
            
            if contrato.tipocontrato.idtipocontrato not in [5, 6]:
                
                if diasnomina > 0 and transporte > 0 :
                    
                    if diasnomina > 30:
                        diasnomina = 30
                    
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
                            aux_pass.valor = transporte
                            aux_pass.save()                  
                    else:
                        
                        
                        Nomina.objects.create(
                            idconcepto = concepto ,#*
                            cantidad=diasnomina ,#*
                            valor=transporte , #*
                            estadonomina = 1,
                            idcontrato_id=contrato.idcontrato ,
                            idnomina_id = idn ,
                        )  
    return True
        

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
    dias_vacaciones = 0

    vacaciones = Vacaciones.objects.filter(
        idcontrato_id=contrato,
        tipovac__idvac=1
    )
    
    
    # Si el contrato no tiene vacaciones legales registradas → 0
    if not vacaciones.exists():
        return 0
    
    for vac in vacaciones:
        
        if not vac.fechainicialvac or not vac.ultimodiavac:
            continue

        # Validar cruce con la nómina
        if vac.fechainicialvac <= nomina.fechafinal and vac.ultimodiavac >= nomina.fechainicial:
            inicio_cruce = max(vac.fechainicialvac, nomina.fechainicial)
            fin_cruce = min(vac.ultimodiavac, nomina.fechafinal)

            # 🔹 Cálculo exacto de días calendario dentro de la nómina
            dias_en_nomina = (fin_cruce - inicio_cruce).days + 1

            # No sumar el día inicial (según norma nómina)
            dias_vacaciones += dias_en_nomina

            # Debug opcional
            if nomina.fechafinal.day == 30:
                dias_vacaciones -= 1
                
    return dias_vacaciones




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

    # 🔹 Filtrar solo vacaciones legales (ajustar si Tipoavacaus usa 'codigo' en lugar de 'id')
    vacaciones = Vacaciones.objects.filter(idcontrato_id=contrato, tipovac__idvac__in=[3,4,5])

    for vac in vacaciones:
        # Solo si hay cruce entre vacaciones y periodo de nómina
        if vac.fechainicialvac and vac.ultimodiavac:
            if vac.fechainicialvac <= nomina.fechafinal and vac.ultimodiavac >= nomina.fechainicial:
                inicio = max(vac.fechainicialvac, nomina.fechainicial)
                fin = min(vac.ultimodiavac, nomina.fechafinal)
                dias_vacaciones += (fin - inicio).days + 1

    return dias_vacaciones 




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

    return dias_incapacidad




def Calculo_vacaciones(contrato, idn):
    
    # Conceptos asociados
    conp_vaca_dis = Conceptosdenomina.objects.get(codigo=24, id_empresa=contrato.id_empresa_id)
    conp_vaca_con = Conceptosdenomina.objects.get(codigo=32, id_empresa=contrato.id_empresa_id)

    # Nómina actual
    nomina_actual = Crearnomina.objects.get(idnomina=idn)

    # Vacaciones según tipo
    vacaciones_dis = Vacaciones.objects.filter(idcontrato=contrato, tipovac__idvac=1)
    vacaciones_con = Vacaciones.objects.filter(idcontrato=contrato, tipovac__idvac=2)

    def procesar_vacaciones(vacaciones, concepto, tipo):
        for vaca in vacaciones:
            existe = Nomina.objects.filter(
                idnomina=idn,
                idconcepto=concepto,
                control=vaca.idvacaciones
            ).exists()

            if existe:
                print(f'Vacación {vaca.idvacaciones} ya está en la nómina.')
                continue

            # 🟦 Tipo 1: Vacaciones disfrutadas → se comparan fechas de disfrute
            if tipo == 1 and vaca.fechainicialvac and vaca.ultimodiavac:
                if vaca.fechainicialvac <= nomina_actual.fechafinal and vaca.ultimodiavac >= nomina_actual.fechainicial:
                    inicio = max(vaca.fechainicialvac, nomina_actual.fechainicial)
                    fin = min(vaca.ultimodiavac, nomina_actual.fechafinal)
                    dias_vacaciones = (fin - inicio).days + 1
                    valor = (contrato.salario / 30) * dias_vacaciones
                    cantidad = calcular_vacaciones(contrato,nomina_actual)
                else:
                    print(f'Vacación {vaca.idvacaciones} fuera del rango de nómina.')
                    continue

            # 🟩 Tipo 2: Vacaciones compensadas → se usan fecha de pago y días pagados
            elif tipo == 2 and vaca.fechapago:
                if nomina_actual.fechainicial <= vaca.fechapago <= nomina_actual.fechafinal:
                    dias_vacaciones = vaca.diasvac or 0
                    base = vaca.basepago or contrato.salario
                    valor = (base / 30) * dias_vacaciones
                    cantidad = 1
                    # Si el pago ya está registrado como valor fijo
                    if vaca.pagovac:
                        valor = vaca.pagovac
                else:
                    print(f'Vacación {vaca.idvacaciones} (tipo 2) con fecha de pago fuera del rango de nómina.')
                    continue

            else:
                print(f'Vacación {vaca.idvacaciones} sin datos válidos.')
                continue

            # Crear registro en la nómina
            Nomina.objects.create(
                idconcepto=concepto,
                cantidad= cantidad,
                estadonomina=1,
                valor=valor,
                idcontrato=contrato,
                idnomina_id=idn,
                control=vaca.idvacaciones
            )

            print(f'Vacación {vaca.idvacaciones} registrada en nómina con valor {valor}')

    # Procesar vacaciones disfrutadas (tipo 1)
    procesar_vacaciones(vacaciones_dis, conp_vaca_dis, tipo=1)

    # Procesar vacaciones compensadas (tipo 2)
    procesar_vacaciones(vacaciones_con, conp_vaca_con, tipo=2)
    




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
        # 🚨 VALIDACIÓN CLAVE:
        # Ejecutar solo si el préstamo se creó ANTES o el MISMO día
        # ---------------------------------------------------------
        if load.fechaprestamo is None:
            continue  # Si no tiene fecha, lo ignoramos para evitar errores

        if load.fechaprestamo > nomina_actual.fechainicial:
            continue  # Este préstamo no aplica a esta nómina

        # Verificar si ya está registrado en la nómina actual
        nominactual = Nomina.objects.filter(
            idnomina=idn,
            idconcepto=conceptosdenomina,
            control=load.idprestamo
        ).exists()

        # Deducciones anteriores de este préstamo
        deducciones = Nomina.objects.filter(
            idconcepto=conceptosdenomina,
            control=load.idprestamo
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

            # Lógica de fecha fin de novedad
            if nov.fechafinnovedad:
                # Si la fecha fin cae dentro del periodo de la nómina => cantidad 0
                if nomina.fechainicial <= nov.fechafinnovedad <= nomina.fechafinal:
                    cantidad = 0
                else:
                    # Si la fecha fin ya pasó (o no está en el periodo) marcamos la novedad como inactiva
                    # (según tu lógica previa)
                    nov.estado_novfija = False
                    nov.save()

            

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



