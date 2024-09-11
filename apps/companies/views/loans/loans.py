from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.filterform import FilterForm 
from apps.components.decorators import  role_required
from apps.companies.models import Prestamos
from apps.companies.forms.loansForm import LoansForm



def loans(request):
    prestamos = Prestamos.objects.all()
    form = LoansForm()
    
    
    return render (request, './companies/loans.html',
                    {
                      'prestamos' :prestamos,  
                      'form' :form,
                    })