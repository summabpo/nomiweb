from django.shortcuts import render,redirect
from apps.administrator.forms.companiesForm import CompaniesForm

from django.contrib import messages
from django.contrib.auth.models import User
from apps.login.models import  Empresa



def createcompanies_admin(request):
    
    
    if request.method == 'POST':
        form = CompaniesForm(request.POST)
        if form.is_valid():

            Empresa.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                db_name=form.cleaned_data['db_name']
            )
                
            messages.success(request, 'La empresa Fue creada Correctamente')
            return redirect('admin:companies')
    else:
        form = CompaniesForm()
        empresas = Empresa.objects.all()
    return render(request, './admin/companies.html',{
        'form': form ,
        'empresas':empresas
        
        })