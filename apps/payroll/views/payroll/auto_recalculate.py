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





def auto_recalculate(idnomina,idcontrato):
    nomina = Crearnomina.objects.get(idnomina = idnomina)
    contrato = Contratos.objects.get(idcontrato = idcontrato)
    sal_min = Salariominimoanual.objects.get(ano = nomina.fechapago.year).salariominimo

    concepto1 = Conceptosdenomina.objects.get(codigo=60, id_empresa =contrato.id_empresa)
    concepto2 = Conceptosdenomina.objects.get(codigo=70, id_empresa =contrato.id_empresa)
    concepto3 = Conceptosdenomina.objects.get(codigo=90, id_empresa =contrato.id_empresa)

    registros = Nomina.objects.select_related(
        'idcontrato',
        'idconcepto'
    ).filter(
        idnomina_id=idnomina,
        idcontrato=contrato,
        idconcepto__codigo__in=[60, 70, 90]
    )


    tipo_salario = contrato.tiposalario.idtiposalario
    # Obtener la suma de las deducciones de la eps 
    total_base_ss = Nomina.objects.filter(
        idcontrato=contrato,
        idnomina=nomina,
        estadonomina = 1 ,
        idconcepto__indicador__nombre='basesegsocial'
    ).exclude(
        idconcepto__codigo__in=[60, 70, 90] # Excluir conceptos cuyo código sea el de EPS
    ).aggregate(total=Sum('valor'))['total'] or 0 

    base_ss_fsp =   Nomina.objects.filter(
        idcontrato = contrato,
        idnomina__mesacumular = nomina.mesacumular ,
        idnomina__anoacumular = nomina.anoacumular ,
        idconcepto__indicador__nombre='basesegsocial'
    ).exclude(
        idconcepto__codigo__in=[60, 70, 90] # Excluir conceptos cuyo código sea el de EPS
    ).aggregate(total=Sum('valor'))['total'] or 0 

    if contrato.tiposalario.idtiposalario == 2:
        base_ss_fsp2 = base_ss_fsp * Decimal('0.7')
    else : 
        base_ss_fsp2 = base_ss_fsp

        
    tiene_eps = registros.filter(idconcepto__codigo=60).exists()
    tiene_pension = registros.filter(idconcepto__codigo=70).exists()
    tiene_fsp = registros.filter(idconcepto__codigo=90).exists()

    if tipo_salario == 2:
        total_base_ss *= (factor_integral / 100)
        total_base_ss = round(total_base_ss, 2)


    base_max = sal_min * tope_ibc.valorfijo
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


    fsp = registros.filter(idconcepto__codigo=90).first()

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
        valorafp = 0.00
        valorfsp = 0.00

    if tiene_eps:

        eps = registros.filter(idconcepto__codigo=60).first()
        if eps.valor != (-1*valoreps):
            eps.valor = -valoreps
            eps.save()  
    else:

        if valoreps > 0:
            Nomina.objects.create(
                idconcepto = concepto1 ,
                cantidad= 0 ,
                estadonomina = 1,
                valor= -1*valoreps , 
                idcontrato =contrato ,
                idnomina = nomina ,
            ) 

        
    if tiene_pension:

        afp = registros.filter(idconcepto__codigo=70).first()
        if afp.valor != (-1*valorafp):
            afp.valor = -valorafp
            afp.save()  

    else :
        if valorafp > 0:
            Nomina.objects.create(
                idconcepto = concepto2 ,
                cantidad= 0 ,
                estadonomina = 1,
                valor= -1*valorafp , 
                idcontrato =contrato ,
                idnomina = nomina ,
            ) 

    if tiene_fsp:
        if fsp.valor != (-1*valorfsp):
            fsp.valor = -valorfsp
            fsp.save()  

        if contrato.pensionado == '2':
            valorafp = 0.00
            valorfsp = 0.00
    else :

        if valorfsp > 0:
            Nomina.objects.create(
                idconcepto = concepto3 ,
                cantidad= 0 ,
                estadonomina = 1,
                valor= -1*valorfsp , 
                idcontrato =contrato ,
                idnomina = nomina ,
            ) 


    return True