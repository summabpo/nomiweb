from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

def startemployees(request):
    return render(request, './base/base2.html')