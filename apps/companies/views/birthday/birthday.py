from django.views import View
from django.shortcuts import render
from apps.companies.models import Contratosemp
from django.http import JsonResponse
from datetime import datetime

class BirthdayView(View):
    def get(self, request):
        fecha_actual = datetime.now().date()
        cumpleanieros = Contratosemp.objects.filter(fechanac__month=fecha_actual.month)
        return render(request, './companies/birthday.html', {'cumpleanieros': cumpleanieros})

    def post(self, request):
        eventos = Contratosemp.objects.filter(fechanac__month=request.POST.get('month'))
        eventos_data = [{
            'title': evento.pnombre + ' ' + evento.papellido,
            'start': evento.fechanac.isoformat(),
        } for evento in eventos]
        return JsonResponse(eventos_data, safe=False)
