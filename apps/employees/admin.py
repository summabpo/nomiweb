from django.contrib import admin

# Register your models here.
def genera_comprobante(request, idnomina, idcontrato):
        idc=idcontrato
        idn=idnomina
        idempleado_id = Contratos.objects.get(idcontrato=idc).idempleado_id
        ide=idempleado_id

        
        #data to print

        dataDevengado = Nomina.objects.filter(idcontrato=idc, idnomina=idn, valor__gt=0).order_by('idconcepto')
        dataDescuento = Nomina.objects.filter(idcontrato=idc, idnomina=idn, valor__lt=0).order_by('idconcepto')
        

        for obj in dataDevengado:
            p.setFont("Courier",9,leading=None)
            p.drawRightString(x1,y1-12,f"{obj.idconcepto}")
            p.drawString(x1 + 10,y1-12,f"{obj.nombreconcepto}")
            p.drawRightString(x1 + 177,y1-12,f"{obj.cantidad}")
            valor_formateado = locale.format_string("%0.0f", obj.valor, grouping=True, monetary=True)
            p.drawRightString(x1 + 244,y1-12,f"{valor_formateado}")
            y1 = y1 - 10
        y1 = 437
        for obj in dataDescuento:
            p.setFont("Courier",9,leading=None)
            p.drawRightString(x1 + 270,y1-12,f"{obj.idconcepto}")
            p.drawString(x1 + 280,y1-12,f"{obj.nombreconcepto}")
            p.drawRightString(x1 + 445,y1-12,f"{obj.cantidad}")
            valor_formateado = locale.format_string("%0.0f", obj.valor, grouping=True, monetary=True)
            p.drawRightString(x1 + 510,y1-12,f"{valor_formateado}")
            y1 = y1 - 10

        totalDevengados = Nomina.objects.filter(idcontrato=idc, idnomina=idn, valor__gt=0).aggregate(totalDevengados=Sum('valor'))['totalDevengados']
        devengadosFormateado=locale.format_string("%0.0f", totalDevengados, grouping=True, monetary=True)
        totalDescuentos = Nomina.objects.filter(idcontrato=idc,idnomina=idn, valor__lt=0).aggregate(totalDescuentos=Sum('valor'))['totalDescuentos']
        descuentosFormateado = locale.format_string("%0.0f", totalDescuentos, grouping=True, monetary=True)
        netoaPagar = Nomina.objects.filter(idcontrato=idc,idnomina=idn).aggregate(netoaPagar=Sum('valor'))['netoaPagar']
        netoFormateado = locale.format_string("%0.0f", netoaPagar, grouping=True, monetary=True)

        p.setFont("Courier",14,leading=None)
        p.drawRightString(300, 163,f"{devengadosFormateado}")
        p.drawRightString(580, 163,f"{descuentosFormateado}")
        p.drawRightString(480, 123,f"{netoFormateado}")

        p.setTitle(f'Report on {d}')
        p.showPage()
        p.save()
        
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)

        
        return response
    