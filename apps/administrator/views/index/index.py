from django.shortcuts import render,redirect
from apps.administrator.forms.createuserForm import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User

# Create your views here.

def index_admin(request):
    return render(request, './admin/index.html')