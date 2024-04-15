from django.shortcuts import render, redirect, get_object_or_404
from .forms import EmployeeForm


def newEmployee(request):
    
    return render(request, './companies/NewEmployee.html')
