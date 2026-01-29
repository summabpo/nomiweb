from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from apps.common.models import EditHistory , Contratos , Entidadessegsocial , User
from apps.companies.forms.HealthInsuranceChangeForm import HealthInsuranceChangeForm
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse

@login_required
@role_required('company','accountant')
def health_insurance_change(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    cambios = EditHistory.objects.filter(
        operation_type='update',
        id_empresa_id=idempresa,
        modified_model='Contratos-Eps'
    ).select_related('user').order_by('-modification_time')


    eps = []

    for item in cambios:
        try:
            contrato = Contratos.objects.select_related('idempleado', 'codeps').get(idcontrato=item.modified_object_id)
            
            empleado = contrato.idempleado
            nombre_completo = f"{empleado.papellido} {empleado.pnombre}"

            eps.append({
                'contrato_id': contrato.idcontrato,
                'documento': empleado.docidentidad,
                'nombre': nombre_completo,
                'eps_anterior': item.old_value,
                'eps_actual': item.new_value,
                'fecha_cambio': item.modification_time,
                'user': item.user.email,
            })

        except Contratos.DoesNotExist:
            continue
        
    
    return render(request, "./companies/health_insurance_change.html",{'eps': eps })




@login_required
@role_required('company','accountant')
def health_insurance_change_add(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    iduser =  usuario['id']
    
    form = HealthInsuranceChangeForm(idempresa = idempresa)
    if request.method == 'POST':
        form = HealthInsuranceChangeForm(request.POST , idempresa=idempresa )
        if form.is_valid():
            idcontrato = form.cleaned_data['contract'] 
            eps_oll = Entidadessegsocial.objects.get(identidad = form.cleaned_data['eps_oll'] )
            eps_new = Entidadessegsocial.objects.get(identidad = form.cleaned_data['eps_new'] )
            
            contrato = Contratos.objects.get(idcontrato = idcontrato) 
            # Actualizar contrato
            contrato.codeps = eps_new
            contrato.save()

            usuario = User.objects.get(id = iduser)
            

            EditHistory.objects.create(
                modified_model = 'Contratos-Eps',  
                modified_object_id = idcontrato, # ID del objeto modificado
                user = usuario ,  # Usuario que hizo la modificación
                modification_time = timezone.now(),  # Fecha de la modificación
                operation_type =  'update' , # Tipo de operación
                field_name='eps',
                old_value=eps_oll.entidad,
                new_value=eps_new.entidad,
                description=f'Se cambió la eps del contrato #{idcontrato}',
                id_empresa_id = idempresa
                
            )
            
            
            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
            response['X-Up-message'] = 'Cambio guardado correctamente'    
            response['X-Up-Location'] = reverse('companies:health_insurance_change')           
            return response
        
        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")  

    return render(request, "./companies/partials/health_insurance_change_add.html",{'form':form})



@login_required
def get_eps(request):
    contract_id = request.GET.get('contract_id')

    try:
        contrato = Contratos.objects.select_related('codeps').get(idcontrato=contract_id)
        return JsonResponse({
            'eps_id': contrato.codeps.identidad if contrato.codeps else '',
            'eps_nombre': contrato.codeps.entidad if contrato.codeps else ''
        })
    except Contratos.DoesNotExist:
        return JsonResponse({'error': 'Contrato no encontrado'}, status=404)