import re
from datetime import datetime, timedelta, date, time
import calendar

# --- 1. Define input string ---
input_string = """2025-09-22 04:00 13:00\nHoras Ordinarias: 1.0\nHED: 5\nHEN: 0\nHEDF: 0\nHENF: 0\nRN: 2\nRNF: 0\nDYF: 0"""

# --- 2. Parse input string ---
# Extract date, start_time, and end_time from the first line
first_line = input_string.split('\n')[0]
date_match = re.match(r'(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) (\d{2}:\d{2})', first_line)

if date_match:
    work_date_str = date_match.group(1)
    start_time_str = date_match.group(2)
    end_time_str = date_match.group(3)

    work_date = datetime.strptime(work_date_str, '%Y-%m-%d').date()
    start_time = datetime.strptime(start_time_str, '%H:%M').time()
    end_time = datetime.strptime(end_time_str, '%H:%M').time()
else:
    print("Could not parse date and times from input string.")
    exit()

# Initialize reported hour types dictionary
hour_types = {
    'Horas Ordinarias': None,
    'HED': None,
    'HEN': None,
    'HEDF': None,
    'HENF': None,
    'RN': None,
    'RNF': None,
    'DYF': None
}

# Extract reported hour values robustly
for line in input_string.split('\n')[1:]:
    match = re.match(r'([a-zA-Z\s]+): (\d+\.?\d*)', line)
    if match:
        key_found = match.group(1).strip()
        value_found = float(match.group(2))
        if key_found in hour_types:
            hour_types[key_found] = value_found

print("Input parsing complete.")

# --- 3. Define Colombian labor rules ---
# Define day and night shift times (Colombian labor law)
day_start = time(6, 0)  # 6:00 AM
day_end = time(18, 0)   # 6:00 PM (Adjusted as per instruction: night shift starts at 6 PM)
night_start = time(18, 0) # 6:00 PM
night_end = time(6, 0)    # 6:00 AM (of the next day)

# Define percentage surcharges (Colombian labor law)
surcharge_hed = 0.25  # Hourly Extra Day (Hora Extra Diurna)
surcharge_hen = 0.75  # Hourly Extra Night (Hora Extra Nocturna)
surcharge_rn = 0.35   # Night Surcharge (Recargo Nocturno)
surcharge_hedf = 1.00 # Hourly Extra Day Festive (Hora Extra Diurna Festiva) - base 0.75 + extra 0.25
surcharge_henf = 1.50 # Hourly Extra Night Festive (Hora Extra Nocturna Festiva) - base 0.75 + extra 0.75
surcharge_rnhf = 0.75 # Night Surcharge Festive (Recargo Nocturno Festivo)
surcharge_hfd = 0.75  # Hourly Festive Day (Hora Festiva Diurna) - This is for ordinary hours worked on a holiday during the day
surcharge_hfn = 1.10  # Hourly Festive Night (Hora Festiva Nocturna) - This is for ordinary hours worked on a holiday during the night (0.75 + 0.35)

print("Colombian labor rules defined.")

# --- 4. Helper functions for holidays ---
def easter_sunday(year):
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)

def apply_ley_emiliani(holiday_date):
    if holiday_date.weekday() == calendar.MONDAY: # Monday is 0
        return holiday_date
    else:
        days_until_monday = (calendar.MONDAY - holiday_date.weekday() + 7) % 7
        return holiday_date + timedelta(days=days_until_monday)

