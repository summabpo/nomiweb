from django.shortcuts import render, redirect, get_object_or_404
from apps.components.decorators import custom_login_required ,custom_permission


@custom_login_required
@custom_permission('employees')
def index_employees(request):
    return render(request, './employees/index.html')
    





