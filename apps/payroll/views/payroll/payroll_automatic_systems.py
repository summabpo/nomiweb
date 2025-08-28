from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Crearnomina , Contratos,NovFijos , EditHistory ,Incapacidades, Conceptosfijos ,Costos,Salariominimoanual, Crearnomina ,EmpVacaciones,Prestamos ,Conceptosdenomina , Empresa , Vacaciones , Nomina , Contratos
from django.contrib import messages
from django.db import transaction, models
from datetime import datetime
from django.db.models import Sum
from datetime import timedelta



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
            if procesar_nomina_reset(idnomina, ne, idempresa,empleados_ids):
                messages.success(request, "Reinicio de nómina realizado correctamente.")
                return redirect('payroll:payrollview', id=idnomina)
            else:
                messages.error(request, "Error al procesar el reinicio de la nómina.")
                return redirect('payroll:payrollview', id=idnomina)
        else:
            messages.error(request, "Error #13 al procesar la nómina.")
            return redirect('payroll:payrollview', id=idnomina)

    
    return render(request, 'payroll/partials/payroll_automatic_systems.html', {'titulo': titulo,'empleados':empleados, 'centros': centros, 'type_payroll': type_payroll , 'idnomina':idnomina})


def procesar_nomina_reset(idn, parte_nomina,idempresa,empleados):
    
    data_nomina = Nomina.objects.filter(
            idnomina_id=idn
        )
    for data in data_nomina:
        data.estadonomina = 2
        data.save()
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
    
    if not parte_nomina:
        parte_nomina = 0

    contratos = Contratos.objects.filter(estadoliquidacion=3, id_empresa =  idempresa) 
    
    if parte_nomina != 0:
        contratos = contratos.filter(idcosto=parte_nomina)

    if empleados: 
        contratos = contratos.filter(idcontrato__in = empleados)
        
    
    try:
        nomina = Crearnomina.objects.get(idnomina=idn)
    except Crearnomina.DoesNotExist:
        return "Error de creación de nómina"
    for contrato in contratos:
        diasnomina = nomina.diasnomina
        if contrato.fechainiciocontrato > nomina.fechafinal:
            diasnomina = (nomina.fechafinal - contrato.fechainiciocontrato).days + 1

        if contrato.fechafincontrato and nomina.fechafinal <= contrato.fechafincontrato <= nomina.fechafinal:
            diasnomina -= (nomina.fechafinal - contrato.fechafincontrato).days
            
            
        dias_vacaciones = calcular_vacaciones(contrato,nomina)
        dias_incapacidad = calculo_incapacidad(contrato, idn)
        diasnomina -= dias_vacaciones 
        diasnomina -= dias_incapacidad 
        
        
        calculo_prestamo(contrato, idn)
        calculo_novfija(contrato, idn)
        
        if contrato.tiposalario_id == 2:
            codigo_aux = '4'
        elif contrato.tipocontrato_id in [5, 6]:
            codigo_aux = '34'
        else:
            codigo_aux = '1'
            
            
        concepto = Conceptosdenomina.objects.get(codigo=codigo_aux, id_empresa_id = idempresa)
        
        if diasnomina > 0:
            if diasnomina > 30:
                diasnomina = 30
                
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
    
    incapacidades = Incapacidades.objects.filter(idcontrato__id_empresa =  idempresa, fechainicial__range=(inicio_nomina, fin_nomina) )
    
    
    if parte_nomina != 0:
        incapacidades = incapacidades.filter(idcontrato__idcosto = parte_nomina)
    
    for incapacidad in incapacidades:
        
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
            dias_incapacidad = (fin_nomina - inicio_nomina).days + 1
        elif ini <= inicio_nomina <= fin_nomina <= fin:
            dias_incapacidad = (fin_nomina - inicio_nomina).days + 1
        elif inicio_nomina <= ini <= fin <= fin_nomina:
            dias_incapacidad = (fin - ini).days + 1
        elif ini >= inicio_nomina and fin >= fin_nomina:
            dias_incapacidad = (fin_nomina - ini).days + 1
        else:
            dias_incapacidad = 0

        #Calculo del IBC
        if pago_incapacidad == "NO":
            ibc = round(ibc * 2 / 3, 0)
            
        if ibc < salario_minimo:
            ibc = salario_minimo
        
        #Tipo de incapacidad
        if tipo == 'EPS1':
            idconceptoi = Conceptosdenomina.objects.get(codigo=25, id_empresa_id = idempresa)
            idconceptoa = Conceptosdenomina.objects.get(codigo=26, id_empresa_id = idempresa) 
            
        elif tipo == 'ARL':
            
            dias_asumidos = dia_asumido_1
            ibc = incapacidad.ibc
            
            idconceptoi = Conceptosdenomina.objects.get(codigo=27, id_empresa_id = idempresa)
            idconceptoa = Conceptosdenomina.objects.get(codigo=28, id_empresa_id = idempresa) 
            
        elif tipo == 'EPS2':
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
        
        ## division de conceptos     
        

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
                print(aux_pass)
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
            idconcepto__indicador__nombre='basesegsocial'
        ).exclude(
            idconcepto__codigo__in=[60, 70, 90] # Excluir conceptos cuyo código sea el de EPS
        ).aggregate(total=Sum('valor'))['total'] or 0  # Reemplaza 'monto' con el nombre correcto de la columna
                
            
        if total_base_ss > 0:
            
            concepto1 = Conceptosdenomina.objects.get(codigo = 60 , id_empresa_id = idempresa)
            concepto2 = Conceptosdenomina.objects.get(codigo = 70 , id_empresa_id = idempresa)
            concepto3 = Conceptosdenomina.objects.get(codigo = 90 , id_empresa_id = idempresa)
            
            base_max = sal_min * tope_ibc.valorfijo
        
            if tipo_salario == 2 :
                total_base_ss *= (factor_integral / 100)
            
                
            base_ss = min(total_base_ss, base_max)
            
            
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
                

            
            valoreps = (total_base_ss * EPS.valorfijo ) / 100
            valorafp = (total_base_ss * AFP.valorfijo ) / 100
            valorfsp = (total_base_ss * FSP) / 100 if total_base_ss >= (sal_min * 4) else 0
            
            
            if contrato.pensionado == '2':
                valorafp = 0
                valorfsp = 0
            
            
            # Crear o actualizar el registro de la EPS
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
        
        diasnomina = nomina.diasnomina
    
        if contrato.fechainiciocontrato > nomina.fechafinal:
            diasnomina = (nomina.fechafinal - contrato.fechainiciocontrato).days + 1
        
        if contrato.fechafincontrato and nomina.fechafinal <= contrato.fechafincontrato <= nomina.fechafinal:
            diasnomina -= (nomina.fechafinal - contrato.fechafincontrato).days
            
        dias_vacaciones = calcular_vacaciones(contrato,nomina)
        dias_incapacidad = calculo_incapacidad(contrato, idn)

        diasnomina -= dias_vacaciones 
        diasnomina -= dias_incapacidad 
        
        
        horas_basico_mes = Nomina.objects.filter(idconcepto__codigo = 1, idcontrato=contrato.idcontrato, 
                                                 idnomina__mesacumular = nomina.mesacumular , idnomina__anoacumular = nomina.anoacumular ,
                                                 estadonomina=2).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        
        horas_basico_quincena = Nomina.objects.filter(idconcepto=1, idcontrato=contrato.idcontrato, 
                                                       idnomina_id=idn).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        
        
        
        total_mes = horas_basico_mes + horas_basico_quincena

        
        
        if not contrato.auxiliotransporte :
            transporte = 0
            diasnomina = 0
                
        elif contrato.salario <= (sal_min * 2):
            # Obtener la suma de las deducciones de la eps 
            total_base_trans = Nomina.objects.filter(
                idcontrato=contrato,
                idnomina_id=idn,
                idconcepto__indicador__nombre='auxtransporte'  
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
        

def calcular_vacaciones(contrato,nomina ):
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
    vacaciones = EmpVacaciones.objects.filter(idcontrato=contrato ,estado = 2 ,tipovac='1' )
    for vac in vacaciones:
        data = Vacaciones.objects.filter(idcontrato=contrato, tipovac='1', idvacmaster = vac.id_sol_vac).first() 
        if data:
            if data.fechainicialvac <= nomina.fechafinal and data.ultimodiavac >= nomina.fechainicial:
                inicio = max(data.fechainicialvac, nomina.fechainicial)
                fin = min(data.ultimodiavac, nomina.fechafinal)
                dias_vacaciones = (fin - inicio).days + 1
        else:
            dias_vacaciones = 0
    return dias_vacaciones




def calculo_incapacidad(contrato, idn ):   
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
    
    dias_incapacidad_tempo = Nomina.objects.filter(
        idnomina=idn,
        idcontrato=contrato,
        idconcepto__codigo__in=[25, 26, 27, 28, 29]
    ).aggregate(total_dias_incapacidad=Sum('cantidad'))['total_dias_incapacidad']
    
    
    if dias_incapacidad_tempo:
        dias_incapacidad = dias_incapacidad_tempo
    
    return int(dias_incapacidad)





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

    loans = Prestamos.objects.filter(idcontrato=contrato , estadoprestamo = True ).order_by('-idprestamo')
    conceptosdenomina = Conceptosdenomina.objects.get(codigo = 50 , id_empresa = contrato.id_empresa_id)
    
    
    
    for load in loans:
        nominactual = Nomina.objects.filter(idnomina=idn , idconcepto=conceptosdenomina,control=load.idprestamo).exists()
        # Obtener deducciones de nómina relacionadas al préstamo
        deducciones = Nomina.objects.filter(
            idconcepto=conceptosdenomina,  # Asegúrate que este es el id correcto para "deducción de préstamo"
            control=load.idprestamo
        ).order_by('-idnomina') 
        
        # Obtener la suma de las deducciones del préstamo
        suma_deducciones = Nomina.objects.filter(
            idconcepto=conceptosdenomina,
            control=load.idprestamo
        ).aggregate(total=Sum('valor'))['total'] or 0  # Reemplaza 'monto' con el nombre correcto de la columna

        
        if deducciones :
            if not nominactual : 
                
                if (load.valorprestamo + suma_deducciones ) > load.valorcuota :
                    valor = load.valorprestamo / load.cuotasprestamo
                else :
                    valor = load.valorprestamo + suma_deducciones
                
                Nomina.objects.create(
                    idconcepto = conceptosdenomina ,
                    cantidad = 1,
                    estadonomina = 1,
                    valor = -1*valor,
                    idcontrato = contrato,
                    idnomina_id = idn,
                    control = load.idprestamo
                )
                
        else:
            valor = load.valorprestamo / load.cuotasprestamo

            Nomina.objects.create(
                idconcepto = conceptosdenomina ,
                cantidad = 1,
                valor = -1*valor,
                estadonomina = 1,
                idcontrato = contrato,
                idnomina_id = idn,
                control = load.idprestamo
            )
    
    
    
def calculo_novfija(contrato, idn):
    """
    Procesa las novedades fijas activas para un contrato en la nómina actual.

    Esta función verifica si una novedad fija ya ha sido registrada en la nómina. 
    Si no lo ha sido, la registra con su valor correspondiente. Si la novedad tiene fecha de finalización 
    dentro del período de la nómina, se registra con cantidad cero y se marca como inactiva.

    Parameters
    ----------
    contrato : Contratos
        Objeto de contrato al que se aplican las novedades fijas.

    idn : int
        ID de la nómina actual en la que se deben registrar las novedades.

    See Also
    --------
    NovFijos : Modelo que contiene las novedades fijas asociadas a un contrato.
    Conceptosdenomina : Catálogo de conceptos de nómina.
    Nomina : Modelo donde se registran las novedades.
    """

    nomina = Crearnomina.objects.get(pk=idn)
    novs = NovFijos.objects.filter(idcontrato=contrato, estado_novfija=True).order_by('-idnovfija')

    for nov in novs:
        if Nomina.objects.filter(idnomina=idn, idconcepto=nov.idconcepto, control=nov.idnovfija).exists():
            continue  # Ya existe, saltar

        cantidad = 1  # Valor por defecto
        crear = False

        if nov.fechafinnovedad:
            if nomina.fechainicial <= nov.fechafinnovedad <= nomina.fechafinal:
                cantidad = 0
                crear = True
            else:
                crear = True
                nov.estado_novfija = False
                nov.save()
        else:
            crear = True
            nov.estado_novfija = False
            nov.save()

        if crear:
            Nomina.objects.create(
                idconcepto=nov.idconcepto,
                cantidad=cantidad,
                valor=nov.valor,
                estadonomina = 1,
                idcontrato=contrato,
                idnomina_id=idn,
                control=nov.idnovfija
            )
