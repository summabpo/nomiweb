

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Crearnomina , Contratos,NovFijos , EditHistory ,Incapacidades, Conceptosfijos ,Costos,Salariominimoanual, Crearnomina ,EmpVacaciones,Prestamos ,Conceptosdenomina , Empresa , Vacaciones , Nomina , Contratos
from django.contrib import messages
from django.db import transaction, models
from datetime import datetime
from django.db.models import Sum
from datetime import timedelta
from apps.components.humani import format_value
from django.http import JsonResponse 
from apps.payroll.views.payroll.payroll_automatic_systems import *


@login_required
@role_required('accountant')
def automatic_systems_2(request, type_payroll=0, idnomina=0 , idcontrato = 0):
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    conceptos_data = []
    
    # basic_payroll(idcontrato ,idempresa, idnomina)
    if type_payroll == 0:
        if basic_payroll(idcontrato, idempresa, idnomina):    
            data = data_visua(idcontrato ,idempresa, idnomina)
            return JsonResponse({'message': 'Datos recibidos correctamente', 'data': data})
        else :
            messages.error(request, "Error al procesar la nómina")
            return redirect('payroll:payrollview', id=idnomina)
    elif type_payroll == 1:
        if incapacidad_payroll(idcontrato, idempresa, idnomina): 
            data = data_visua(idcontrato ,idempresa, idnomina)
            return JsonResponse({'message': 'Datos recibidos correctamente', 'data': data})
        else :
            messages.error(request, "Error al procesar la nómina")
            return redirect('payroll:payrollview', id=idnomina)
    elif type_payroll == 2:
        if aportes_payroll(idcontrato, idempresa, idnomina): 
            data = data_visua(idcontrato ,idempresa, idnomina)
            return JsonResponse({'message': 'Datos recibidos correctamente', 'data': data})
        else :
            messages.error(request, "Error al procesar la nómina")
            return redirect('payroll:payrollview', id=idnomina)
    elif type_payroll == 3:
        if transporte_payroll(idcontrato, idempresa, idnomina): 
            data = data_visua(idcontrato ,idempresa, idnomina)
            return JsonResponse({'message': 'Datos recibidos correctamente', 'data': data})
        else :
            messages.error(request, "Error al procesar la nómina")
            return redirect('payroll:payrollview', id=idnomina)
    
    return render(request, 'payroll/partials/payroll_automatic_systems_2.html')



def basic_payroll(idcontrato ,idempresa, idnomina):
    
    try:
        nomina = Crearnomina.objects.get(idnomina=idnomina)
    except Crearnomina.DoesNotExist:
        return "Error de creación de nómina"
    
    contrato = Contratos.objects.get(idcontrato = idcontrato) 
    
    diasnomina = nomina.diasnomina
    if contrato.fechainiciocontrato > nomina.fechafinal:
        diasnomina = (nomina.fechafinal - contrato.fechainiciocontrato).days + 1

    if contrato.fechafincontrato and nomina.fechafinal <= contrato.fechafincontrato <= nomina.fechafinal:
        diasnomina -= (nomina.fechafinal - contrato.fechafincontrato).days
        
        
    dias_vacaciones = calcular_vacaciones(contrato,nomina)
    dias_incapacidad = calculo_incapacidad(contrato, idnomina)
    diasnomina -= dias_vacaciones 
    diasnomina -= dias_incapacidad 
    
    
    calculo_prestamo(contrato, idnomina)
    calculo_novfija(contrato, idnomina)
    
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
            idnomina_id=idnomina
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
                idnomina_id = idnomina ,
            )   
    return True
    



def incapacidad_payroll(idcontrato ,idempresa, idnomina):
    
    nomina = Crearnomina.objects.get(idnomina=idnomina)
    inicio_nomina, fin_nomina = nomina.fechainicial, nomina.fechafinal
    ano = nomina.anoacumular.ano 
    
    incapacidades = Incapacidades.objects.filter(idcontrato__id_empresa =  idempresa, fechainicial__range=(inicio_nomina, fin_nomina) ,idcontrato  = idcontrato )
    salario_minimo = Salariominimoanual.objects.get( ano = ano ).salariominimo
    pago_incapacidad = Empresa.objects.get(idempresa=1).ige100 or "NO"
    
    
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
                    idnomina_id=idnomina
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
                    idnomina_id=idnomina
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