def is_colombian_holiday(check_date):
    year = check_date.year

    fixed_holidays = [
        (1, 1),   # Año Nuevo
        (5, 1),   # Día del Trabajo
        (7, 20),  # Día de la Independencia
        (8, 7),   # Batalla de Boyacá
        (12, 8),  # Día de la Inmaculada Concepción
        (12, 25)  # Navidad
    ]

    for month, day in fixed_holidays:
        if check_date == date(year, month, day):
            return True

    easter = easter_sunday(year)

    movable_holidays = {
        'Epifanía': date(year, 1, 6), # 6 de enero (se traslada)
        'San José': date(year, 3, 19), # 19 de marzo (se traslada)
        'Jueves Santo': easter + timedelta(days=-3),
        'Viernes Santo': easter + timedelta(days=-2),
        'Ascensión de Jesús': easter + timedelta(days=43), # 40 días después de Pascua (se traslada)
        'Corpus Christi': easter + timedelta(days=64), # 60 días después de Pascua (se traslada)
        'Sagrado Corazón': easter + timedelta(days=71), # 68 días después de Pascua (se traslada)
        'San Pedro y San Pablo': date(year, 6, 29), # 29 de junio (se traslada)
        'Asunción de la Virgen': date(year, 8, 15), # 15 de agosto (se traslada)
        'Día de la Raza': date(year, 10, 12), # 12 de octubre (se traslada)
        'Todos los Santos': date(year, 11, 1), # 1 de noviembre (se traslada)
    }

    holidays_to_move = [
        'Epifanía', 'San José', 'Ascensión de Jesús', 'Corpus Christi',
        'Sagrado Corazón', 'San Pedro y San Pablo', 'Asunción de la Virgen',
        'Día de la Raza', 'Todos los Santos'
    ]

    for name, hol_date in movable_holidays.items():
        if name in holidays_to_move:
            if check_date == apply_ley_emiliani(hol_date):
                return True
        elif check_date == hol_date:
            return True

    return False

print("Holiday helper functions defined.")

# --- 5. Calculate Colombian hours function ---
def calculate_colombian_hours(work_date, start_time, end_time):
    start_dt = datetime.combine(work_date, start_time)
    end_dt = datetime.combine(work_date, end_time)

    if end_dt < start_dt:
        end_dt += timedelta(days=1) # Work extends into the next day

    # Apply 1 hour lunch break deduction
    # Only apply if the total shift duration is greater than 1 hour
    if (end_dt - start_dt).total_seconds() / 3600 > 1:
        end_dt_effective = end_dt - timedelta(hours=1)
    else:
        end_dt_effective = end_dt # No lunch break if shift is 1 hour or less

    is_holiday = is_colombian_holiday(work_date)
    is_sunday = (work_date.weekday() == 6) # Monday is 0, Sunday is 6
    is_festive = is_holiday or is_sunday

    calculated_hours = {
        'Horas Ordinarias': 0.0,
        'HED': 0.0, # Horas Extra Diurnas
        'HEN': 0.0, # Horas Extra Nocturnas
        'HEDF': 0.0, # Horas Extra Diurnas Festivas
        'HENF': 0.0, # Horas Extra Nocturnas Festivas
        'RN': 0.0,  # Recargo Nocturno (Ordinary Night Surcharge)
        'RNF': 0.0, # Recargo Nocturno Festivo (Ordinary Festive Night Surcharge)
        'DYF': 0.0 # Horas Diurnas y Festivas (Ordinary Festive Day Surcharge)
    }

    total_worked_minutes = 0
    current_dt = start_dt

    while current_dt < end_dt_effective:
        next_minute = current_dt + timedelta(minutes=1)

        # Determine if the current minute is day or night
        # Day: 6:00 to 18:00
        # Night: 18:00 to 6:00 (of next day if shift crosses midnight)
        current_minute_time = current_dt.time()
        is_day_hour = day_start <= current_minute_time < day_end
        is_night_hour = not is_day_hour # Any hour outside day_start to day_end is considered night

        # Check if it's an ordinary hour or an extra hour
        # Assuming an 8-hour ordinary workday (480 minutes)
        if total_worked_minutes < 8 * 60: # Within ordinary hours (first 8 hours)
            if is_festive:
                if is_day_hour:
                    calculated_hours['DYF'] += 1/60 # Ordinary Festive Day (Recargo Dominical/Festivo Diurno)
                elif is_night_hour:
                    calculated_hours['RNF'] += 1/60 # Ordinary Festive Night Surcharge (Recargo Nocturno Dominical/Festivo)
            else: # Not festive (weekday)
                if is_day_hour:
                    calculated_hours['Horas Ordinarias'] += 1/60 # Ordinary Day
                elif is_night_hour:
                    calculated_hours['RN'] += 1/60 # Ordinary Night Surcharge (Recargo Nocturno)
        else: # Beyond ordinary hours, it's extra time
            if is_festive:
                if is_day_hour:
                    calculated_hours['HEDF'] += 1/60 # Extra Festive Day
                elif is_night_hour:
                    calculated_hours['HENF'] += 1/60 # Extra Festive Night
            else: # Not festive (weekday)
                if is_day_hour:
                    calculated_hours['HED'] += 1/60 # Extra Day
                elif is_night_hour:
                    calculated_hours['HEN'] += 1/60 # Extra Night

        total_worked_minutes += 1
        current_dt = next_minute

    return calculated_hours

