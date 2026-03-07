from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from apps.common.models import EditHistory , Contratos , Entidadessegsocial , User
from apps.companies.forms.SeveranceChangeForm import SeveranceChangeForm
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse

@login_required
@role_required('company','accountant')
def severance_fund_change(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    cambios = EditHistory.objects.filter(
        operation_type='update',
        id_empresa_id=idempresa,
        modified_model='Contratos-Fdc'
    ).select_related('user').order_by('-modification_time')


    cargos = []

    for item in cambios:
        try:
            contrato = Contratos.objects.select_related('idempleado', 'cargo').get(idcontrato=item.modified_object_id)

            empleado = contrato.idempleado
            nombre_completo = f"{empleado.papellido} {empleado.pnombre}"

            cargos.append({
                'contrato_id': contrato.idcontrato,
                'documento': empleado.docidentidad,
                'nombre': nombre_completo,
                'fondo_anterior': item.old_value,
                'fondo_actual': item.new_value,
                'fecha_cambio': item.modification_time,
                'user': item.user.email,
            })

        except Contratos.DoesNotExist:
            continue
        
    
    return render(request, "./companies/severance_fund_change.html",{'cargos': cargos })




@login_required
@role_required('company','accountant')
def severance_fund_change_add(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    iduser =  usuario['id']
    
    form = SeveranceChangeForm(idempresa = idempresa)
    if request.method == 'POST':
        form = SeveranceChangeForm(request.POST , idempresa=idempresa )
        if form.is_valid():
            idcontrato = form.cleaned_data['contract'] 
            fps_oll = Entidadessegsocial.objects.get(identidad = form.cleaned_data['fps_oll'] )
            fps_new = Entidadessegsocial.objects.get(identidad = form.cleaned_data['fps_new'] )
            
            contrato = Contratos.objects.get(idcontrato = idcontrato) 
            # Actualizar contrato
            contrato.cargo = fps_new
            contrato.save()

            usuario = User.objects.get(id = iduser)
            

            EditHistory.objects.create(
                modified_model = 'Contratos-Fdc',  
                modified_object_id = idcontrato, # ID del objeto modificado
                user = usuario ,  # Usuario que hizo la modificación
                modification_time = timezone.now(),  # Fecha de la modificación
                operation_type =  'update' , # Tipo de operación
                field_name='FDC',
                old_value=fps_oll.entidad,
                new_value=fps_new.entidad,
                description=f'Se cambió el FDC del contrato #{idcontrato}',
                id_empresa_id = idempresa
                
            )
            
            
            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
            response['X-Up-message'] = 'Cambio guardado correctamente'    
            response['X-Up-Location'] = reverse('companies:severance_fund_change')           
            return response
        
        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")  

    return render(request, "./companies/partials/severance_fund_change_add.html",{'form':form})



@login_required
def get_fps(request):
    contract_id = request.GET.get('contract_id')

    try:
        contrato = Contratos.objects.select_related('fondocesantias').get(idcontrato=contract_id)
        cargo_id= contrato.fondocesantias.identidad if contrato.fondocesantias else ''
        cargo_nombre =  contrato.fondocesantias.identidad if contrato.fondocesantias else ''

        print('-------------')
        print(cargo_id)
        print(cargo_nombre)
        print('-------------')

        return JsonResponse({
            'cargo_id': contrato.fondocesantias.identidad if contrato.fondocesantias else '',
            'cargo_nombre': contrato.fondocesantias.identidad if contrato.fondocesantias else ''
        })
    except Contratos.DoesNotExist:
        return JsonResponse({'error': 'Contrato no encontrado'}, status=404)