def aportes_payroll(idcontrato ,idempresa, idnomina):
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
    
    contrato = Contratos.objects.get(idcontrato =  idcontrato)
            
    salario_emp = contrato.salario
    tipo_salario = contrato.tiposalario.idtiposalario

    
    # Obtener la suma de las deducciones de la eps 
    total_base_ss = Nomina.objects.filter(
        idcontrato=contrato,
        idnomina_id=idnomina,
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
            idnomina_id=idnomina
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
                    idnomina_id = idnomina ,
                )  
            
        
        
        
        aux_pass = Nomina.objects.filter(
            idconcepto=concepto2,
            idcontrato=contrato,
            estadonomina = 1,
            idnomina_id=idnomina
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
                    idnomina_id = idnomina ,
                ) 
        
        
        
        if valorfsp > 0:
            aux_pass = Nomina.objects.filter(
                idconcepto=concepto3,
                idcontrato=contrato,
                estadonomina = 1,
                idnomina_id= idnomina
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
                        idnomina_id = idnomina ,
                    ) 
                
    return True



def transporte_payroll(idcontrato ,idempresa, idnomina):
    
    contrato = Contratos.objects.get(idcontrato =  idcontrato)
    try:
        nomina = Crearnomina.objects.get(idnomina=idnomina)
    except Crearnomina.DoesNotExist:
        return "Error de creación de nómina"
    
    sal_min = Salariominimoanual.objects.get(ano = nomina.anoacumular.ano).salariominimo
    aux_tra = Salariominimoanual.objects.get(ano = nomina.anoacumular.ano).auxtransporte
    
    diasnomina = nomina.diasnomina
    
    if contrato.fechainiciocontrato > nomina.fechafinal:
        diasnomina = (nomina.fechafinal - contrato.fechainiciocontrato).days + 1
    
    if contrato.fechafincontrato and nomina.fechafinal <= contrato.fechafincontrato <= nomina.fechafinal:
        diasnomina -= (nomina.fechafinal - contrato.fechafincontrato).days
        
    dias_vacaciones = calcular_vacaciones(contrato,nomina)
    dias_incapacidad = calculo_incapacidad(contrato, idnomina)

    diasnomina -= dias_vacaciones 
    diasnomina -= dias_incapacidad 
    
    
    horas_basico_mes = Nomina.objects.filter(idconcepto__codigo = 1, idcontrato=contrato.idcontrato, 
                                                idnomina__mesacumular = nomina.mesacumular , idnomina__anoacumular = nomina.anoacumular ,
                                                estadonomina=2).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
    
    horas_basico_quincena = Nomina.objects.filter(idconcepto=1, idcontrato=contrato.idcontrato, 
                                                    idnomina_id=idnomina).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
    
    total_mes = horas_basico_mes + horas_basico_quincena

    if not contrato.auxiliotransporte :
        transporte = 0
        diasnomina = 0
            
    elif contrato.salario <= (sal_min * 2):
        # Obtener la suma de las deducciones de la eps 
        total_base_trans = Nomina.objects.filter(
            idcontrato=contrato,
            idnomina_id=idnomina,
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
                    idnomina_id=idnomina
                    
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
                        idnomina_id = idnomina ,
                    )  
    return True



    
def data_visua(idcontrato ,idempresa, idnomina):
    ingreso = 0  # Inicializamos la variable ingreso
    egreso = 0   # Inicializamos la variable egreso
    conceptos_data = []
    
    conceptos = Nomina.objects.filter(
                    idnomina__idnomina= idnomina ,
                    idcontrato__idcontrato=idcontrato 
                ).select_related('idcontrato').order_by('idconcepto__codigo')
        
    for concepto1 in conceptos:
        
        concepto_info = {
            'idn': concepto1.idregistronom,
            "id": concepto1.idconcepto.idconcepto,
            "amount": concepto1.cantidad,
            "value": concepto1.valor,
        }
        
        if concepto1.valor > 0:
            ingreso += concepto1.valor  # Agregar a ingreso si es positivo
        elif concepto1.valor < 0:
            egreso += concepto1.valor 
        
        # Agregar el concepto al arreglo
        conceptos_data.append(concepto_info)        
    
    total = ingreso + egreso
    salario = concepto1.idcontrato.salario 
    
    data = {    
        "salario": f"{format_value(salario)}$",
        "ingresos": f"{format_value(ingreso)}$",
        "egresos": f"{format_value(egreso)}$",
        "total": f"{format_value(total)}$",
        "conceptos": conceptos_data,
        "value": True,
        "conceptors": [(item.idconcepto, f"{item.codigo} - {item.nombreconcepto}") for item in Conceptosdenomina.objects.filter(id_empresa_id=idempresa).order_by('codigo') ]
    }
    
    return data 
