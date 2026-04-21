

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
        return []

    contrato = Contratos.objects.get(idcontrato=idcontrato)
    if contrato.tiposalario.idtiposalario == 2:
        codigo_aux = '4'
    elif contrato.tipocontrato_id == 6:
        codigo_aux = '34'
    else:
        codigo_aux = '1'
    
    acumulados = precargar_acumulados(nomina, int(codigo_aux))
    concepto = Conceptosdenomina.objects.get(codigo = codigo_aux, id_empresa = contrato.id_empresa)
    diasnomina = calcular_dias(contrato,nomina,int(codigo_aux),acumulados)

    calculo_prestamo(contrato, idnomina)
    Calculo_vacaciones(contrato, idnomina)
    calculo_novfija(contrato, idnomina)

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
                idconcepto = concepto ,
                cantidad=diasnomina ,
                valor=valorsalario ,
                estadonomina = 1,
                idcontrato_id=contrato.idcontrato ,
                idnomina_id = idnomina ,
            ) 

    return True
    



def incapacidad_payroll(idcontrato ,idempresa, idnomina):

    nomina = Crearnomina.objects.get(idnomina=idnomina)
    inicio_nomina, fin_nomina = nomina.fechainicial, nomina.fechafinal
    ano = nomina.anoacumular.ano 

    salario_minimo = Salariominimoanual.objects.get( ano = ano ).salariominimo
    pago_incapacidad = Empresa.objects.get(idempresa = idempresa).ige100 or "NO"

    contract = Contratos.objects.get(idcontrato=idcontrato)
    incapacidades = Incapacidades.objects.filter(idcontrato__id_empresa =  idempresa, idcontrato_id = idcontrato ).order_by('-fechainicial')

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

        if pago_incapacidad == "NO":
            ibc = round(ibc * 2 / 3, 0)
            
        if ibc < salario_minimo:
            ibc = salario_minimo

        idconceptoi, idconceptoa = return_tipo_incapacidad(tipo, idempresa)
        inicio_real = max(ini, inicio_nomina)
        fin_real = min(fin, fin_nomina)

        if inicio_real > fin_real:
            dias_incapacidad = 0
            continue
        else:
            dias_incapacidad = (fin_real - inicio_real).days + 1

            dias_incapacidad -= dias_asumidos

        if prorroga:
            dias_asumidos = 0
            dias_incapacidad = calculo_incapacidad(contract.idcontrato, nomina)
            ibc = disabilities_ibc(contract , str(inicio_nomina) )
            valor_incapacidad = (ibc / 30 ) * dias_incapacidad

            valor_incapacidad = (
                Decimal(ibc) / Decimal('30') * Decimal(dias_incapacidad)
            ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

            if dias_incapacidad > 0:
                grabar_incapacidad(idconceptoi, dias_incapacidad, valor_incapacidad, contract, idnomina , idempresa, incapacidad)
                
                break
        else : 
            valor_incapacidad = (
                Decimal(ibc) / Decimal('30') * Decimal(dias_incapacidad)
            ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

            valor_asumido = (
                Decimal(ibc) / Decimal('30') * Decimal(dias_asumidos)
            ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

            if dias_incapacidad > 0:
                grabar_incapacidad(idconceptoi, dias_incapacidad, valor_incapacidad, contract, idnomina, idempresa, incapacidad)

            if dias_asumidos > 0:
                grabar_incapacidad(idconceptoa, dias_asumidos, valor_asumido, contract, idnomina, idempresa, incapacidad)


    return True


def aportes_payroll(idcontrato ,idempresa, idnomina):


    EPS = Conceptosfijos.objects.get(idfijo=8)
    AFP = Conceptosfijos.objects.get(idfijo=10)
    tope_ibc = Conceptosfijos.objects.get(idfijo=2)
    factor_integral = Conceptosfijos.objects.get(idfijo=1).valorfijo

    fsp416 = Conceptosfijos.objects.get(idfijo=12).valorfijo
    fsp1617 = Conceptosfijos.objects.get(idfijo=13).valorfijo
    fsp1718 = Conceptosfijos.objects.get(idfijo=14).valorfijo
    fsp1819 = Conceptosfijos.objects.get(idfijo=15).valorfijo
    fsp1920 = Conceptosfijos.objects.get(idfijo=16).valorfijo
    fsp21 = Conceptosfijos.objects.get(idfijo=17).valorfijo

    contrato = Contratos.objects.select_related('tiposalario').get(idcontrato=idcontrato)
    tipo_salario = contrato.tiposalario.idtiposalario
    sal_min = Salariominimoanual.objects.get(ano = datetime.now().year).salariominimo
    nomina = Crearnomina.objects.get( idnomina = idnomina)

    # Obtener la suma de las deducciones de la eps 
    total_base_ss = Nomina.objects.filter(
        idcontrato=contrato,
        idnomina_id=idnomina,
        estadonomina = 1 ,
        idconcepto__indicador__nombre='basesegsocial'
    ).exclude(
        idconcepto__codigo__in=[60, 70, 90] # Excluir conceptos cuyo código sea el de EPS
    ).aggregate(total=Sum('valor'))['total'] or 0  # Reemplaza 'monto' con el nombre correcto de la columna
                
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

        base_max = sal_min * tope_ibc.valorfijo

        if tipo_salario == 2:   
            total_base_ss *= (factor_integral / 100)
            total_base_ss = round(total_base_ss, 2)
        
        base_ss = min(total_base_ss, base_max)
        base_ss = round(base_ss, 2)

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

        if valoreps > 0:

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
                        idnomina_id = idnomina ,
                    )

        if valorafp > 0:

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
                        idnomina_id = idnomina ,
                    ) 
            
            
            
    
    if base_ss_fsp2 > 0:
        concepto3 = Conceptosdenomina.objects.get(codigo=90, id_empresa_id=idempresa)

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
            
        if contrato.pensionado == '2':
            valorfsp = 0.00


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
                    idnomina_id=idnomina
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
                        idnomina_id = idnomina ,
                    ) 
            
    return True



def transporte_payroll(idcontrato ,idempresa, idnomina):
    
    try:
        nomina = Crearnomina.objects.get(idnomina=idnomina)
    except Crearnomina.DoesNotExist:
        return []

    contrato = Contratos.objects.get(idcontrato=idcontrato)
    sal_min = Salariominimoanual.objects.get(ano=nomina.anoacumular.ano).salariominimo
    aux_tra = Salariominimoanual.objects.get(ano=nomina.anoacumular.ano).auxtransporte
    concepto = Conceptosdenomina.objects.get(codigo=2, id_empresa = contrato.id_empresa)
    acumulados = precargar_acumulados(nomina, 2)

    diasnomina = calcular_dias(contrato, nomina, 2,acumulados)

    if contrato.tipocontrato.idtipocontrato in [5, 6]:
        valor = 0


    transporte = return_transporte(contrato, nomina, diasnomina, sal_min, aux_tra)

    aux_pass = Nomina.objects.filter(
            idconcepto=concepto,
            idcontrato=contrato,
            estadonomina=1,
            idnomina_id=idnomina,
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
                idnomina_id=idnomina,
            )

    return True
        



    
def data_visua(idcontrato ,idempresa, idnomina):
    ingreso = 0  # Inicializamos la variable ingreso
    egreso = 0   # Inicializamos la variable egreso
    conceptos_data = []
    
    conceptos = Nomina.objects.filter(
                    idnomina__idnomina= idnomina ,
                    idcontrato__idcontrato=idcontrato ,
                    estadonomina = 1 
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
