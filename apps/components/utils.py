from datetime import datetime

def calcular_dias_360(fechainicial, fechafinal):
    #Calcula la diferencia entre dos fechas considerando todos los meses con 30 dias.

    fechainicial = datetime.strptime(fechainicial, "%Y-%m-%d")
    fechafinal = datetime.strptime(fechafinal, "%Y-%m-%d")

    anios_diferencia = fechafinal.year - fechainicial.year
    meses_diferencia = fechafinal.month - fechainicial.month
    dias_diferencia = fechafinal.day - fechainicial.day

    dias_totales_360 = (anios_diferencia * 360) + (meses_diferencia * 30) + dias_diferencia

    return dias_totales_360