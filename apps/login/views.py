from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login , logout
from django.contrib import messages
from .forms import LoginForm
from django.contrib.auth.models import User
from .funtion import authenticate_custom


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('companies:editcontracsearch')  
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    return render(request, './users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login:login')


def redirect_user(request):
    return redirect('login')

