from django.shortcuts import render, redirect, get_object_or_404
from apps.components.decorators import  role_required
from apps.common.models  import NovSalarios, Contratos
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from apps.companies.forms.updatesalaryForm import updatesalaryForm
from django.http import JsonResponse , HttpResponse
from django.urls import reverse

@login_required
@role_required('company','accountant')
def update_salary(request):
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    novsalarios = NovSalarios.objects.filter(idcontrato__id_empresa = idempresa )
    
    
    
    return render (request, './companies/update_salary.html',{'novsalarios':novsalarios})



@login_required
@role_required('company','accountant')
def update_salary_add(request):
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    form = updatesalaryForm(idempresa = idempresa)
    if request.method == 'POST':
        form = updatesalaryForm(request.POST , idempresa=idempresa )
        if form.is_valid():
            
            newsalary = NovSalarios.objects.create(
                idcontrato_id = form.cleaned_data['idcontrato'] ,
                salarioactual = form.cleaned_data['Salario_Actual'] ,
                nuevosalario = form.cleaned_data['Salario_nuevo'] ,
                fechanuevosalario = form.cleaned_data['fecha_nuevo'] ,
                tiposalario = form.cleaned_data['contractType'] ,
            )
            
            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
            response['X-Up-message'] = 'Nuevo salario guardada exitosamente'    
            response['X-Up-Location'] = reverse('companies:update_salary')           
            return response

        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")   
    return render (request, './companies/partials/update_salary_add.html',{'form':form})


@login_required
@role_required('company','accountant')
def get_contract_salary(request):
    """
    Endpoint para obtener el salario de un contrato específico
    """
    if request.method == 'GET':
        
        contract_id = request.GET.get('contract_id')
        if not contract_id:
            return JsonResponse({
                'success': False,
                'error': 'ID de contrato requerido'
            })
        
        try:
            contract = Contratos.objects.get(
                idcontrato=contract_id,
                estadocontrato=1  # Solo contratos activos
            )
            return JsonResponse({
                'success': True,
                'salary': contract.salario or 0
            })
        except Contratos.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Contrato no encontrado'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })