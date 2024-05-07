from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Tipodocumento , Paises , Ciudades , Contratosemp , Contratos
from apps.companies.forms.EmployeeForm import EmployeeForm
from django.contrib import messages
from apps.login.middlewares import NombreDBSingleton
from apps.components.decorators import custom_login_required ,custom_permission


@custom_login_required
@custom_permission('entrepreneur')
def index_companies(request):
    contactos = Contratosemp.objects.all()
    return render(request, './companies/index.html',{'comn':contactos})
    





