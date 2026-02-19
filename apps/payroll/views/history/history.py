from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import HistoricoNomina, Salariominimoanual , Entidadessegsocial , Cargos , Costos , Nomina , Crearnomina
from django.contrib import messages
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from django.urls import reverse
from decimal import Decimal 
from django.db.models import F, Q, Case, When, Value, CharField, Sum, Count
from django.db.models.functions import Concat

def clean_field(field_name):
    return Case(
        When(**{f"{field_name}__in": ["no data", "sin dato", "n/a", "none", "ninguno"]}, then=Value("")),
        default=F(field_name),
        output_field=CharField()
    )


@login_required
@role_required('company','admin','accountant')
def history_salary(request):
    

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    historys = HistoricoNomina.objects.select_related(
        'contrato__idempleado',
        'contrato',
        'contrato__id_empresa' , 
    ).filter(contrato__id_empresa = idempresa).annotate(
        contract_id = F('contrato'), 
        employee_name=Concat(
            clean_field('contrato__idempleado__pnombre'), Value(' '),
            clean_field('contrato__idempleado__snombre'), Value(' '),
            clean_field('contrato__idempleado__papellido'), Value(' '),
            clean_field('contrato__idempleado__sapellido'),
        ),
        employee_document=F('contrato__idempleado__docidentidad'),
    )
    
    return render(request, './payroll/history_salary.html',{'historys':historys})



@login_required
@role_required('company','admin','accountant')
def history_salary_details(request,id):
    history = HistoricoNomina.objects.get(id = id)

    data = history.historial

    salud_ids = set()
    pension_ids = set()
    cargo_ids = set()
    costo_ids = set()
    nomina_ids = set()

    for item in data.values():

        salud_ids.add(item['salud_id'])
        pension_ids.add(item['pension_id'])
        cargo_ids.add(item['cargo_id'])
        costo_ids.add(item['costo_id'])
        nomina_ids.add(item['idnomina'])


    salud = Entidadessegsocial.objects.in_bulk(salud_ids)
    pension = Entidadessegsocial.objects.in_bulk(pension_ids)
    cargos = Cargos.objects.in_bulk(cargo_ids)
    costos = Costos.objects.in_bulk(costo_ids)
    nomina = Crearnomina.objects.in_bulk(nomina_ids,field_name='idnomina')

    enriched = []

    for key, item in data.items():
        aux = nomina.get(item['idnomina'])
        enriched.append({
            'nombre_nomina': item['nombre_nomina'],
            'fecha_inicio': item['fecha_inicio'],
            'fecha_final': item['fecha_final'],
            'salario': item['salario'],
            'eps': salud.get(item['salud_id']),
            'pension': pension.get(item['pension_id']),
            'cargo': cargos.get(item['cargo_id']),
            'costo': costos.get(item['costo_id']),
            'nomina':aux.idnomina ,
        })

    enriched = sorted(enriched, key=lambda x: x['nomina'], reverse=True)
    return render(request, './payroll/partials/history_salary_details.html',{'data':enriched})
