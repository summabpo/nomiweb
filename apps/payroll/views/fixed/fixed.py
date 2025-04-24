from django.shortcuts import render 
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import NovFijos , Conceptosdenomina , Contratos
from apps.payroll.forms.FixedForm import FixidForm
from django.http import HttpResponse
from django.urls import reverse

@login_required
@role_required('accountant')
def fixed(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    novfijos = NovFijos.objects.filter(idcontrato__id_empresa = idempresa).order_by('-idnovfija')
    return render(request, './payroll/fixedconcepts.html',{'novfijos': novfijos})
    

@login_required
@role_required('accountant')
def fixed_modal(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = FixidForm(idempresa=idempresa)
    
    if request.method == 'POST':
        form = FixidForm(request.POST , idempresa=idempresa )
        if form.is_valid():
            
            # Aquí obtienes los datos del formulario limpio
            idcontrato = form.cleaned_data['idcontrato']
            valor = form.cleaned_data['valor']
            descrip = form.cleaned_data['descrip']
            idconcepto = form.cleaned_data['idconcepto']
            estado = form.cleaned_data['estado']
            fecha = form.cleaned_data['fecha']

            concepto = Conceptosdenomina.objects.get(idconcepto = idconcepto  )
            contrato = Contratos.objects.get(idcontrato = idcontrato)

            NovFijos.objects.create(
                idconcepto = concepto ,  
                valor = valor , 
                idcontrato = contrato ,   #fk principal 
                estado_novfija = estado,
                descripcion = descrip ,
                fechafinnovedad = fecha ,

            )

            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
            response['X-Up-message'] = 'La Novedad fue registrada correctamente'    
            response['X-Up-Location'] = reverse('payroll:fixedconcepts')           
            return response
    
    return render(request, './payroll/partials/fixedconceptsmodal.html' ,{'form':form})





