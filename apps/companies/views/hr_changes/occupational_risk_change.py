from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from apps.common.models import EditHistory , Contratos , Entidadessegsocial , User
from apps.companies.forms.OccupationalRiskChangeForm import OccupationalRiskChangeForm
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse

@login_required
@role_required('company','accountant')
def occupational_risk_change(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    cambios = EditHistory.objects.filter(
        operation_type='update',
        id_empresa_id=idempresa,
        modified_model='Contratos-Afp'
    ).select_related('user').order_by('-modification_time')


    afp = []

    for item in cambios:
        try:
            contrato = Contratos.objects.select_related('idempleado', 'codafp').get(idcontrato=item.modified_object_id)
            
            empleado = contrato.idempleado
            nombre_completo = f"{empleado.papellido} {empleado.pnombre}"

            afp.append({
                'contrato_id': contrato.idcontrato,
                'documento': empleado.docidentidad,
                'nombre': nombre_completo,
                'afp_anterior': item.old_value,
                'afp_actual': item.new_value,
                'fecha_cambio': item.modification_time,
                'user': item.user.email,
            })

        except Contratos.DoesNotExist:
            continue
        
    
    return render(request, "./companies/occupational_risk_change.html",{'afp': afp })




@login_required
@role_required('company','accountant')
def occupational_risk_change_add(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    iduser =  usuario['id']
    
    form = OccupationalRiskChangeForm(idempresa = idempresa)
    if request.method == 'POST':
        form = OccupationalRiskChangeForm(request.POST , idempresa=idempresa )
        if form.is_valid():
            idcontrato = form.cleaned_data['contract'] 
            afp_oll = Entidadessegsocial.objects.get(identidad = form.cleaned_data['afp_oll'] )
            afp_new = Entidadessegsocial.objects.get(identidad = form.cleaned_data['afp_new'] )
            
            contrato = Contratos.objects.get(idcontrato = idcontrato) 
            # Actualizar contrato
            contrato.codafp = afp_new
            contrato.save()

            usuario = User.objects.get(id = iduser)
            

            EditHistory.objects.create(
                modified_model = 'Contratos-Afp',  
                modified_object_id = idcontrato, # ID del objeto modificado
                user = usuario ,  # Usuario que hizo la modificación
                modification_time = timezone.now(),  # Fecha de la modificación
                operation_type =  'update' , # Tipo de operación
                field_name='afp',
                old_value=afp_oll.entidad,
                new_value=afp_new.entidad,
                description=f'Se cambió la eps del contrato #{idcontrato}',
                id_empresa_id = idempresa
                
            )
            
            
            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
            response['X-Up-message'] = 'Cambio guardado correctamente'    
            response['X-Up-Location'] = reverse('companies:occupational_risk_change')           
            return response
        
        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")  

    return render(request, "./companies/partials/occupational_risk_change_add.html",{'form':form})



@login_required
def get_afp(request):
    contract_id = request.GET.get('contract_id')

    try:
        contrato = Contratos.objects.select_related('codafp').get(idcontrato=contract_id)
        return JsonResponse({
            'afp_id': contrato.codafp.identidad if contrato.codafp else '',
            'afp_nombre': contrato.codafp.entidad if contrato.codafp else ''
        })
    except Contratos.DoesNotExist:
        return JsonResponse({'error': 'Contrato no encontrado'}, status=404)