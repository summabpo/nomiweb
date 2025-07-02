from django.shortcuts import render 
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import NovFijos , Conceptosdenomina , Contratos ,Indicador
from apps.payroll.forms.FixedForm import FixidForm
from django.http import HttpResponse
from django.urls import reverse
from apps.payroll.forms.FamilyForm import FamilyForm , FamilyForm2



@login_required
@role_required('accountant')
def family_list(request):
    familys = Indicador.objects.all().order_by('id')
    return render(request, './payroll/family_list.html',{'familys': familys})
   
   
   
@login_required
@role_required('accountant')
def family_create(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = FamilyForm(idempresa = idempresa)
    if request.method == 'POST':
        form = FamilyForm(request.POST , idempresa=idempresa )
        if form.is_valid():
            indicador = Indicador.objects.create(
                nombre = form.cleaned_data['name'] ,
                descripcion = form.cleaned_data['descrip']
            )
            
            concepts = form.cleaned_data['idconcepto']
            for data in concepts : 
                concept = Conceptosdenomina.objects.get(idconcepto = data )
                concept.indicador.add(indicador)
                
            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
            response['X-Up-message'] = 'Familia guardada exitosamente'    
            response['X-Up-Location'] = reverse('payroll:family_list')           
            return response
        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")    
    
    return render(request, './payroll/partials/family_create.html',{'form': form})




@login_required
@role_required('accountant')
def family_detail(request,id):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    family = Indicador.objects.get(id = id)
    conceptos = Conceptosdenomina.objects.filter(indicador=family ,id_empresa = idempresa )
    data = {
        'name': family.nombre,
        'descrip': family.descripcion,
        'concepts': conceptos,  # Lista de conceptos relacionados
    }
    return render(request, './payroll/partials/family_detail.html',{'data': data})
   


@login_required
@role_required('accountant')
def family_edit(request,id):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    family = Indicador.objects.get(id = id)
    conceptos = Conceptosdenomina.objects.filter(indicador=family ,id_empresa = idempresa )
    data = {
        'name': family.nombre,
        'descrip': family.descripcion,
        'idconcepto': [i.idconcepto for i in conceptos] ,  # Lista de conceptos relacionados
    }
    
    form = FamilyForm2(idempresa = idempresa , initial = data)
    if request.method == 'POST':
        form = FamilyForm2(request.POST,idempresa = idempresa)
        if form.is_valid():
            
            descrip = form.cleaned_data['descrip']
            
            if family.descripcion != descrip:
                family.descripcion = descrip 
            
            family.save()
            
            concepts_ids_post = set(form.cleaned_data['idconcepto'])  # IDs del formulario (POST)
            concepts_current = Conceptosdenomina.objects.filter(indicador=family, id_empresa=idempresa)

            # 1. Eliminar conceptos que ya no están seleccionados
            for concept in concepts_current:
                if concept.idconcepto not in concepts_ids_post:
                    concept.indicador.remove(family)

            # 2. Agregar los nuevos conceptos seleccionados (o mantener los existentes)
            for concept_id in concepts_ids_post:
                concept = Conceptosdenomina.objects.get(idconcepto=concept_id)
                concept.indicador.add(family)
                
            
            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
            response['X-Up-message'] = 'Familia actualizada exitosamente'    
            response['X-Up-Location'] = reverse('payroll:family_list')           
            return response
        
    return render(request, './payroll/partials/family_edit.html',{'form': form})


