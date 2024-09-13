from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.filterform import FilterForm 
from apps.components.decorators import  role_required
from apps.companies.models import Incapacidades , Contratosemp ,Contratos,Entidadessegsocial ,Diagnosticosenfermedades
from apps.companies.forms.disabilitiesForm  import DisabilitiesForm
from datetime import datetime


def disabilities(request):
  errors = False
  incapacidades = Incapacidades.objects.values(
      'idcontrato__idcontrato',
      'idempleado__docidentidad',
      'idempleado__pnombre',
      'idempleado__snombre',
      'idempleado__papellido',
      'idempleado__sapellido',
      'entidad',
      'coddiagnostico__coddiagnostico',
      'diagnostico',
      'prorroga',
      'fechainicial',
      'dias',
  ).order_by('-idincapacidad')
  
  
  form = DisabilitiesForm()
  
  if request.method == 'POST':
    form = DisabilitiesForm(request.POST)
    if form.is_valid():
      # Procesa los datos del formulario
      contract = form.cleaned_data['contract']
      entity = form.cleaned_data['entity']
      origin = form.cleaned_data['origin']
      initial_date = form.cleaned_data['initial_date']
      incapacity_days = form.cleaned_data['incapacity_days']
      diagnosis_code = form.cleaned_data['diagnosis_code']
      extension = form.cleaned_data['extension']
      end_date = form.cleaned_data['end_date']
      previous_month_ibc = form.cleaned_data['previous_month_ibc']
      
      
      contrato = Contratos.objects.get(idcontrato = contract)
      empleado = Contratosemp.objects.get(idempleado = contrato.idempleado.idempleado)
      entidad = Entidadessegsocial.objects.get(codigo = entity)
      dianostico = Diagnosticosenfermedades.objects.get(coddiagnostico = diagnosis_code)
      
      
      new_incapacity = Incapacidades(
        empleado = f"{empleado.papellido} {empleado.sapellido} {empleado.snombre} {empleado.pnombre} - {empleado.snombre} P" , 
        tipoentidad = entidad.tipoentidad, 
        entidad = entidad.entidad,
        coddiagnostico = dianostico,
        diagnostico =  dianostico.diagnostico,
        fechainicial = datetime.strptime(initial_date, "%Y-%m-%d"),
        dias = int (incapacity_days),
        idempleado= empleado,
        idcontrato = contrato,
        prorroga =  extension ,
        ibc = previous_month_ibc,
        finincap =  datetime.strptime(end_date, "%Y-%m-%d"),
      )
      new_incapacity.save()  
      errors = False
      messages.success(request, 'La Incapacidad ha sido añadido con éxito.')
      return redirect('companies:disabilities')
    else:
      errors = True
    

  return render (request, './companies/disabilities.html',
                  {
                    'incapacidades' :incapacidades,  
                    'form' :form,
                    'errors':errors,
                  })