print("Hour calculation function defined.")

# --- 6. Call calculation and compare results ---
calculated_distribution = calculate_colombian_hours(work_date, start_time, end_time)

print("\n--- Reported Hours ---")
for key, value in hour_types.items():
    print(f"{key}: {value:.2f}")

print("\n--- Calculated Hour Distribution ---")
for key, value in calculated_distribution.items():
    print(f"{key}: {value:.2f}")

print("\n--- Discrepancies ---")
discrepancies = {}

for key in hour_types.keys():
    reported_value = hour_types.get(key, 0.0) # Get reported value, default to 0 if not found
    calculated_value = calculated_distribution.get(key, 0.0)

    # Handle slight floating point differences
    if abs(reported_value - calculated_value) > 0.01: # Threshold for discrepancy
        discrepancies[key] = {
            'reported': reported_value,
            'calculated': calculated_value,
            'difference': reported_value - calculated_value
        }

if discrepancies:
    print("Discrepancies found:")
    for key, values in discrepancies.items():
        print(f"  {key}: Reported={values['reported']:.2f}, Calculated={values['calculated']:.2f}, Difference={values['difference']:.2f}")
else:
    print("No significant discrepancies found.")
    
    
    
    
    
    
    
    
    
    
    

@login_required
@role_required('accountant')
def time_doc(request, id):
    usuario = request.session.get('usuario', {})
    idempresa = usuario.get('idempresa')

    tiempos = Tiempos.objects.filter(idnomina=id).select_related('idcontrato__idsede')

    inicio_horario = int(Conceptosfijos.objects.get(conceptofijo = "HORARIO NOCTURNO INICIO").valorfijo)
    fin_horario = int(Conceptosfijos.objects.get(conceptofijo = "HORARIO NOCTURNO FIN").valorfijo)
    
    print('---------------')
    print(fin_horario)
    print(inicio_horario)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Tiempo Marcados"

    headers = [
        'Idcontrato', 'Empleado', 'FechaIngreso', 'HoraIngreso', 'FechaSalida', 'HoraSalida',
        'HorasDescuentos', 'HorasTraba', 'HorasOrdi', 'Saldo', 'HorasDomFes',
        'Hed', 'Hen', 'Hedf', 'Henf', 'Rn', 'Rnf', 'Dyf', 'Sede'
    ]
    ws.append(headers)

    colors = ["FFF9C4", "C8E6C9", "BBDEFB", "FFCDD2", "D1C4E9"]
    total_fill = PatternFill(start_color="E0E0E0", end_color="E0E0E0", fill_type="solid")
    total_font = Font(bold=True)

    current_contract = None
    color_index = 0

    CO_HOLIDAYS = holidays.CO(years=2025)

    # Inicializar acumuladores
    acumulados = {
        'HorasTraba': 0,
        'HorasOrdi': 0,
        'HorasDomFes': 0,
        'Hed': 0,
        'Hen': 0,
        'Hedf': 0,
        'Henf': 0,
        'Rn': 0,
        'Rnf': 0,
        'Dyf': 0
    }

    def convertir_a_horas_decimal(hora_obj):
        if isinstance(hora_obj, time):
            return hora_obj.hour + hora_obj.minute / 60 + hora_obj.second / 3600
        elif isinstance(hora_obj, str):
            hora_obj = hora_obj.strip().lower().replace('.', '')
            hora_obj = hora_obj.replace('a m', 'am').replace('p m', 'pm')
            hora_24 = datetime.strptime(hora_obj, "%I:%M:%S %p").time()
            return hora_24.hour + hora_24.minute / 60 + hora_24.second / 3600
        else:
            return float(hora_obj or 0)

    def agregar_totales_contrato(contrato_id):
        """Agrega una fila con los totales acumulados del contrato actual."""
        if contrato_id is None:
            return
        total_row = [
            contrato_id,
            "TOTAL CONTRATO",
            "", "", "", "",
            "",
            acumulados['HorasTraba'],
            acumulados['HorasOrdi'],
            "",
            acumulados['HorasDomFes'],
            acumulados['Hed'], acumulados['Hen'], acumulados['Hedf'], acumulados['Henf'],
            acumulados['Rn'], acumulados['Rnf'], acumulados['Dyf'],
            "",
        ]
        ws.append(total_row)

        # Estilos
        for cell in ws[ws.max_row]:
            cell.fill = total_fill
            cell.font = total_font

        # Reiniciar acumuladores
        for k in acumulados.keys():
            acumulados[k] = 0

    # 🔁 Recorrer registros
    for registro in tiempos.order_by('idcontrato__idcontrato'):
        contrato_id = registro.idcontrato.idcontrato

        # Si cambia el contrato, agregamos totales del anterior
        if current_contract is not None and contrato_id != current_contract:
            agregar_totales_contrato(current_contract)

        # Cambiar color del bloque
        if contrato_id != current_contract:
            current_contract = contrato_id
            color_index = (color_index + 1) % len(colors)
            fill = PatternFill(start_color=colors[color_index],
                               end_color=colors[color_index],
                               fill_type="solid")

        horas_trabajadas = horas_ordinarias = 0
        hed = hen = hedf = henf = rn = rnf = dyf = horas_domfes = 0

        if registro.horaingreso and registro.horasalida:
            try:
                hora_ingreso = convertir_a_horas_decimal(registro.horaingreso)
                hora_salida = convertir_a_horas_decimal(registro.horasalida)
                hora_descuento = convertir_a_horas_decimal(registro.horasdescuentos) if registro.horasdescuentos else 0

                if hora_salida < hora_ingreso:
                    hora_salida += 24

                horas_trabajadas = round(hora_salida - hora_ingreso - hora_descuento, 2)

                fecha = registro.fechaingreso
                es_domingo = fecha.weekday() == 6
                es_festivo = fecha in CO_HOLIDAYS

                for h in range(int(hora_ingreso), int(hora_salida)):
                    hora_actual = (hora_ingreso + (h - hora_ingreso))
                    if fin_horario <= hora_actual < inicio_horario:
                        if es_domingo or es_festivo:
                            hedf += 1
                        elif h >= 8:
                            hed += 1
                    else:
                        if es_domingo or es_festivo:
                            henf += 1
                        elif h >= 8:
                            hen += 1

                    if hora_actual >= inicio_horario or hora_actual < fin_horario:
                        rn += 1
                        if es_domingo or es_festivo:
                            rnf += 1

                if es_domingo or es_festivo:
                    horas_domfes = horas_trabajadas
                    dyf = horas_domfes

            except Exception as e:
                print(f"Error calculando horas para contrato {contrato_id}: {e}")

        horas_ordinarias = horas_trabajadas - (hed + hen + hedf + henf + rn + rnf + dyf + horas_domfes)
        horas_ordinarias = max(horas_ordinarias, 0)
        # Acumular totales
        acumulados['HorasTraba'] += horas_trabajadas
        acumulados['HorasOrdi'] += horas_ordinarias
        acumulados['HorasDomFes'] += horas_domfes
        acumulados['Hed'] += hed
        acumulados['Hen'] += hen
        acumulados['Hedf'] += hedf
        acumulados['Henf'] += henf
        acumulados['Rn'] += rn
        acumulados['Rnf'] += rnf
        acumulados['Dyf'] += dyf

        # Agregar fila
        row = [
            contrato_id,
            getattr(registro.idcontrato, 'empleado', 'N/A'),
            registro.fechaingreso,
            registro.horaingreso,
            registro.fechasalida,
            registro.horasalida,
            registro.horasdescuentos,
            horas_trabajadas,
            horas_ordinarias,
            '0.0',
            horas_domfes,
            hed, hen, hedf, henf, rn, rnf, dyf,
            registro.idcontrato.idsede.nombresede if registro.idcontrato.idsede else "",
        ]

        
        ws.append(row)

        for cell in ws[ws.max_row]:
            cell.fill = fill

        ws.cell(row=ws.max_row, column=3).number_format = 'DD/MM/YYYY'
        ws.cell(row=ws.max_row, column=5).number_format = 'DD/MM/YYYY'
        
        # print(
        #     f"Fecha: {registro.fechaingreso} | "
        #     f"Ingreso: {registro.horaingreso} | Salida: {registro.horasalida} || "
        #     f"Horas trabajadas: {horas_trabajadas} | "
        #     f"Horas ordinarias: {horas_ordinarias} | "
        #     f"HED: {hed} | HEN: {hen} | HEDF: {hedf} | HENF: {henf} | "
        #     f"RN: {rn} | RNF: {rnf} | DYF: {dyf}"
        # )

    # 🔚 Totales del último contrato
    agregar_totales_contrato(current_contract)

    output = BytesIO()
    wb.save(output)
    
    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="Tiempo_Marcados.xlsx"'
    
    return response
    
    
    
    
    
    
    
    
    
 ---------- Función auxiliar para calcular extras ----------
    def calcular_horas_extras(tiempos_queryset):
        CO_HOLIDAYS = holidays.CO(years=ano_obj.ano)
        horas_por_contrato = {}

        inicio_horario = int(Conceptosfijos.objects.get(conceptofijo = "HORARIO NOCTURNO INICIO").valorfijo)
        fin_horario = int(Conceptosfijos.objects.get(conceptofijo = "HORARIO NOCTURNO FIN").valorfijo)
    
        
        conceptos = Conceptosfijos.objects.filter(
            conceptofijo__in=[
                'JORNADA MAXIMA MENSUAL',
                'HORA EXTRA DIURNA FACTOR',
                'HORA EXTRA NOCTURNA FACTOR',
                'HORA EXTRA DIURNA FESTIVA FACTOR',
                'HORA EXTRA NOCTURNA FESTIVA FACTOR',
                'RECARGO NOCTURNO FACTOR',
                'RECARGO DOMINICAL O FESTIVO FACTOR'
            ]
        ).values('conceptofijo', 'valorfijo')

        factores = {c['conceptofijo']: float(c['valorfijo']) for c in conceptos}

        jmm = factores.get('JORNADA MAXIMA MENSUAL', 220.0)  # ejemplo 220h/mes
        hed_factor  = factores.get('HORA EXTRA DIURNA FACTOR', 1.0)
        hen_factor  = factores.get('HORA EXTRA NOCTURNA FACTOR', 1.0)
        hedf_factor = factores.get('HORA EXTRA DIURNA FESTIVA FACTOR', 1.0)
        henf_factor = factores.get('HORA EXTRA NOCTURNA FESTIVA FACTOR', 1.0)
        rn_factor   = factores.get('RECARGO NOCTURNO FACTOR', 1.0)
        rdf_factor  = factores.get('RECARGO DOMINICAL O FESTIVO FACTOR', 1.0)

        # mapa (contrato, fecha) -> horas usadas como normales (para contar 8h diarias)
        daily_regular = {}

        for t in tiempos_queryset:
            id_contrato = t.get('idcontrato_id')
            salario = Contratos.objects.get(idcontrato=id_contrato).salario

            fecha_ing = parse_date_obj(t.get('fechaingreso')) or parse_date_obj(t.get('fechasalida'))
            hora_ingreso = parse_time_obj(t.get('horaingreso'))
            hora_salida = parse_time_obj(t.get('horasalida'))
            horas_descuentos = horasdescuento_to_timedelta(t.get('horasdescuentos'))

            if not (hora_ingreso and hora_salida and fecha_ing):
                continue

            dt_ingreso = datetime.combine(fecha_ing, hora_ingreso)
            dt_salida = datetime.combine(fecha_ing, hora_salida)
            if dt_salida < dt_ingreso:
                dt_salida += timedelta(days=1)

            dt_salida_adj = dt_salida - horas_descuentos
            if dt_salida_adj < dt_ingreso:
                dt_salida_adj = dt_ingreso

            worked = dt_salida_adj - dt_ingreso
            if worked < timedelta():
                worked = timedelta()

            total_hours = round(worked.total_seconds() / 3600, 2)

            # Inicializar contadores por registro
            normales_diurnas = normales_nocturnas = 0.0     # normales dentro de la jornada
            normales_diurnas_festiva = normales_nocturnas_festiva = 0.0  # normales en festivo/dominical
            hed = hen = hedf = henf = 0.0  # extras
            # base de jornada diaria (8h típicas); si tienes variable por contrato, reemplazar aquí
            base_hours = 8.0

            hora_actual = dt_ingreso
            end_time = dt_salida
            step = timedelta(minutes=1)  # precisión por minuto
            slice_date = hora_actual.date()
            
            if slice_date == date(2025, 10, 2):
                print(f" in : {dt_ingreso} out {end_time}")
                print(f" H1 {time(fin_horario, 0)} H2 {time(inicio_horario, 0)}")
                print('-----------------')
                
            while hora_actual < end_time:
                siguiente = min(hora_actual + step, end_time)
                dur = (siguiente - hora_actual).total_seconds() / 3600.0
                
                is_domingo = slice_date.weekday() == 6
                is_festivo = slice_date in CO_HOLIDAYS
                is_festivo_o_dominio = is_festivo or is_domingo
                is_nocturna = not (time(fin_horario, 0) <= hora_actual.time() < time(inicio_horario, 0))
                
                
                
                if slice_date == date(2025, 10, 2):
                    print(f" I : {hora_actual}  d : {is_domingo} f : {is_festivo}  f_d : {is_festivo_o_dominio} n : {is_nocturna}")
                
                key_day = (id_contrato, slice_date)
                used_regular = daily_regular.get(key_day, 0.0)
                remaining_regular = max(0.0, base_hours - used_regular)

                if is_festivo_o_dominio:
                    # Festivo / dominical: diferenciamos si queda dentro de la jornada normal o ya es extra
                    if remaining_regular > 0:
                        alloc_regular = min(dur, remaining_regular)
                        # asignar a normales festivas (diurna/nocturna)
                        if is_nocturna:
                            normales_nocturnas_festiva += alloc_regular
                        else:
                            normales_diurnas_festiva += alloc_regular
                        daily_regular[key_day] = used_regular + alloc_regular

                        rest = dur - alloc_regular
                        if rest > 0:
                            # el resto son horas extra festivas
                            if is_nocturna:
                                henf += rest
                            else:
                                hedf += rest
                    else:
                        # todo el trozo es extra festiva
                        if is_nocturna:
                            henf += dur
                        else:
                            hedf += dur
                else:
                    # Día normal (no festivo)
                    if remaining_regular > 0:
                        alloc_regular = min(dur, remaining_regular)
                        if is_nocturna:
                            normales_nocturnas += alloc_regular
                        else:
                            normales_diurnas += alloc_regular
                        daily_regular[key_day] = used_regular + alloc_regular

                        rest = dur - alloc_regular
                        if rest > 0:
                            # resto son horas extra (nocturna o diurna)
                            if is_nocturna:
                                hen += rest
                            else:
                                hed += rest
                    else:
                        # todo el trozo es extra en día normal
                        if is_nocturna:
                            hen += dur
                        else:
                            hed += dur

                hora_actual = siguiente

            # Inicializar acumuladores por contrato si falta
            if id_contrato not in horas_por_contrato:
                horas_por_contrato[id_contrato] = {
                    'salario': salario,
                    'horas_normales': 1.0,
                    'horas_trabajadas': 0.0,
                    'normales_diurnas': 0.0,
                    'normales_nocturnas': 0.0,
                    'normales_diurnas_festiva': 0.0,
                    'normales_nocturnas_festiva': 0.0,
                    'hed': 0.0,
                    'hen': 0.0,
                    'hedf': 0.0,
                    'henf': 0.0,
                }

            acc = horas_por_contrato[id_contrato]
            acc['horas_trabajadas'] += total_hours
            acc['normales_diurnas'] += normales_diurnas
            acc['normales_nocturnas'] += normales_nocturnas
            acc['normales_diurnas_festiva'] += normales_diurnas_festiva
            acc['normales_nocturnas_festiva'] += normales_nocturnas_festiva
            acc['hed'] += hed
            acc['hen'] += hen
            acc['hedf'] += hedf
            acc['henf'] += henf
        
            acc['horas_normales'] += henf

        # Calcular valores (NOTA: la interpretación de los "factores" puede variar — abajo comento cómo adaptarlo)
        for contrato_id, valores in horas_por_contrato.items():
            salario = valores['salario']
            valor_hora = salario / jmm  # jmm: jornada maxima mensual (horas mensuales)

            # horas festivas normales totales (dentro de la jornada)
            normales_festivas = valores['normales_diurnas_festiva'] + valores['normales_nocturnas_festiva']

            # Si tus factores son multiplicadores totales (ej. recargo nocturno = 1.35),
            # y quieres calcular el VALOR ADICIONAL a pagar (no el pago total por la hora),
            # entonces usa (factor - 1). Si en tu DB tienes directamente el % (ej. 0.35),
            # usa simplemente factor * valor_hora * horas.
            #
            # Aquí asumo que los factores en la BD representan multiplicadores TOTALES
            # (ej. HORA EXTRA DIURNA FACTOR = 1.25). Para sacar la parte adicional:
            def extra_amount(hours, factor):
                return hours * valor_hora * factor 
                

            Vhed  = round(extra_amount(valores['hed'], hed_factor), 1)
            Vhen  = round(extra_amount(valores['hen'], hen_factor), 1)
            Vhedf = round(extra_amount(valores['hedf'], hedf_factor), 1)
            Vhenf = round(extra_amount(valores['henf'], henf_factor), 1)
            # recargo nocturno: normalmente aplica sobre horas nocturnas dentro de la jornada (normales_nocturnas)
            Vrn = round(extra_amount(valores['normales_nocturnas'], rn_factor), 1)
            # recargo dominical/festivo para horas normales en ese día
            Vdyf = round(extra_amount(normales_festivas, rdf_factor), 1)

            valores['Vhed']  = Vhed
            valores['Vhen']  = Vhen
            valores['Vhedf'] = Vhedf
            valores['Vhenf'] = Vhenf
            valores['Vrn']   = Vrn
            valores['Vdyf']  = Vdyf

            valores['dyf'] = round(normales_festivas, 1)

            valores['ValorExtras'] = round(Vhed + Vhen + Vhedf + Vhenf + Vrn + Vdyf, 1)

            # redondear todas las horas/valores
            for k, v in list(valores.items()):
                if isinstance(v, (int, float)):
                    valores[k] = round(v, 1)

        return horas_por_contrato


