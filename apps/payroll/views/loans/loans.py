import datetime
from django.shortcuts import render
import requests

from django.http import JsonResponse
from django.contrib import messages
from django.db.models import F, Q, Case, When, Value, CharField, Sum, Count
from django.db.models.functions import Concat
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse

#models
from apps.common.models import Prestamos

#
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

# view detail electronic payroll container
@login_required
@role_required('accountant', 'company')
def employee_loans(request):

    loans = Prestamos.objects.all()

    context = {
        'loans': loans
    }

    return render(request, 'payroll/employee_loans.html', context)